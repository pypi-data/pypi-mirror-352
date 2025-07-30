import pytest
from unittest.mock import patch, MagicMock
from cogniceptshell.agent_life_cycle import AgentLifeCycle as agent

@pytest.fixture
def mock_response():
    response = MagicMock()
    response.json.return_value = {'info': {'version': '1.3.2'}}
    return response

@pytest.fixture
def mock_requests_get(mock_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_input_yes():
    with patch('builtins.input', return_value='y'):
        yield

@pytest.fixture
def mock_input_no():
    with patch('builtins.input', return_value='n'):
        yield

@pytest.fixture
def mock_pkg_resources():
    mock_distribution = MagicMock()
    mock_distribution.version = "1.0.2"
    with patch('pkg_resources.require', return_value=[mock_distribution]):
        yield

@pytest.fixture
def mock_os_system():
    with patch('os.system', return_value=0):
        # Set the return value of the mocked os.system to simulate success (0 exit code)
        yield

def test_version_update_skip_true(mock_pkg_resources, mock_requests_get, mock_os_system, mock_input_yes, capsys):
    args = MagicMock(skip=True)
    agent.cognicept_version_update(None, args)
    captured = capsys.readouterr()
    assert "cognicept-shell current version" in captured.out
    assert "Installing Version 1.3.2" in captured.out

def test_version_update_skip_false_input_yes(mock_pkg_resources, mock_requests_get, mock_os_system, mock_input_yes, capsys):
    args = MagicMock(skip=False)
    agent.cognicept_version_update(None, args)
    captured = capsys.readouterr()
    assert "cognicept-shell current version" in captured.out
    assert "Installing Version 1.3.2" in captured.out

def test_version_update_skip_false_input_no(mock_pkg_resources, mock_requests_get,mock_os_system, mock_input_no, capsys):
    args = MagicMock(skip=False)
    agent.cognicept_version_update(None, args)
    captured = capsys.readouterr()
    assert "cognicept-shell was not updated" in captured.out
