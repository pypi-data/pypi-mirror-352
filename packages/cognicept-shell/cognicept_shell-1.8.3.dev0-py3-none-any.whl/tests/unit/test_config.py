import mock
import pytest
import requests
from mock import patch
import os
import yaml
from cogniceptshell.common import bcolors

from cogniceptshell.configuration import Configuration


class SuccessAwsCredentials(object):
    def __init__(self):
        self.status_code = 200

    def json(self):
        return {"AccessKeyId": os.getenv('AWS_ACCESS_KEY_ID', ""), "SecretAccessKey": os.getenv('AWS_SECRET_ACCESS_KEY', ""), "SessionToken": ""}


class NotFoundMockResponse(object):
    def __init__(self):
        self.status_code = 404


def mock_aws_endpoint(*args, **kwargs):
    if(args[0] == "https://test.cognicept.systems/api/agent/v1/aws/assume_role"):
        return SuccessAwsCredentials()
    else:
        return NotFoundMockResponse()

def setup_file(tmpdir):
    p = tmpdir.join("runtime.env")
    p.write("COG_AGENT_CONTAINERS=container1;container2\nCOG_AGENT_IMAGES=image1;image2\nCOGNICEPT_API_URI=https://test.cognicept.systems/api/agent/v1/aws/assume_role\nCOGNICEPT_ACCESS_KEY=CORRECT-KEY")


def setup_wrong_uri_file(tmpdir):
    p = tmpdir.join("runtime.env")
    p.write(
        "COGNICEPT_API_URI=https://www.wronguri.blame\nCOGNICEPT_ACCESS_KEY=INCORRECT-KEY")


def setup_correct_uri_file(tmpdir):
    p = tmpdir.join("runtime.env")
    p.write(
        "COGNICEPT_API_URI=https://test.cognicept.systems/api/agent/v1/\nCOGNICEPT_ACCESS_KEY=CORRECT-KEY")


def setup_wrong_uri_file_for_init(tmpdir):
    p = tmpdir.join("runtime.env")

def setup_correct_uri_file_for_init(tmpdir):
    p = tmpdir.join("runtime.env")
    p.write(
        "COGNICEPT_USER_API_URI=https://test.cognicept.systems/api/agent/v1/")

def mock_shutil_copy_fail_no_space(arg1, arg2):
    test_exp = OSError(28, 'No space left on device')
    raise(test_exp)

def mock_shutil_copy_fail_others(arg1, arg2):
    test_exp = OSError(1, 'Operation not permitted')
    raise(test_exp)

def mock_shutil_copy_success(arg1, arg2):
    pass

def mock_file_write_fail(arg1, arg2):
    raise(PermissionError)

def test_yes_input():
    object = Configuration()
    assert (object._interpret_bool_input("Y") == True)

def test_no_input():
    object = Configuration()
    assert (object._interpret_bool_input("n") == False)

def test_other_input():
    object = Configuration()
    assert (object._interpret_bool_input("g") == None)
    assert (object._interpret_bool_input("%") == None)
    assert (object._interpret_bool_input("1") == None)
    assert (object._interpret_bool_input("akjflakjewr4f56f74ew@!!@$@!$") == None)

def test_is_ssh_disabled(tmpdir):
    setup_file(tmpdir)
    object = Configuration()
    object.load_config(str(tmpdir) + "/")
    assert (object.is_ssh_enabled() == False)    
    object.config["COG_ENABLE_SSH_KEY_AUTH"] = False
    assert (object.is_ssh_enabled() == False)

def test_is_ssh_disabled(tmpdir):
    setup_file(tmpdir)
    object = Configuration()
    object.load_config(str(tmpdir) + "/")
    object.config["COG_ENABLE_SSH_KEY_AUTH"] = True
    assert (object.is_ssh_enabled() == True)


def test_incorrect_cognicept_key_fetch_aws_keys(tmpdir, capsys, monkeypatch):
    setup_wrong_uri_file(tmpdir)
    
    monkeypatch.setattr(requests, "get", mock_aws_endpoint)
    object = Configuration()
    object.load_config(str(tmpdir) + "/")
    try:
        result = object.fetch_aws_keys()
        assert(result == False)
    except:
        pytest.fail("Incorrect Cognicept API URI gave exception", pytrace=True)


def test_correct_cognicept_key_fetch_aws_keys(tmpdir, capsys, monkeypatch):
    setup_correct_uri_file(tmpdir)

    monkeypatch.setattr(requests, "get", mock_aws_endpoint)
    object = Configuration()
    object.load_config(str(tmpdir) + "/")
    try:
        result = object.fetch_aws_keys()
        assert(result == SuccessAwsCredentials().json())
    except:
        pytest.fail("Correct Cognicept API URI gave exception", pytrace=True)


def test_wrong_get_cognicept_api_uri_init(tmpdir, capsys):
    setup_wrong_uri_file_for_init(tmpdir)
    object = Configuration()
    object.load_config(str(tmpdir) + "/")
    result = object.get_cognicept_user_api_uri()
    assert(result == 'https://app.kabam.ai/api/web/v2/')


def test_correct_get_cognicept_api_uri_init(tmpdir, capsys):
    setup_correct_uri_file_for_init(tmpdir)
    object = Configuration()
    object.load_config(str(tmpdir) + "/")
    result = object.get_cognicept_user_api_uri()
    assert(result == 'https://test.cognicept.systems/api/agent/v1/')


def test_no_runtime_dotenv(tmpdir, capsys):
    object = Configuration()
    object.load_config(str(tmpdir) + "/")
    captured = capsys.readouterr()
    assert str(captured.out) == "Configuration file `" + str(tmpdir) + "/runtime.env` does not exist.\nConfiguration file `" + str(tmpdir) + "/runtime.env` is empty, You can start adding the configs.\n"
    
def test_with_runtime_dotenv(tmpdir, capsys):
    setup_file(tmpdir)
    object = Configuration()
    result = object.load_config(str(tmpdir) + "/")
    assert result == True

def test_save_config_success(tmpdir, capsys):
    setup_file(tmpdir)
    object = Configuration()
    result = object.load_config(str(tmpdir) + "/")
    object.save_config(args=None)
    captured = capsys.readouterr()
    assert str(captured.out) == bcolors.OKBLUE + "Backed up runtime configuration to: " + str(tmpdir) + "/runtime.env.bk" + bcolors.ENDC + "\n" + \
                                bcolors.OKGREEN + "Runtime configuration has been updated" + bcolors.ENDC + "\n"

def test_save_config_fail_backup_no_space(tmpdir, capsys):
    setup_file(tmpdir)
    object = Configuration()
    result = object.load_config(str(tmpdir) + "/")
    with patch('shutil.copyfile', new=mock_shutil_copy_fail_no_space):
        object.save_config(args=None)
        captured = capsys.readouterr()
    assert str(captured.out) == bcolors.FAIL + "Could not back up runtime configuration. Aborting saving runtime configuration. No space left on device!" + bcolors.ENDC + "\n"

def test_save_config_fail_backup_other_exceptions(tmpdir, capsys):
    setup_file(tmpdir)
    object = Configuration()
    result = object.load_config(str(tmpdir) + "/")
    with patch('shutil.copyfile', new=mock_shutil_copy_fail_others):
        object.save_config(args=None)
        captured = capsys.readouterr()
    assert str(captured.out) == bcolors.FAIL + "Could not back up runtime configuration. Aborting saving runtime configuration: Operation not permitted" + bcolors.ENDC + "\n"

def test_save_config_fail_permissions(tmpdir, capsys):
    setup_file(tmpdir)
    object = Configuration()
    result = object.load_config(str(tmpdir) + "/")
    # Mock shutil to succeed blindly to trigger 
    with patch('shutil.copyfile', new=mock_shutil_copy_success):
        with mock.patch("builtins.open", mock_file_write_fail):
            object.save_config(args=None)
            captured = capsys.readouterr()
    assert str(captured.out) == bcolors.OKBLUE + "Backed up runtime configuration to: " + str(tmpdir) + "/runtime.env.bk" + bcolors.ENDC + "\n" + \
                                bcolors.FAIL + "Could not write into `" + str(tmpdir) + "/runtime.env" + "`. Please check write permission or run with `sudo`." + bcolors.ENDC + "\n"
    
def test_get_docker_compose(monkeypatch):
    object = Configuration()
    # Mock config dictionary with COG_COMPOSE_DIR key
    object.config = {"COG_COMPOSE_FILE": "/path/to/docker-compose.yml"}
    
    # Mock yaml file contents
    yaml_data = """
    services:
        camera_top:
            image: 412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:realsense
        ip_cam_front:
            image: 412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:crystal
    """
    
    # Mock the open() function to return yaml file contents
    mock_file = mock.mock_open(read_data=yaml_data)
    monkeypatch.setattr("builtins.open", mock_file)
    # Call the function with the mock config
    result = object.get_docker_compose()
    
    # Check that the expected dictionary was returned
    expected_result = {"camera_top": "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:realsense", "ip_cam_front": "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:crystal"}
    assert result == expected_result

def test_fail_get_docker_compose_(monkeypatch, capsys):
    object = Configuration()
    # Mock config dictionary with COG_COMPOSE_DIR key
    object.config = {"COG_COMPOSE_FILE": "/path/to/docker-compose.yml"}
    
    # Call the function with the input directory but file not found
    result = object.get_docker_compose()
    assert result == {}

    # Mock empty file contents
    yaml_data = """"""
    
    # Mock the open() function to return yaml file contents
    mock_file = mock.mock_open(read_data=yaml_data)
    monkeypatch.setattr("builtins.open", mock_file)
    # Call the function with the mock config with empty data
    result = object.get_docker_compose()
    assert result == {}
    
    # Test wrong try get data from invalid yaml format docker-compose file
    yaml_data = """
    services:
    camera_top:
            image: 412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:realsense
        ip_cam_front:
            image: 412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:crystal
    """
    mock_file1 = mock.mock_open(read_data=yaml_data)
    monkeypatch.setattr("builtins.open", mock_file1)
    result = object.get_docker_compose()
    assert result == {}

def test_get_robot_config_success():
    object = Configuration()
    object.get_cognicept_api_uri = mock.Mock(
        return_value="https://dev.cognicept.systems/api/agent/v2/")
    object.get_cognicept_credentials = mock.Mock(
        return_value="mock_key")

    class MockResponse:
        def __init__(self) -> None:
            self.status_code = 200
        
        def json(self):
           return {"PROPERTIES": {"CLOSE_ENOUGH_DISTANCE": {"value": "0.5"}}}

    with patch("requests.get", mock.Mock(return_value=MockResponse())):
        robot_config = object.get_robot_config()
    assert robot_config is not None
    assert isinstance(robot_config, dict)
    assert robot_config.get("CLOSE_ENOUGH_DISTANCE", None) == "0.5"

def test_get_robot_config_failure():
    object = Configuration()
    object.get_cognicept_api_uri = mock.Mock(
        return_value="https://dev.cognicept.systems/api/agent/v2/")
    object.get_cognicept_credentials = mock.Mock(
        return_value="gdgds")

    class MockResponse:
        def __init__(self) -> None:
            self.status_code = 401
        
        def json(self):
           return {}

    with patch('requests.get', new=mock.Mock(return_value=MockResponse())):\
        assert object.get_robot_config() == {}

def test_update_robot_config_success():
    object = Configuration()
    object.config = {}
    mock_config = {"property_1": "A", "property_2": "B"}
    object.get_robot_config = mock.Mock(return_value=mock_config)

    update_status = object.update_robot_config(args=None)
    assert update_status == True

    assert object.config.get("property_1", None) == "A"
    assert object.config.get("property_2", None) == "B"

def test_update_robot_config_failure():
    object = Configuration()
    object.config = {}
    object.get_robot_config = mock.Mock(return_value=None)

    update_status = object.update_robot_config(args=None)
    assert update_status == False

def setup_compose_agents(tmpdir, agent_config):

    # Create config files
    runtime_file = tmpdir.join("runtime.env") # TODO: Remove after compose migration
    agent_config_file = tmpdir.join("docker-compose.yaml")
    runtime_file.write(f"COG_COMPOSE_FILE={agent_config_file}\nCOG_AGENT_CONTAINERS=test_agent\nCOG_AGENT_IMAGES=test_image") # TODO: Remove after compose migration

    # Add configs
    agent_config_file.write(yaml.dump(agent_config))

    # Check created configs
    assert os.path.isfile(runtime_file)
    assert os.path.isfile(agent_config_file)
    with open(agent_config_file, "r") as f:
        assert yaml.safe_load(f) == agent_config

def test_agent_disabled(tmpdir):

    agent_config = {
        "services": {
                "test_agent_1": {
                    "enabled": False,
                    "container_name": "test_agent_1",
                    "image": "test_image_1"
                },
                "test_agent_2": {
                    "container_name": "test_agent_2",
                    "image": "test_image_2"
                }
        }
    }

    setup_compose_agents(tmpdir, agent_config)

    config = Configuration()
    config.load_config(tmpdir + "/")
    print(config.config)
    assert "COG_COMPOSE_FILE" in list(config.config.keys())

    enabled_agents = {
                "test_agent_2":"test_image_2"
    }
    assert config.get_docker_compose() == enabled_agents

def test_agent_enabled(tmpdir):

    agent_config = {
        "services": {
                "test_agent_1": {
                    "container_name": "test_agent_1",
                    "image": "test_image_1"
                },
                "test_agent_2": {
                    "container_name": "test_agent_2",
                    "image": "test_image_2"
                }
        }
    }
    setup_compose_agents(tmpdir, agent_config)

    config = Configuration()
    config.load_config(tmpdir + "/")
    print(config.config)
    assert "COG_COMPOSE_FILE" in list(config.config.keys())

    enabled_agents = {
                "test_agent_1":"test_image_1",
                "test_agent_2":"test_image_2"
    }
    assert config.get_docker_compose() == enabled_agents
