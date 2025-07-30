import pytest
from unittest.mock import patch
import psutil

from cogniceptshell.agent_life_cycle import AgentLifeCycle as agent

@pytest.fixture
def mock_disk_usage():
    with patch('psutil.disk_usage') as mock_disk_usage:
        mock_disk_usage.return_value.free = 50 * (1024 * 1024 * 1024)  # 50 GB
        yield mock_disk_usage

def test_get_disk_space(mock_disk_usage):
    result = agent.get_disk_space(None)
    assert result == 50
