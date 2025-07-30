import os
import boto3
import pytest
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock, Mock, call
from botocore.exceptions import ClientError
from cogniceptshell.configuration import Configuration


class TestPullConfig(unittest.TestCase):

 
    def test_pull_config_templates_success(self):

        mock_args = Mock()
        mock_s3_client = Mock()
        mock_list_objects = Mock(return_value = {
            'Contents': [
                {'Key': 'robot_model/template1.yaml'},
                {'Key': 'robot_model/template2.yml'},
                {'Key': 'robot_model/other_file.txt'}
            ]
        })
        mock_download_file = Mock()

        mock_args.path = os.curdir
        mock_args.config.config = {
            'ECS_ROBOT_MODEL': 'robot_model',
            'AWS_ACCESS_KEY_ID': 'dummy_id',
            'AWS_SECRET_ACCESS_KEY': 'dummy_key',
            'AWS_SESSION_TOKEN': 'dummy_token'
        }

        mock_s3_client.list_objects_v2 = mock_list_objects
        mock_s3_client.download_file = mock_download_file

        
        with patch('boto3.client', return_value=mock_s3_client):
            object = Configuration()
            object.pull_config_templates(mock_args)  
            print(dir(mock_s3_client))

        # mock_s3_client.assert_called_once()
        mock_list_objects.assert_called_once()
        print(mock_download_file.call_args_list)
        calls = [
            call.mock_download_file("robot-config-templates", 'robot_model/template1.yaml', ".templates/template1.yaml"),
            call.mock_download_file("robot-config-templates", 'robot_model/template2.yml', ".templates/template2.yml")]
        mock_download_file.assert_has_calls(calls)

def test_pull_config_templates_list_objects_error(capsys, tmpdir, mocker):
    # 1. Setup tmpdir with a templates folder inside
    templates_folder = tmpdir.mkdir("templates")

    # 2. Mock the necessary objects and functions
    mock_args = mocker.MagicMock()
    mock_args.config.config = {
        'ECS_ROBOT_MODEL': 'robot_model',
        'AWS_ACCESS_KEY_ID': 'dummy_id',
        'AWS_SECRET_ACCESS_KEY': 'dummy_key'
    }
    mock_args.path = str(tmpdir)

    mock_s3_client = mocker.MagicMock()
    mocker.patch("boto3.client", return_value=mock_s3_client)

    mock_error = ClientError({'Error': {'Code': 'SomeErrorCode', 'Message': 'SomeErrorMessage'}}, 'ListObjectsV2')
    mock_s3_client.list_objects_v2.side_effect = mock_error

    # Create an instance of Configuration
    config = Configuration()

    # Call the function
    config.pull_config_templates(mock_args)

    # Assert the correct behavior
    assert "Failed to retrieve template config files" in capsys.readouterr().out

    assert not os.listdir(templates_folder)


def test_pull_config_templates_download_file_error(capsys, tmpdir, mocker):
    # 1. Setup tmpdir with a templates folder inside
    templates_folder = tmpdir.mkdir("templates")

    # 2. Mock the necessary objects and functions
    mock_args = mocker.MagicMock()
    mock_args.config.config = {
        'ECS_ROBOT_MODEL': 'robot_model',
        'AWS_ACCESS_KEY_ID': 'dummy_id',
        'AWS_SECRET_ACCESS_KEY': 'dummy_key'
    }
    mock_args.path = str(tmpdir)

    mock_s3_client = mocker.MagicMock()
    mocker.patch("boto3.client", return_value=mock_s3_client)

    mock_response = {
        'Contents': [
            {'Key': 'robot_model/template1.yaml'},
            {'Key': 'robot_model/template2.yml'},
            {'Key': 'robot_model/other_file.txt'}
        ]
    }
    mock_s3_client.list_objects_v2.return_value = mock_response

    mock_error = ClientError({'Error': {'Code': 'SomeErrorCode', 'Message': 'SomeErrorMessage'}}, 'DownloadFile')
    mock_s3_client.download_file.side_effect = mock_error

    # Create an instance of Configuration
    config = Configuration()

    # Call the function
    config.pull_config_templates(mock_args)

    # Assert the correct behavior
    assert "Failed to retrieve template config files" in capsys.readouterr().out

    assert not os.listdir(templates_folder)


if __name__ == '__main__':
    unittest.main()