import json
import uuid
import pytest
import requests
from datetime import datetime
from unittest.mock import Mock, patch
from requests.exceptions import Timeout,TooManyRedirects

from cogniceptshell.agent_life_cycle import AgentLifeCycle
from cogniceptshell.common import post_event_log

@pytest.fixture
def mock_object():
    # Mock the object instance and its methods
    mock_obj = Mock()
    mock_obj._docker_images = {
        'image1': 'ecr/image1:latest',
        'image2': 'ecr/image2:latest',
    }
    return mock_obj

@pytest.fixture
def mock_args():
    # Mock the args object returned by argparse.parse_args()
    mock_args = Mock()
    mock_args.config.config = {
        'AGENT_POST_API': 'http://example.com/api',
        'AGENT_ID': 'agent123',
        'ROBOT_CODE': 'robot456',
        'SITE_CODE': 'site789',
    }
    return mock_args

@pytest.fixture()
def mock_payload():

    expected_output = {
        "agent_id": "agent123",
        "compounding": False,
        "create_ticket": False,
        "description": "Null",
        "error_code": "Null",
        "event_id": "f74a399f-7d23-4645-aaa5-3446eab0d4e4",
        "level": 1,
        "message": "Test message",
        "module": "Updater",
        "property_id": "site789",
        "resolution": "Null",
        "robot_id": "robot456",
        "source": "auto_updater",
        "timestamp": "2024-08-20T13:41:38.909134"
    }   

    return expected_output 

class MockPostResponseSuccess:
    def __init__(self):
        self.status_code = 200

class MockPostResponseFailure:
    def __init__(self):
        self.status_code = 404

def test_successfull_event_log_post(mock_args, mock_payload):
    with patch("cogniceptshell.common.datetime.datetime") as mock_datetime, \
         patch("requests.post", Mock(return_value=MockPostResponseSuccess())), \
         patch("uuid.uuid4", Mock(return_value="f74a399f-7d23-4645-aaa5-3446eab0d4e4")), \
         patch("cogniceptshell.common.is_agent_active", Mock(return_value=True)):
                
            mock_datetime.utcnow.return_value  = datetime.fromisoformat("2024-08-20T13:41:38.909134")
            response = post_event_log(mock_args, "Test message")

    assert response == mock_payload

def test_failed_request_event_log_post(mock_args):
    with patch("cogniceptshell.common.datetime.datetime") as mock_datetime, \
         patch("requests.post", Mock(return_value=MockPostResponseFailure())), \
         patch("uuid.uuid4", Mock(return_value="f74a399f-7d23-4645-aaa5-3446eab0d4e4")):
                
            mock_datetime.utcnow.return_value  = datetime.fromisoformat("2024-08-20T13:41:38.909134")
            response = post_event_log(mock_args, "Test message")

    assert response == None

def test_exception_event_log_post(mock_args):
    with patch("cogniceptshell.common.datetime.datetime") as mock_datetime, \
         patch("requests.post", Mock(side_effect=TooManyRedirects)), \
         patch("uuid.uuid4", Mock(return_value="f74a399f-7d23-4645-aaa5-3446eab0d4e4")):
                
            mock_datetime.utcnow.return_value  = datetime.fromisoformat("2024-08-20T13:41:38.909134")
            response = post_event_log(mock_args, "Test message")

    assert response == None

def test_streamer_not_running_event_log_post(mock_args, mock_payload):
    with patch("cogniceptshell.common.datetime.datetime") as mock_datetime, \
         patch("requests.post", Mock(return_value=MockPostResponseSuccess())), \
         patch("uuid.uuid4", Mock(return_value="f74a399f-7d23-4645-aaa5-3446eab0d4e4")), \
         patch("cogniceptshell.common.is_agent_active", Mock(return_value=False)):
  
            mock_datetime.utcnow.return_value  = datetime.fromisoformat("2024-08-20T13:41:38.909134")
            response = post_event_log(mock_args, "Test message")

    assert response == None