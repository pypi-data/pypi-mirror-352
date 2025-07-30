import re
import requests
import os
import shutil
import docker
import boto3, botocore
import mock
import yaml
import pytest
from mock import patch, MagicMock, Mock


from cogniceptshell.configuration import Configuration
from cogniceptshell.agent_life_cycle import AgentLifeCycle

from tests.unit.mock_docker_client import MockDockerClient


class SuccessEcrCredentials(object):
    def __init__(self):
        self.status_code = 200
    def json(self):
        return {"AccessKeyId": os.getenv('AWS_ACCESS_KEY_ID',""), "SecretAccessKey": os.getenv('AWS_SECRET_ACCESS_KEY', ""), "SessionToken": "" }

class NotFoundLoginResponse(object):
    def __init__(self):
        self.status_code = 404

class SuccessAwsCredentials(object):
    def __init__(self):
        self.status_code = 200

    def json(self):
        return {"AccessKeyId": os.getenv('AWS_ACCESS_KEY_ID', ""), "SecretAccessKey": os.getenv('AWS_SECRET_ACCESS_KEY', ""), "SessionToken": ""}

class NotFoundMockResponse(object):
    def __init__(self):
        self.status_code = 404

class MockUnlock:
    def __init__(self, unlock):
        self.unlock = unlock
        self.detach = False

def mock_aws_endpoint(*args, **kwargs):
    if(args[0] == "https://test.cognicept.systems/api/agent/v1/aws/assume_role"):
        return SuccessAwsCredentials()
    else:
        return NotFoundMockResponse()

def mock_ecr_endpoint(*args, **kwargs):
    if(args[0] == "https://test.cognicept.systems/api/v1/aws/assume_role/ecr"):
        return SuccessEcrCredentials()
    else:
        return NotFoundMockResponse()

def setup_file(tmpdir):
    p = tmpdir.join("runtime.env")
    p.write("AGENT_POST_API=http://0.0.0.0:8042\nAGENT_ID=test\nROBOT_CODE=testbot\nSITE_CODE=test_site\nCOG_AGENT_CONTAINERS=container1;container2\nCOG_AGENT_IMAGES=image1;image2\nCOG_COMPOSE_FILE=/path/to/compose/dir")

def setup_templates_folder(tmpdir):
    templates_dir = tmpdir.mkdir("templates")
    template_file_path = os.path.join(str(templates_dir), "template.yaml")
    with open(template_file_path, "w") as template_file:
        template_file.write("Mock template content")

def setup_wrong_file(tmpdir):
    p = tmpdir.join("runtime.env")
    p.write("COG_AGENT_CONTAINERS=container1;container2\nCOG_AGENT_IMAGES=image1")

def setup_test_docker_file(tmpdir):
    p = tmpdir.join("runtime.env")
    p.write("AWS_ACCESS_KEY_ID=TESTKEY\nAWS_SECRET_ACCESS_KEY=TESTKEY\nAWS_SESSION_TOKEN=TESTTOKEN\nCOG_AGENT_CONTAINERS=test\nCOG_AGENT_IMAGES=ubuntu:latest\nCOGNICEPT_API_URI=https://test.cognicept.systems/api/agent/v1/\nCOGNICEPT_ACCESS_KEY=CORRECT-KEY\nAGENT_POST_API=http://0.0.0.0:8024\nAGENT_ID=abcd123\nROBOT_CODE=13579\nSITE_CODE=12345")

def setup_test_docker_compose_file(tmpdir):
    p = tmpdir.join("runtime.env")
    p.write("AGENT_POST_API=http://0.0.0.0:8042\nAGENT_ID=test\nROBOT_CODE=testbot\nSITE_CODE=test_site\nAWS_ACCESS_KEY_ID=TESTKEY\nAWS_SECRET_ACCESS_KEY=TESTKEY\nAWS_SESSION_TOKEN=TESTTOKEN\nCOG_AGENT_CONTAINERS=container_test\nCOG_AGENT_IMAGES=ubuntu:latest\nCOGNICEPT_API_URI=https://test.cognicept.systems/api/agent/v1/\nCOGNICEPT_ACCESS_KEY=CORRECT-KEY\nCOG_COMPOSE_FILE=/path/to/compose/docker-compose.yaml")

def setup_wrong_api(tmpdir):
    p = tmpdir.join("runtime.env")
    p.write("COG_AGENT_CONTAINERS=test\nCOG_AGENT_IMAGES=ubuntu:latest\nCOGNICEPT_API_URI=https://wrongaddress.com/")

def setup_logs(tmpdir):

    expected_location = ".cognicept/agent/logs/directory"
    logs_dir = tmpdir.mkdir("agent").mkdir("logs")
    p = logs_dir.join("latest_log_loc.txt")
    p.write(expected_location + "\n")
    latest_log_dir = logs_dir.mkdir("directory")
    p2 = latest_log_dir.join("logDataStatus.json")
    p2.write('{"agent_id":"d1d26af0-27f0-4e45-8c6c-3e6d6e1736b7","compounding":"Null","create_ticket":true,"description":"Null","event_id":"Null","level":"Heartbeat","message":"Offline","module":"Status","property_id":"64dd2881-7010-4d9b-803e-42ea9439bf17","resolution":"Null","robot_id":"d1d26af0-27f0-4e45-8c6c-3e6d6e1736b7","source":"Null","telemetry":{},"timestamp":"2020-06-26T09:33:47.995496"}')

    p3 = latest_log_dir.join("logData1.json")
    p3.write('{"agent_id":"d1d26af0-27f0-4e45-8c6c-3e6d6e1736b7","compounding":false,"create_ticket":false,"description":"Null","event_id":"2a9e5abc-0412-4840-badc-d83094ddc0c6","level":"2","message":"Setting pose (10.986000): 9.700 9.600 -0.000","module":"Localization","property_id":"64dd2881-7010-4d9b-803e-42ea9439bf17","resolution":"Null","robot_id":"d1d26af0-27f0-4e45-8c6c-3e6d6e1736b7","source":"amcl","telemetry":{"nav_pose":{"orientation":{"w":0.99999148220339307,"x":0,"y":0,"z":-0.0041274108907466923},"position":{"x":0.02080195682017939,"y":0.024943113508386214,"z":0}},"odom_pose":{"orientation":{"w":0.99999999991375599,"x":0,"y":0,"z":-1.3133466028590658e-05},"position":{"x":7.9073011611115254e-06,"y":-1.4214209401935302e-10,"z":0}}},"timestamp":"2020-06-26T07:37:25.506519"}')

def setup_logs_extra(tmpdir):

    cog_dir = tmpdir.mkdir(".cognicept")
    kriya_dir = cog_dir.mkdir("kriya_logs")
    p = kriya_dir.join("test1.txt")
    p.write("test-data")
    p2 = kriya_dir.join("test2.txt")
    p2.write("test2-data")
    agent_dir = cog_dir.mkdir("agent").mkdir("logs")
    p3 = agent_dir.join("latest_log_loc.txt")
    p3.write(".cognicept/agent/logs/directory")
    bunched_logs_dir = agent_dir.mkdir("bunched_logs")
    p4 = bunched_logs_dir.join("bunched.txt")
    p4.write("dummy_data")
    unittest_logs = agent_dir.mkdir("unittest_logs")
    p5 = unittest_logs.join("unittest1.json")
    p5.write("unittest_dummy_data")
    dummy_agent_dir = agent_dir.mkdir("test1")
    p6 = dummy_agent_dir.join("dummy_data.json")
    p6.write("agent_dummy_data")

def mock_good_ecr_pull(self, operation_name, kwarg):
    """
    Utility mock AWS SDK for a good ECR pull function
    """
    # Used to check is ECR -- was called, fail wantedly for test framework to catch
    if (operation_name == 'GetAuthorizationToken'):
        raise boto3.exceptions.Boto3Error
    else:
        raise SystemExit

def mock_bad_ecr_pull(self, operation_name, kwarg):
    """
    Utility mock AWS SDK for a bad ECR pull function
    """
    # Used to check is ECR -- was called, fail wantedly with ClientError to handle
    if (operation_name == 'GetAuthorizationToken'):
        # Raising exception to simulate bad credentials
        resp = {
            'Error': {
                'Code': 'SomeServiceException',
                'Message': 'Details/context around the exception or error'
            },
            'ResponseMetadata': {
                'RequestId': '1234567890ABCDEF',
                'HostId': 'host ID data will appear here as a hash',
                'HTTPStatusCode': 400,
                'HTTPHeaders': {'header metadata key/values will appear here'},
                'RetryAttempts': 0
            }
        }

        raise(botocore.exceptions.ClientError(resp, operation_name))
    else:
        raise SystemExit

def mock_compose_file():
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
    return mock_file

def test_init(tmpdir,monkeypatch):
    # setup container/image config
    setup_file(tmpdir)
    monkeypatch.setattr("builtins.open", mock_compose_file())
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    assert(len(agent_lifecycle._docker_images) == 4)
    assert agent_lifecycle._compose_dir == "/path/to/compose"
    assert agent_lifecycle._docker_compose_container_name == ["camera_top","ip_cam_front"]

def test_incorrect_init(tmpdir):

    # setup container/image config
    setup_wrong_file(tmpdir)


    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    assert(len(agent_lifecycle._docker_images) == 0)

def test_latest_log_loc(tmpdir):
    args = type('', (), {})()
    args.path = str(tmpdir) + "/"

    setup_logs(tmpdir)

    agent_lifecycle = AgentLifeCycle()
    returned_location = agent_lifecycle._get_latest_log_loc(args)
    
    assert(returned_location == "agent/logs/directory")

def test_get_last_event(tmpdir, capsys):
    args = type('', (), {})()
    args.path = str(tmpdir) + "/"

    setup_logs(tmpdir)

    agent_lifecycle = AgentLifeCycle()

    capsys.readouterr().out
    agent_lifecycle.get_last_event(args)
    output = str(capsys.readouterr().out)
    matches = re.findall(r"\b2020-06-26T07:37:25.506519\b", output, re.MULTILINE)
    # check if file was found and printed 
    assert len(matches) == 1

def test_parsing_ok_kriya_logs(capsys):
    agent_lifecycle = AgentLifeCycle()

    log = """[ INFO] [1594729019.086950527]: WEBRTC:: STATUS:: ERROR
[ INFO] [1594729019.166115169]: WEBSOCKET:: STATUS:: ERROR
[ INFO] [1594729019.169204677]: AGENT:: STATUS:: ERROR
[ INFO] [1594729019.086950527]: WEBRTC:: STATUS:: OK
[ INFO] [1594729019.166115169]: WEBSOCKET:: STATUS:: OK
[ INFO] [1594729019.169204677]: AGENT:: STATUS:: OK"""
    capsys.readouterr().out
    agent_lifecycle._parse_remote_intervention_agent_logs(log)
    output = str(capsys.readouterr().out)
    matches = re.findall(r"ONLINE", output, re.MULTILINE)
    assert len(matches) == 1

def test_parsing_not_init_kriya_logs(capsys):
    agent_lifecycle = AgentLifeCycle()

    log = """[ INFO] [1594729019.169204677]: WEBSOCKET:: STATUS:: INIT"""
    capsys.readouterr().out
    agent_lifecycle._parse_remote_intervention_agent_logs(log)
    output = str(capsys.readouterr().out)
    matches = re.findall(r"NOT INITIALIZED", output, re.MULTILINE)
    assert len(matches) == 1

def test_parsing_agent_error_kriya_logs(capsys):
    agent_lifecycle = AgentLifeCycle()

    log = """[ INFO] [1594729019.086950527]: WEBRTC:: STATUS:: OK
[ INFO] [1594729019.166115169]: WEBSOCKET:: STATUS:: OK
[ INFO] [1594729019.169204677]: AGENT:: STATUS:: OK
[ INFO] [1594729019.086950527]: WEBRTC:: STATUS:: OK
[ INFO] [1594729019.166115169]: WEBSOCKET:: STATUS:: OK
[ INFO] [1594729019.169204677]: AGENT:: STATUS:: ERROR"""
    capsys.readouterr().out
    agent_lifecycle._parse_remote_intervention_agent_logs(log)
    output = str(capsys.readouterr().out)
    matches = re.findall(r"ERROR", output, re.MULTILINE)
    assert len(matches) == 1

def test_parsing_websocket_error_kriya_logs(capsys):
    agent_lifecycle = AgentLifeCycle()

    log = """[ INFO] [1594729019.086950527]: WEBRTC:: STATUS:: OK
[ INFO] [1594729019.166115169]: WEBSOCKET:: STATUS:: OK
[ INFO] [1594729019.169204677]: AGENT:: STATUS:: OK
[ INFO] [1594729019.086950527]: WEBRTC:: STATUS:: OK
[ INFO] [1594729019.166115169]: WEBSOCKET:: STATUS:: ERROR
[ INFO] [1594729019.169204677]: AGENT:: STATUS:: OK"""
    capsys.readouterr().out
    agent_lifecycle._parse_remote_intervention_agent_logs(log)
    output = str(capsys.readouterr().out)
    matches = re.findall(r"ERROR", output, re.MULTILINE)
    assert len(matches) == 1

def test_parsing_webrtc_error_kriya_logs(capsys):
    agent_lifecycle = AgentLifeCycle()

    log = """[ INFO] [1594729019.086950527]: WEBRTC:: STATUS:: OK
[ INFO] [1594729019.166115169]: WEBSOCKET:: STATUS:: OK
[ INFO] [1594729019.169204677]: AGENT:: STATUS:: OK
[ INFO] [1594729019.086950527]: WEBRTC:: STATUS:: ERROR
[ INFO] [1594729019.166115169]: WEBSOCKET:: STATUS:: OK
[ INFO] [1594729019.169204677]: AGENT:: STATUS:: OK"""
    capsys.readouterr().out
    agent_lifecycle._parse_remote_intervention_agent_logs(log)
    output = str(capsys.readouterr().out)
    matches = re.findall(r"ERROR", output, re.MULTILINE)
    assert len(matches) == 1

def test_run(tmpdir, capsys):
    args = type('', (), {})()
    args.path = str(tmpdir) + "/"

    setup_test_docker_file(tmpdir)
    setup_templates_folder(tmpdir)
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    args.config = local_cfg
    args.agents = True

    # run container
    mock_docker_client = MockDockerClient()
    with patch("docker.from_env", new=lambda: mock_docker_client):
        result = agent_lifecycle.start(args)
        assert result == True

        # check status
        output = capsys.readouterr().out
        print(output)
        agent_lifecycle.get_status(args)
        output = str(capsys.readouterr().out)

        print(output)
        matches1 = re.findall(r"ONLINE", output, re.MULTILINE)
        assert len(matches1) == 1

        result = agent_lifecycle.remove_agents(args)
        assert result == True

        # check if offline
        capsys.readouterr().out
        agent_lifecycle.get_status(args)
        output = str(capsys.readouterr().out)
        matches2 = re.findall(r"CONTAINER NOT FOUND", output, re.MULTILINE)
        assert len(matches2) == 1

def test_update_fail(tmpdir, capsys, monkeypatch):
    # setup runtime variables
    setup_test_docker_file(tmpdir)
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    args = type('', (), {})()
    args.path = str(tmpdir) + "/"
    args.reset = False
    args.config = local_cfg
    args.detach = False
    mock_docker_client = MockDockerClient()
    mock_docker_client.images._images.append('ubuntu:latest')
    with patch("docker.from_env", new=lambda: mock_docker_client):
        # run container
        args.list = ["test"]
        args.image = ["ros:colab"]
        args.detach = False

    with patch('botocore.client.BaseClient._make_api_call', new=mock_bad_ecr_pull):
        try:
            monkeypatch.setattr(requests, "get", mock_aws_endpoint)
            result = agent_lifecycle.update(args)     
        except boto3.exceptions.Boto3Error:
            result = False
        except Exception:
            result = True
        assert result == False
    
def test_update_success(tmpdir, capsys, monkeypatch):
    # setup runtime variables
    setup_test_docker_file(tmpdir)
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    args = type('', (), {})()
    args.path = str(tmpdir) + "/"
    args.reset = False
    args.config = local_cfg
    args.detach = False

    with patch('botocore.client.BaseClient._make_api_call', new=mock_bad_ecr_pull):
        args.image = ["ros:crystal"]
        try:
            monkeypatch.setattr(requests, "get", mock_aws_endpoint)
            result = agent_lifecycle.update_agents(args) 
        except boto3.exceptions.Boto3Error:
            result = False
        except Exception:
            result = True
        assert result == True

def test_update_docker(tmpdir, capsys, monkeypatch):
    # setup runtime variables
    setup_test_docker_file(tmpdir)
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    args = type('', (), {})()
    args.path = str(tmpdir) + "/"
    args.reset = False
    args.config = local_cfg
    args.detach = False

    with patch('botocore.client.BaseClient._make_api_call', new=mock_bad_ecr_pull):
        args.image = ["docker"]
        try:
            monkeypatch.setattr(requests, "get", mock_aws_endpoint)
            result = agent_lifecycle.update_agents(args) 
        except boto3.exceptions.Boto3Error:
            result = False
        except Exception:
            result = True
        assert result == True

def test_update_fail_multiple(tmpdir, capsys, monkeypatch):
    # setup runtime variables
    setup_test_docker_file(tmpdir)
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    args = type('', (), {})()
    args.path = str(tmpdir) + "/"
    args.reset = False
    args.config = local_cfg
    args.detach = False

    with patch('botocore.client.BaseClient._make_api_call', new=mock_bad_ecr_pull):
        args.image = ["ros:crystal","ros:colab"]
        try:
            monkeypatch.setattr(requests, "get", mock_aws_endpoint)
            result = agent_lifecycle.update(args) 
        except boto3.exceptions.Boto3Error:
            result = False
        except Exception:
            result = True
        assert result == False

def test_update_success_multiple(tmpdir, capsys, monkeypatch):
    # setup runtime variables
    setup_test_docker_file(tmpdir)
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    args = type('', (), {})()
    args.path = str(tmpdir) + "/"
    args.reset = False
    args.config = local_cfg
    args.detach = False

    with patch('botocore.client.BaseClient._make_api_call', new=mock_bad_ecr_pull):
        args.image = ["ros:crystal","ros:colab_aux-test-led-break"]
        try:
            monkeypatch.setattr(requests, "get", mock_aws_endpoint)
            result = agent_lifecycle.update_agents(args) 
        except boto3.exceptions.Boto3Error:
            result = False
        except Exception:
            result = True
        assert result == True

def test_update_docker_compose(tmpdir, capsys, monkeypatch):
    # setup runtime variables
    setup_test_docker_compose_file(tmpdir)
    monkeypatch.setattr("builtins.open", mock_compose_file())
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    args = type('', (), {})()
    args.path = str(tmpdir) + "/"
    args.reset = False
    args.config = local_cfg
    args.detach = False

    with patch('botocore.client.BaseClient._make_api_call', new=mock_bad_ecr_pull):
        try:
            monkeypatch.setattr(requests, "get", mock_aws_endpoint)
            result = agent_lifecycle.update_agents()
            output = str(capsys.readouterr().out)
            # update from COGNICEPT_AGENTS
            matches_cognicept_container = re.findall(r"container_test:", output, re.MULTILINE)
            # update from docker-compose file
            matches_docker_compose_container = re.findall(r"camera_top:", output, re.MULTILINE)
            assert len(matches_cognicept_container) == 1
            assert len(matches_docker_compose_container) == 1
        except boto3.exceptions.Boto3Error:
            result = False
        except Exception:
            result = True
        assert result == True

def test_agent_restart(tmpdir, capsys):
    args = type('', (), {})()
    args.path = str(tmpdir) + "/"

    setup_test_docker_file(tmpdir)
    setup_templates_folder(tmpdir)
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)
    
    args.config = local_cfg    
    args.agents = True

    mock_docker_client = MockDockerClient()
    mock_docker_client.images._images.append('ubuntu:latest')
    with patch("docker.from_env", new=lambda: mock_docker_client):
        # run container
        args.list = ["test"]
        args.attach = True
        args.prune = False
        result = agent_lifecycle.restart(args)
        assert result == True
        
        args.list = ["test"]

        # run container
        args.list = ["unknown_container"]
        result = agent_lifecycle.restart(args)
        assert result == False

        # run container
        args.list = ["test","unknown_container"]
        result = agent_lifecycle.restart(args)
        assert result == False

        args.list = ["test"]
        result = agent_lifecycle.remove_agents(args)
        assert result == True

        result = agent_lifecycle.start(args)
        assert result == True

        del args.list
        result = agent_lifecycle.remove_agents(args)
        assert result == True


def test_agent_restart_compose(tmpdir, monkeypatch, capsys):
    args = type('', (), {})()
    args.path = str(tmpdir) + "/"
    setup_test_docker_compose_file(tmpdir)
    setup_templates_folder(tmpdir)
    monkeypatch.setattr("builtins.open", mock_compose_file())
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    args.config = local_cfg    
    args.agents = True

    mock_docker_client = MockDockerClient()
    mock_docker_client.images._images.append('ubuntu:latest')
    mock_docker_client.images._images.append('412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:realsense')
    mock_docker_client.images._images.append('412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:crystal')
    with patch("docker.from_env", new=lambda: mock_docker_client):
        # run container
        args.list = ["camera_top"]
        args.attach = True
        args.prune = False
        result = agent_lifecycle.restart(args)
        assert result == True

        # run container
        args.list = ["unknown_container"]
        result = agent_lifecycle.restart(args)
        assert result == False

        # run container
        args.list = ["container_test","unknown_container"]
        result = agent_lifecycle.restart(args)
        assert result == False

        args.list = ["container_test"]
        result = agent_lifecycle.remove_agents(args)
        assert result == True

        del args.list

        # To test docker-compose works with restart function
        result = agent_lifecycle.restart(args)
        output = str(capsys.readouterr().out)
        matches_docker_compose_container = re.findall(r"camera_top:", output, re.MULTILINE)
        assert len(matches_docker_compose_container) > 0
        assert result == True

def test_correct_ecr_credentials(tmpdir, capsys, monkeypatch):

    # setup runtime variables
    setup_test_docker_file(tmpdir)

    with patch('botocore.client.BaseClient._make_api_call', new=mock_good_ecr_pull):
        local_cfg = Configuration()
        local_cfg.load_config(str(tmpdir) + "/")

        args = type('', (), {})()
        args.path = str(tmpdir) + "/"
        args.reset = False
        args.config = local_cfg
        args.detach = False

        agent_lifecycle = AgentLifeCycle()
        agent_lifecycle.configure_containers(local_cfg)
        try:
            monkeypatch.setattr(requests, "get", mock_aws_endpoint)
            result = agent_lifecycle.update(args)            
        except boto3.exceptions.Boto3Error:
            result = True
        except Exception:
            result = False

    assert(result == True)

def test_wrong_ecr_credentials(tmpdir):

    # setup runtime variables
    setup_test_docker_file(tmpdir)

    with patch('botocore.client.BaseClient._make_api_call', new=mock_bad_ecr_pull):
        local_cfg = Configuration()
        local_cfg.load_config(str(tmpdir) + "/")

        args = type('', (), {})()
        args.path = str(tmpdir) + "/"
        args.reset = False
        args.config = local_cfg
        args.detach = False

        agent_lifecycle = AgentLifeCycle()
        agent_lifecycle.configure_containers(local_cfg)
        try:
            result = agent_lifecycle.update(args)       
        except Exception:
            print('Update failed')
            result = True

    assert(result == False)

def test_get_image_digest_success():
    mock_docker_client = mock.Mock()
    mock_image = mock.Mock()
    mock_image.attrs = {"RepoDigests": ["repository@sha256:abcdef1234567890"]}
    mock_docker_client.images.get.return_value = mock_image
    image_name = "test_image"
    expected_digest = "sha256:abcdef1234567890"

    with patch("docker.from_env", new=lambda: mock_docker_client):
        # Call the function and assert the result
        agent_lifecycle = AgentLifeCycle()
        result = agent_lifecycle.get_image_digest(image_name)
        assert result == expected_digest

def test_get_image_digest_failure():
    mock_docker_client = mock.Mock()
    mock_docker_client.images.get.side_effect = docker.errors.ImageNotFound("Image not found")

    image_name = "test_image"

    with patch("docker.from_env", new=lambda: mock_docker_client):
        # Call the function and assert the result
        agent_lifecycle = AgentLifeCycle()
        result = agent_lifecycle.get_image_digest(image_name)
        assert result is None

def test_get_version_tag_success():
    image_data = ['412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/repo1','latest']
    expected_tag = 'v1.0.1'
    image_digest = 'sha12345'
    
    with patch('cogniceptshell.agent_life_cycle.AgentLifeCycle.get_image_digest', return_value=image_digest) as mock_get_image_digest:
        with patch('boto3.client') as mock_client:
                # Mock the describe_images() method
                mock_describe_images = mock_client.return_value.describe_images
                # Set the response for the describe_images() method
                mock_describe_images.return_value = {
                    'imageDetails': [
                        {'imageTags': ['latest', 'v1.0.1', 'match1.2.3']},
                    ]
                }

                # Call the function
                agent_lifecycle = AgentLifeCycle()
                ecr_client = boto3.client('ecr', region_name='ap-southeast-1')
                result = agent_lifecycle.get_version_tag_from_latest(image_data, ecr_client)

                # Assert the result
                assert result == expected_tag
                mock_get_image_digest.assert_called_with(':'.join(image_data))
                mock_client.assert_called_with('ecr', region_name='ap-southeast-1')
                mock_describe_images.assert_called_with(
                    registryId="412284733352",
                    repositoryName='repo1',
                    imageIds=[{"imageDigest": image_digest}]
                )

def test_get_version_tag_failure():
    image_data = ['412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/repo1','latest']
    image_digest = 'sha12345'
    
    with patch('cogniceptshell.agent_life_cycle.AgentLifeCycle.get_image_digest', return_value=image_digest) as mock_get_image_digest:
        with patch('boto3.client') as mock_client:
            # Raise a Boto3Error when the client is called
            mock_client.side_effect = boto3.exceptions.Boto3Error("Boto3 client error")

            # Call the function
            agent_lifecycle = AgentLifeCycle()
            result = agent_lifecycle.get_version_tag_from_latest(image_data,mock_client)

            # Assert the result is None
            assert result is None
            mock_get_image_digest.assert_called_with(':'.join(image_data))
 

def test_display_version(tmpdir, monkeypatch, capsys):
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    args = type('', (), {})()
    args.path = str(tmpdir) + "/"
    args.reset = False
    args.config = local_cfg
    
    setup_file(tmpdir)
    
    object = mock.Mock()
    object._docker_images = {"image1": "repo/image1:1.0", "image2": "repo/image2"}
    object.get_version_tag_from_latest.return_value = None
    AgentLifeCycle.display_version(object,args)
    output = str(capsys.readouterr().out)
    matches = re.findall(r"Cognicept Shell Version", output, re.MULTILINE)
    container_with_version_matches = re.findall(r"1.0", output, re.MULTILINE)
    # check if Cognicept Version is printed out
    print(output)
    assert len(matches) == 1
    assert len(container_with_version_matches) == 1

def test_clear_logs(tmpdir):

    def mock_check_sudo_password(cmd, capture_output, input, encoding):
        return True

    def mock_subprocess_clear_logs(cmd_list, stdin, stdout, stderr):

        exclude = ["sudo","-S","-k","rm","-r"]

        cmd_list = [item for item in cmd_list if item not in exclude]

        if len(cmd_list) > 0:
            for item in cmd_list:
                if os.path.isfile(item):
                    os.remove(item)
                elif os.path.exists(item):
                    shutil.rmtree(item)
        
        dummy_object = MagicMock()
        dummy_object.communicate.return_value = (b'', b'')
        return dummy_object


    args = type('', (), {})()
    args.path = str(tmpdir) + "/.cognicept/"

    kriya_logs_dir = args.path + "kriya_logs/"
    agent_logs_dir = args.path + "agent/logs"
    
    setup_logs_extra(tmpdir)

    agent_lifecycle = AgentLifeCycle()
    
    with patch('builtins.input', side_effect=['y']), patch('subprocess.run', mock_check_sudo_password), patch('subprocess.Popen', mock_subprocess_clear_logs), patch('getpass.getpass', return_value=""):
        agent_lifecycle.clear_logs(args)

    assert len(os.listdir(kriya_logs_dir))== 0
    assert len(os.listdir(agent_logs_dir)) == 3
    assert len(os.listdir(agent_logs_dir + "/bunched_logs/")) == 0
    assert len(os.listdir(agent_logs_dir + "/unittest_logs/")) == 0

def test_parse_compose(tmpdir, monkeypatch):

    setup_file(tmpdir)
    monkeypatch.setattr("builtins.open", mock_compose_file())
    local_cfg = Configuration()
    local_cfg.load_config(str(tmpdir) + "/")

    agent_lifecycle = AgentLifeCycle()
    agent_lifecycle.configure_containers(local_cfg)

    compose_agent_yaml = {
        "test_agent": {
            "network_mode": "host",
            "restart": "unless-done",
            "stdin_open": False,
            "volumes": ["/host/folder:/container/folder", "/host/folder2:/container/folder2:ro"],
            "environment": ["TEST_VAR=False"],
            "command": "test_command"
        }
    }

    options = agent_lifecycle.parse_compose(compose_agent_yaml["test_agent"])

    assert options["network_mode"] == "host"
    assert options["restart_policy"] == {"Name": "unless-done"}
    assert options["stdin_open"] == False
    assert options["tty"] == True
    assert options["volumes"]["/host/folder"] == {"bind": "/container/folder",  "mode": "rw"}
    assert options["volumes"]["/host/folder2"] == {"bind": "/container/folder2",  "mode": "ro"}
    assert options["environment"]["TEST_VAR"] == "False"
    assert options["command"] == "test_command"
