from unittest import mock
import pytest
from unittest.mock import Mock, patch, call
import subprocess
import json


from cogniceptshell.robot_api_registrar import RobotAPIRegistrar


class MockConfiguration:
    def __init__(self, config_values=None):
        self.config_values = config_values or {}

    def get_config(self, key):
        return self.config_values.get(key)

    def add_config(self, key, value):
        self.config_values[key] = value

    def save_config(self, args):
        pass


class MockArgs:
    def __init__(self, client_id="test_id", client_secret="test_secret"):
        self.api = client_secret
        self.config = MockConfiguration(
            {
                "AUTH_SERVICE_URL": "http://keycloak.test",
                "DEVICE_SERVICE_URL": "http://device.test",
                "ROBOT_CODE": "TEST123",
                "ROBOT_KEY": "test-robot",
            }
        )


@pytest.fixture
def registrar():
    return RobotAPIRegistrar()


@pytest.fixture
def mock_args():
    return MockArgs()


def test_init(registrar):
    assert registrar.agent_client_id == ""
    assert registrar.agent_client_secret == ""
    assert registrar.device_service_url == ""
    assert registrar.auth_service_url == ""
    assert registrar.config is None


def test_load_config_values_success(registrar, mock_args):
    registrar.load_config_values(mock_args)
    assert registrar.agent_client_id == "agent-client-TEST123"
    assert registrar.agent_client_secret == "test_secret"
    assert registrar.auth_service_url == "http://keycloak.test"
    assert registrar.device_service_url == "http://device.test"


def test_load_config_values_missing_keycloak_url(registrar):
    args = MockArgs()
    args.config = MockConfiguration(
        {"DEVICE_SERVICE_URL": "http://device.test"}
    )

    with pytest.raises(SystemExit):
        registrar.load_config_values(args)


def test_load_config_values_missing_device_url(registrar):
    args = MockArgs()
    args.config = MockConfiguration(
        {"AUTH_SERVICE_URL": "http://keycloak.test"}
    )

    with pytest.raises(SystemExit):
        registrar.load_config_values(args)


@patch("subprocess.run")
def test_install_tailscale_already_installed(mock_run, registrar):
    mock_run.return_value = Mock(returncode=0)
    registrar.install_tailscale()
    mock_run.assert_called_once_with(
        "tailscale version", shell=True, check=True, capture_output=True
    )


@patch("cogniceptshell.robot_api_registrar.get_user_confirmation")
@patch("subprocess.run")
def test_install_tailscale_with_confirmation_yes(
    mock_run, mock_user_confirmation, registrar
):
    # First call raises CalledProcessError (tailscale not found)
    mock_run.side_effect = [
        subprocess.CalledProcessError(1, "tailscale version"),
        Mock(returncode=0),  # curl check succeeds
        Mock(returncode=0),  # installation succeeds
    ]

    mock_user_confirmation.return_value = True

    registrar.install_tailscale()

    assert mock_run.call_count == 3
    mock_user_confirmation.assert_called_once()
    mock_run.assert_has_calls(
        [
            call(
                "tailscale version",
                shell=True,
                check=True,
                capture_output=True,
            ),
            call(["which", "curl"], capture_output=True),
            call(
                "curl -fsSL https://tailscale.com/install.sh | sh",
                shell=True,
                check=True,
            ),
        ]
    )


@patch("cogniceptshell.robot_api_registrar.get_user_confirmation")
@patch("subprocess.run")
def test_install_tailscale_with_confirmation_no(
    mock_run, mock_user_confirmation, registrar
):
    # Mock tailscale version check to fail (not installed)
    mock_run.side_effect = subprocess.CalledProcessError(
        1, "tailscale version"
    )

    # Mock user input to 'no'
    mock_user_confirmation.return_value = False

    with pytest.raises(SystemExit):
        registrar.install_tailscale()

    # Verify that only the version check was called
    mock_run.assert_called_once_with(
        "tailscale version", shell=True, check=True, capture_output=True
    )
    mock_user_confirmation.assert_called_once()


@patch("requests.post")
def test_get_auth_token_success(mock_post, registrar, mock_args):
    registrar.load_config_values(mock_args)
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "test_token"}
    mock_post.return_value = mock_response

    token = registrar.get_auth_token()  # Changed from get_keycloak_token

    assert token == "test_token"
    mock_post.assert_called_once_with(
        "http://keycloak.test/realms/smart_plus/protocol/openid-connect/token",
        data={
            "client_id": f"agent-client-{registrar.config.get_config('ROBOT_CODE')}",
            "client_secret": registrar.agent_client_secret,
            "grant_type": "client_credentials",
        },
    )


@patch("requests.post")
def test_get_auth_token_failure(mock_post, registrar, mock_args):
    registrar.load_config_values(mock_args)
    mock_response = Mock()
    mock_response.status_code = 401
    mock_post.return_value = mock_response

    with pytest.raises(SystemExit):
        registrar.get_auth_token()  # Changed from get_keycloak_token


@patch("requests.put")
def test_register_with_device_service_success(mock_put, registrar, mock_args):
    registrar.load_config_values(mock_args)
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "device": {"id": "test_device_id"},
            "tailscale_key": {"key": "test_key"},
        }
    }
    mock_put.return_value = mock_response

    result = registrar.register_with_device_service("test_token")

    assert result["device"]["id"] == "test_device_id"
    assert result["tailscale_key"]["key"] == "test_key"
    mock_put.assert_called_once_with(
        "http://device.test/devices/register/TEST123",
        headers={"Authorization": "Bearer test_token"},
        json={
            "device_type": "ROBOT",
            "team_id": mock.ANY,  # Use mock.ANY for the UUID
            "krapi_version": "1.0",
        },
    )


@patch("subprocess.run")
def test_connect_to_tailscale_success(mock_run, registrar, mock_args):
    registrar.load_config_values(mock_args)
    mock_run.return_value = Mock(returncode=0)

    registrar.connect_to_tailscale("test_key")

    mock_run.assert_called_once_with(
        [
            "sudo",
            "tailscale",
            "up",
            "--authkey",
            "test_key",
            "--hostname",
            "test-robot",
            "--reset",
        ],
        check=True,
    )


@patch("subprocess.run")
def test_get_tailscale_info_success(mock_run, registrar):
    mock_result = Mock()
    mock_result.stdout = json.dumps(
        {
            "Self": {
                "TailscaleIPs": ["100.100.100.100"],
                "HostName": "test-host",
                "ID": "test-id",
            }
        }
    )
    mock_run.return_value = mock_result

    result = registrar.get_tailscale_info()

    assert result == {
        "tailscale_ip": "100.100.100.100",
        "tailscale_host": "test-host",
        "tailscale_device_id": "test-id",
    }


@patch("requests.put")
def test_update_device_info_success(mock_put, registrar, mock_args):
    registrar.load_config_values(mock_args)
    tailscale_info = {
        "tailscale_ip": "100.100.100.100",
        "tailscale_host": "test-host",
        "tailscale_device_id": "test-id",
    }

    registrar.update_device_info("device-id", tailscale_info, "test-token")

    mock_put.assert_called_once_with(
        "http://device.test/devices/device-id",
        headers={"Authorization": "Bearer test-token"},
        json={
            "tailscale_ip": "100.100.100.100",
            "tailscale_host": "test-host",
            "tailscale_device_id": "test-id",
            "krapi_version": "1.0",
        },
    )


def test_store_credentials(registrar, mock_args):
    registrar.load_config_values(mock_args)
    registrar.store_credentials("test-device-id", mock_args)

    assert (
        registrar.config.config_values["ROBOT_API_DEVICE_ID"] == "test-device-id"
    )
    assert (
        registrar.config.config_values["ROBOT_API_CLIENT_ID"]
        == f"agent-client-{registrar.config.get_config('ROBOT_CODE')}"
    )
    assert (
        registrar.config.config_values["ROBOT_API_CLIENT_SECRET"] == "test_secret"
    )


@patch("requests.post")
@patch("requests.put")
@patch("subprocess.run")
def test_register_device_full_flow(
    mock_run, mock_put, mock_post, registrar, mock_args
):
    # Mock subprocess.run for tailscale operations
    mock_run.side_effect = [
        Mock(returncode=0),  # tailscale version check
        Mock(returncode=0),  # tailscale up
        Mock(
            stdout=json.dumps(
                {  # tailscale status
                    "Self": {
                        "TailscaleIPs": ["100.100.100.100"],
                        "HostName": "test-host",
                        "ID": "test-id",
                    }
                }
            )
        ),
    ]

    # Mock Keycloak token request
    mock_token_response = Mock()
    mock_token_response.status_code = 200
    mock_token_response.json.return_value = {"access_token": "test_token"}

    # Mock device registration
    mock_register_response = Mock()
    mock_register_response.status_code = 200
    mock_register_response.json.return_value = {
        "data": {
            "device": {"id": "test_device_id"},
            "tailscale_key": {"key": "test_key"},
        }
    }

    mock_post.side_effect = [mock_token_response]
    mock_put.side_effect = [mock_register_response, Mock(status_code=200)]

    # Execute full registration flow
    registrar.register_device(mock_args)

    # Verify all operations were called
    assert mock_run.call_count >= 2
    assert mock_post.call_count == 1
    assert mock_put.call_count == 2

    # Verify credentials were stored
    assert (
        registrar.config.config_values["ROBOT_API_DEVICE_ID"] == "test_device_id"
    )
    assert (
        registrar.config.config_values["ROBOT_API_CLIENT_ID"]
        == f"agent-client-{registrar.config.get_config('ROBOT_CODE')}"
    )
    assert (
        registrar.config.config_values["ROBOT_API_CLIENT_SECRET"] == "test_secret"
    )
