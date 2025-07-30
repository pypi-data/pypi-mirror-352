import os
import pytest
from unittest.mock import patch
from cogniceptshell.agent_life_cycle import AgentLifeCycle

class MockArgs:
    def __init__(self, path):
        self.path = path
        self.config = MockConfig()

class MockConfig:
    def __init__(self):
        self.config = {
            'KEY1': 'value1',
            'KEY2': 'value2'
        }

def test_populate_config_files_success(capsys, tmpdir):
    # Mock the necessary paths and files
    with patch('cogniceptshell.agent_life_cycle.os.path.expanduser') as mock_expanduser:
        mock_expanduser.return_value = str(tmpdir)

        # Create a mock template file
        template_filename = 'template.yaml'
        template_path = tmpdir.join(template_filename)
        with open(template_path, 'w') as template_file:
            template_file.write("key1: ${KEY1}\nkey2: ${KEY2}")

        # Call the function to be tested
        agent_lifecycle = AgentLifeCycle()
        agent_lifecycle.populate_config_files(MockArgs(str(tmpdir)))

        # Verify the new file is created
        assert template_filename in os.listdir(str(tmpdir))

        # Verify variable replacements
        with open(str(tmpdir.join(template_filename)), 'r') as output_file:
            content = output_file.read()
            assert 'key1: value1' in content
            assert 'key2: value2' in content

        # Capture the printed output
        captured = capsys.readouterr()
        printed_output = captured.out.strip()

        # Assert the expected output in the terminal
        assert printed_output == 'Config files populated and copied successfully.'

def test_populate_config_files_no_template_files(capsys, tmpdir):
    # Mock the necessary paths and files
    with patch('cogniceptshell.agent_life_cycle.os.path.expanduser') as mock_expanduser:
        mock_expanduser.return_value = str(tmpdir)

        # Call the function to be tested
        agent_lifecycle = AgentLifeCycle()

        # Verify failure case: No template file exists
        agent_lifecycle.populate_config_files(MockArgs(str(tmpdir)))

        # Capture the printed output
        captured = capsys.readouterr()
        printed_output = captured.out.strip()

        # Assert the expected output in the terminal
        assert 'No templates found in the specifed source folder' in printed_output

def test_populate_config_files_no_output_folder(tmpdir):
    # Mock the necessary paths and files
    with patch('cogniceptshell.agent_life_cycle.os.path.expanduser') as mock_expanduser:
        mock_expanduser.side_effect = lambda path: path.replace('~', str(tmpdir))

        # Create a mock template file
        template_filename = 'template.yaml'
        template_path = tmpdir.join(template_filename)
        with open(template_path, 'w') as template_file:
            template_file.write("key1: ${KEY1}\nkey2: ${KEY2}")

        # Set output folder to a non-existent directory
        non_existent_folder = tmpdir.join('non_existent_folder')

        # Call the function to be tested
        agent_lifecycle = AgentLifeCycle()

        # Verify failure case: Output folder doesn't exist
        with pytest.raises(FileNotFoundError) as exc_info:
            agent_lifecycle.populate_config_files(MockArgs(str(non_existent_folder)))

        # Assert the specific exception is raised
        assert "Specifed target folder for templates does not exist" in str(exc_info.value)

def test_populate_config_files_no_templates_folder(tmpdir, capsys):
    # Mock the necessary paths and files
    with patch('cogniceptshell.agent_life_cycle.os.path.expanduser') as mock_expanduser, \
            patch('cogniceptshell.agent_life_cycle.os.listdir') as mock_listdir:
        # Set the mock return values
        mock_expanduser.return_value = str(tmpdir)
        mock_listdir.side_effect = FileNotFoundError("[Errno 2] No such file or directory: '/path/to/templates'")

        # Call the function to be tested
        agent_lifecycle = AgentLifeCycle()

        # Verify failure case: No templates folder
        with pytest.raises(SystemExit):
            agent_lifecycle.populate_config_files(MockArgs(str(tmpdir)))
