import os
import json
from time import sleep
import requests
import subprocess
from uuid import uuid4
from enum import Enum
from typing import Dict, Any

from cogniceptshell.common import bcolors, get_user_confirmation


class LogType(Enum):
    INFO = bcolors.OKBLUE
    SUCCESS = bcolors.OKGREEN
    WARNING = bcolors.WARNING
    ERROR = bcolors.FAIL


class RobotAPIRegistrar:
    def __init__(self):
        from cogniceptshell.configuration import Configuration

        self.agent_client_id = ""
        self.agent_client_secret = ""
        self.device_service_url = ""
        self.auth_service_url = ""
        self.config: Configuration = None

    def log(self, message: str, level: LogType) -> None:
        """Centralized logging method with color coding."""
        print(f"{level.value}{message}{bcolors.ENDC}")

    def validate_config_url(self, url_name: str, url_value: str) -> None:
        """Validate configuration URL existence."""
        if url_value is None:
            self.log(
                f"{url_name} is not set in the configuration file",
                LogType.ERROR,
            )
            raise SystemExit(1)

    def register_device(self, args) -> None:
        """Main method to handle device registration process."""
        self.load_config_values(args)

        # Step 1: Install Tailscale if not installed
        self.install_tailscale()

        # Step 2: Generate auth token
        token = self.get_auth_token()

        # Step 3: Register device with device service API
        device_info = self.register_with_device_service(token)

        # Step 4: Connect to Tailscale using the provided key
        self.connect_to_tailscale(device_info["tailscale_key"]["key"])

        # Step 5: Get Tailscale device information
        tailscale_info = self.get_tailscale_info()

        # Step 6: Update device information in device service
        self.update_device_info(
            device_info["device"]["id"], tailscale_info, token
        )

        # Step 7: Store device details in runtime.env
        self.store_credentials(device_info["device"]["id"], args)

        self.log(
            "Robot API device registration completed successfully",
            LogType.SUCCESS,
        )

    def load_config_values(self, args) -> None:
        """Load and validate configuration values."""
        self.config = args.config
        self.agent_client_id = (
            f"agent-client-{self.config.get_config('ROBOT_CODE')}"
        )
        self.agent_client_secret = args.api

        self.auth_service_url = self.config.get_config("AUTH_SERVICE_URL")
        self.device_service_url = self.config.get_config("DEVICE_SERVICE_URL")

        self.validate_config_url("AUTH_SERVICE_URL", self.auth_service_url)
        self.validate_config_url("DEVICE_SERVICE_URL", self.device_service_url)

    def check_curl_installation(self) -> None:
        """Check if curl is installed."""
        if (
            subprocess.run(["which", "curl"], capture_output=True).returncode
            != 0
        ):
            self.log(
                "Curl is needed for tailscale installation. "
                "Please install curl and try again",
                LogType.WARNING,
            )
            raise SystemExit(1)

    def install_tailscale(self) -> None:
        """Install Tailscale if not present."""
        try:
            subprocess.run(
                "tailscale version",
                shell=True,
                check=True,
                capture_output=True,
            )
            return
        except subprocess.CalledProcessError:
            self.log("Tailscale not found", LogType.WARNING)

        # Get user confirmation before proceeding with installation
        confirm_message = (
            "Tailscale installation is required for device registration.\n"
            "This will:\n"
            "1. Download the Tailscale installation script\n"
            "2. Install Tailscale on your system using sudo privileges\n"
            "3. Create necessary network configurations"
        )

        if not get_user_confirmation(confirm_message):
            self.log(
                "Tailscale installation cancelled. "
                "Device registration cannot proceed.",
                LogType.ERROR,
            )
            raise SystemExit(1)

        self.log("Installing Tailscale...", LogType.INFO)

        try:
            self.check_curl_installation()
            subprocess.run(
                "curl -fsSL https://tailscale.com/install.sh | sh",
                shell=True,
                check=True,
            )
            sleep(3)  # Allow tailscale to stabilize
        except subprocess.CalledProcessError:
            self.log("Tailscale installation failed", LogType.ERROR)
            raise SystemExit(1)

    def get_auth_token(self) -> str:
        """Obtain authentication token."""
        data = {
            "client_id": self.agent_client_id,
            "client_secret": self.agent_client_secret,
            "grant_type": "client_credentials",
        }
        response = requests.post(
            f"{self.auth_service_url}/realms/smart_plus/protocol"
            "/openid-connect/token",
            data=data,
        )

        if response.status_code != 200:
            self.log(
                "Error occurred while authenticating with auth service",
                LogType.ERROR,
            )
            raise SystemExit(1)

        return response.json().get("access_token", None)

    def register_with_device_service(self, token: str) -> Dict[str, Any]:
        """Register device with device service."""
        self.log("Registering device with Robot API...", LogType.INFO)

        headers = {"Authorization": f"Bearer {token}"}
        smart_device_id = self.config.get_config("ROBOT_CODE")
        device_data = {
            "device_type": "ROBOT",
            "team_id": str(uuid4()),  # Read team_id from config file later
            "krapi_version": "1.0",  # TODO: fetch correct krapi version
        }

        response = requests.put(
            f"{self.device_service_url}/devices/register/{smart_device_id}",
            headers=headers,
            json=device_data,
        )

        if response.status_code != 200:
            self.log(
                "Error occurred while registering device with Robot API",
                LogType.ERROR,
            )
            raise SystemExit(1)

        self.log("Device registered with Robot API", LogType.SUCCESS)
        return response.json().get("data", None)

    def connect_to_tailscale(self, tailscale_key: str) -> None:
        """Connect device to Tailscale network."""
        self.log("Connecting device to Tailscale...", LogType.INFO)

        robot_key = self.config.get_config("ROBOT_KEY")
        if not robot_key:
            self.log(
                "ROBOT_KEY not found, using system nodename as tailscale host",
                LogType.WARNING,
            )
        hostname = (
            robot_key.replace("_", "-") if robot_key else os.uname().nodename
        )

        try:
            subprocess.run(
                [
                    "sudo",
                    "tailscale",
                    "up",
                    "--authkey",
                    tailscale_key,
                    "--hostname",
                    hostname,
                    "--reset",
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            self.log("Connection to Tailscale failed", LogType.ERROR)
            raise SystemExit(1)

        self.log("Device connected to Tailscale successfully", LogType.SUCCESS)

    def get_tailscale_info(self) -> Dict[str, str]:
        """Retrieve Tailscale device information."""
        try:
            result = subprocess.run(
                ["tailscale", "status", "--json"],
                capture_output=True,
                text=True,
                check=True,
            )
            tailscale_status = json.loads(result.stdout)
        except Exception:
            self.log(
                "Error occurred while fetching tailscale details",
                LogType.ERROR,
            )
            raise SystemExit(1)

        device_details = tailscale_status["Self"]

        return {
            "tailscale_ip": device_details["TailscaleIPs"][0],
            "tailscale_host": device_details["HostName"],
            "tailscale_device_id": device_details["ID"],
        }

    def update_device_info(
        self, device_id: str, tailscale_info: Dict[str, str], token: str
    ) -> None:
        """Update device information in KCRAPI service."""
        self.log("Updating device details...", LogType.INFO)

        headers = {"Authorization": f"Bearer {token}"}
        update_data = {
            "tailscale_ip": tailscale_info["tailscale_ip"],
            "tailscale_host": tailscale_info["tailscale_host"],
            "tailscale_device_id": tailscale_info["tailscale_device_id"],
            "krapi_version": "1.0",
        }

        try:
            requests.put(
                f"{self.device_service_url}/devices/{device_id}",
                headers=headers,
                json=update_data,
            )
        except Exception:
            self.log(
                "Error occurred while updating device details", LogType.ERROR
            )
            return

        self.log("Device details updated successfully", LogType.INFO)

    def store_credentials(self, device_id: str, args) -> None:
        """Store device credentials in configuration file."""
        self.config.add_config("ROBOT_API_DEVICE_ID", device_id)
        self.config.add_config("ROBOT_API_CLIENT_ID", self.agent_client_id)
        self.config.add_config(
            "ROBOT_API_CLIENT_SECRET", self.agent_client_secret
        )
        self.config.save_config(args)
