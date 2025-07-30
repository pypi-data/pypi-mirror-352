from atexit import register
from os import environ
from subprocess import Popen, run
from time import sleep, time

from requests import HTTPError, RequestException, get, post
from retry import retry

from ...models.bitwarden import Attachment, BitWardenItem, VaultItem
from ...models.bitwarden.exceptions import VaultError, VaultItemError, VaultItemNotFoundError
from ...utils.core import BW_PORT, singleton
from ...utils.core.download_bitwarden import get_bw_path, install_bitwarden, is_bitwarden_installed
from ...utils.services import logger


@singleton
class Bitwarden:
    """Bitwarden class."""

    def __init__(self):
        """Initialize the Bitwarden class."""
        if is_bitwarden_installed():
            self.bw_path = get_bw_path()
        else:
            self.bw_path = install_bitwarden()
        self.bw_url = f"http://localhost:{BW_PORT}"
        self.vault_items: dict[str, VaultItem] = {}
        self.bw_process: Popen | None = None
        register(self.cleanup)

        self.os_env = environ.copy()
        self.password = ""

    def cleanup(self):
        """Clean up resources by terminating the Bitwarden process if it is running."""
        try:
            if hasattr(self, "bw_process") and self.bw_process is not None:
                self.bw_process.terminate()
                self.bw_process.wait(timeout=5)  # Ensure the process terminates
                self.bw_process = None
        except Exception as e:
            logger.warning(f"Exception during cleanup: {e}")

    def __logout(self) -> None:
        """Logs out the user from the vault by terminating the Bitwarden process and executing the logout command."""
        self.cleanup()

        run(
            [
                self.bw_path,
                "logout",
            ],
            capture_output=True,
            input=None,
            text=True,
            timeout=180,
            env=self.os_env,
        )

    def _wait_for_server(self, timeout: int = 30, interval: float = 0.5):
        logger.info("Waiting for Bitwarden server to start")
        start_time = time()
        while time() - start_time < timeout:
            try:
                response = get(f"{self.bw_url}/status", timeout=1)
                if response.ok:
                    return
            except RequestException:
                pass
            sleep(interval)

        raise VaultError("Bitwarden server failed to start within timeout period")

    @retry(tries=3, delay=5, logger=logger)
    def login_from_env(self, force_latest: bool = False):
        """Login to the vault using environment variables.

        Args:
            force_latest (bool, optional): If True, download the latest version of the Bitwarden CLI. Defaults to False.

        Environment variables required:
        - BW_CLIENTID
        - BW_CLIENTSECRET
        - BW_PASSWORD
        """
        if force_latest:
            logger.info("Downloading the latest Bitwarden binary.")
            self.cleanup()
            install_bitwarden(force_latest)

        logger.info("Login in to Bitwarden.")

        self.__logout()

        MANDATORY_ENV_VARS = [
            "BW_CLIENTID",
            "BW_CLIENTSECRET",
            "BW_PASSWORD",
        ]

        missing_vars = [key for key in MANDATORY_ENV_VARS if key not in self.os_env]

        if missing_vars:
            raise VaultError(f"Environment variable(s) not set: {', '.join(missing_vars)}")

        process = run(
            [self.bw_path, "login", "--apikey"],
            capture_output=True,
            input=None,
            text=True,
            timeout=30,
            env=self.os_env,
        )

        if process.returncode != 0:
            raise VaultError(f"Failed to login: {process.stderr}")

        self.password = self.os_env["BW_PASSWORD"]

        self.open_bw_server()
        self._wait_for_server()
        self.unlock()
        self._load_all_items()

        if not self.is_vault_unlocked:
            raise VaultError("Failed to unlock the vault. Is the password correct?")

        if not self.vault_items:
            logger.warning("No items found in the vault. Re-downloading the binary...")
            self.cleanup()
            install_bitwarden(force_latest)
            raise VaultError("Failed to initialize the vault: No items found.")

    def login(self, client_id: str, client_secret: str, password: str, username: str = "", force_latest: bool = False):
        """Sets the client ID, client secret, and password in the environment variables and initiates the login process.

        Args:
            client_id (str): The client ID for authentication.
            client_secret (str): The client secret for authentication.
            password (str): The user's mater password for authentication.
            username (str): The username for authentication.
            force_latest (bool, optional): If True, download the latest version of the Bitwarden CLI. Defaults to False.
        """
        self.os_env["BW_CLIENTID"] = client_id
        self.os_env["BW_CLIENTSECRET"] = client_secret
        self.os_env["BW_PASSWORD"] = password
        self.os_env["BW_USERNAME"] = username
        self.login_from_env(force_latest=force_latest)

    def open_bw_server(self):
        """Open the Bitwarden server."""
        self.bw_process = Popen(
            [
                self.bw_path,
                "serve",
                "--port",
                str(BW_PORT),
            ],
            env=self.os_env,
        )

    @retry(tries=5, delay=5)
    def unlock(self):
        """Unlock the vault."""
        r = post(
            f"{self.bw_url}/unlock",
            json={"password": self.password},
            timeout=5,
        )
        if not r.ok or r.json().get("success") is not True:
            raise VaultError("Failed to unlock vault.")

    def __create_vault_item(self, data) -> VaultItem:
        """Create a vault item."""
        item = BitWardenItem()
        item.name = data.get("name")
        item.totp_key = data.get("login", {}).get("totp")
        item.fields = {item.get("name"): item.get("value") for item in data.get("fields", {}) if item.get("name")}
        if uris := data.get("login", {}).get("uris", [{}]):
            item.url_list = [item.get("uri") for item in uris if item.get("uri")]
        item.url = item.url_list[0] if item.url_list else None
        item.username = data.get("login", {}).get("username")
        item.password = data.get("login", {}).get("password")
        item.attachments = [
            Attachment(name=item.get("fileName"), item_id=item.get("id"), url=item.get("url"))
            for item in data.get("attachments", [])
            if item.get("fileName")
        ]
        item.collection_id_list = data.get("collectionIds")
        item.item_id = data.get("id")
        item.folder_id = data.get("folderId")
        item.notes = data.get("notes")

        return item

    def _load_all_items(self):
        """Get all items from the vault."""
        logger.info("Loading items from the vault.")
        try:
            r = self._load_all_items_request()
        except RequestException:
            logger.warning("Failed to retrieve all items, the library will get items individually")
            return
        if not r.ok:
            raise VaultError("Failed to retrieve items.")

        for item in r.json().get("data").get("data"):
            if not item.get("name"):
                continue
            self.vault_items[item.get("name")] = self.__create_vault_item(item)

    @retry((ConnectionError, HTTPError), tries=7, delay=1, backoff=1)
    def _load_all_items_request(self):
        return get(f"{self.bw_url}/list/object/items", timeout=60)

    @retry(exceptions=(RequestException,), tries=3, delay=1)
    def get_item(self, item_name: str) -> VaultItem:
        """Get a vault item by name.

        Args:
            item_name: The name of the item to retrieve.

        Returns:
            VaultItem: The vault item.
        """
        if item := self.vault_items.get(item_name):
            return item
        r = get(f"{self.bw_url}/list/object/items", params={"search": item_name}, timeout=30)
        if not r.ok:
            raise VaultItemNotFoundError(f"Failed to retrieve item {item_name}.")
        if not (data := r.json().get("data").get("data")):
            raise VaultItemNotFoundError(f"Item {item_name} not found.")
        if len(data) > 1:
            raise VaultItemError(f"Multiple items with name {item_name} found.")
        self.vault_items[item_name] = self.__create_vault_item(data[0])

        return self.vault_items[item_name]

    def get_attachment(self, item_name: str, attachment_name: str, file_path: str | None = None) -> str:
        """Get an attachment by name.

        Args:
            item_name: The name of the item to retrieve.
            attachment_name: The attachment to retrieve.
            file_path: The path to save the attachment to.

        Returns:
            str: The path to the downloaded attachment.
        """
        return self.get_item(item_name).get_attachment(attachment_name, file_path)

    def update_password(self, item_name: str, password: str | None = None) -> str:
        """Update the password of the vault item.

        Args:
            item_name: The name of the item to retrieve.
            password: The new password. If None, a new password will be generated.

        Returns:
            str: The new password.
        """
        return self.get_item(item_name).update_password(password)

    def update_custom_fields(self, item_name: str, fields: dict) -> dict:
        """Update the custom fields of the vault item.

        Args:
            item_name: The name of the item to retrieve.
            fields: The new custom fields.

        Returns:
            dict: The new custom fields.
        """
        return self.get_item(item_name).update_custom_fields(fields)

    @property
    def is_vault_unlocked(self) -> bool:
        """Check if the vault is unlocked."""
        if self.bw_process is None:
            return False
        serve_status = get(f"{self.bw_url}/status", timeout=5)
        if not serve_status.ok:
            return False

        return serve_status.json().get("data").get("template").get("status") == "unlocked"

    def __del__(self):
        """Cleans up resources by logging out and terminating the Bitwarden process if it is running."""
        self.cleanup()
