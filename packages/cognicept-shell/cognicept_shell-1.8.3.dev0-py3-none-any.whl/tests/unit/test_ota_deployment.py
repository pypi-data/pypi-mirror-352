import os
import pytest
import subprocess
import zipfile
from mock import Mock, patch
from cogniceptshell.ota_updater import OTAUpdater
from cogniceptshell.common import bcolors


def error_log(message):
    return bcolors.FAIL + message + bcolors.ENDC

def warn_log(message):
    return bcolors.WARNING + message + bcolors.ENDC

def success_log(message):
    return bcolors.OKGREEN + message + bcolors.ENDC

def info_log(message):
    return bcolors.OKBLUE + message + bcolors.ENDC

class MockConfig:
    def __init__(self):
        self.config = None

class MockArgs:

    def __init__(self):
        self.path = None
        self.config = MockConfig()

def create_zipfile(base_path, filename):
    zipfile_path = os.path.join(base_path, filename)
    zipfile.ZipFile(zipfile_path, "w").close()

def create_service_file(base_path, filename):
    
    service_file_path = os.path.join(base_path, filename)
    open(service_file_path, "w").close()

def test_download_ota_fail_no_base_folder(capsys):

    updater = OTAUpdater()
    mock_args = MockArgs()
    mock_args.path = "/non/existent/path"

    result = updater.download_ota_server(mock_args)
    assert result == False
    assert error_log(f"Cannot update ota server: /non/existent/path does not exist") in capsys.readouterr().out

def test_download_ota_fail_empty_list_objects(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": None})
    mock_boto3_client.list_objects_v2 = mock_list_objects

    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client):
        updater = OTAUpdater()
        result = updater.download_ota_server(mock_args)

        assert result == False
        assert error_log("Could not update ota server: Empty response") in capsys.readouterr().out

def test_download_ota_fail_download_fail(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": [{"Key": "other_file"}]})
    mock_boto3_client.list_objects_v2 = mock_list_objects

    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client):
        updater = OTAUpdater()
        result = updater.download_ota_server(mock_args)    

        assert result == False
        assert error_log(f"Could not update ota server: file not found at {os.path.join(mock_args.path, 'auto_update_server.zip')}") in capsys.readouterr().out

def test_download_ota_success(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = str(tmpdir)

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": [{"Key": "auto_update_server.zip"}]})
    mock_boto3_client.list_objects_v2 = mock_list_objects
    mock_download_file = Mock(side_effect= lambda x, y, z: create_zipfile(mock_args.path, "auto_update_server.zip"))
    mock_boto3_client.download_file = mock_download_file

    mock_zipfile = Mock()
    mock_extract_all = Mock()
    mock_zipfile.extract_all = mock_extract_all

    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client),\
         patch("subprocess.check_call", Mock(return_value=0)):
        
        print(os.listdir(mock_args.path))
        updater = OTAUpdater()
        result = updater.download_ota_server(mock_args)
        assert result == True

def test_setup_ota_fail_no_base_folder(capsys):

    updater = OTAUpdater()
    mock_args = MockArgs()
    mock_args.path = "/non/existent/path"

    result = updater.setup_ota_server(mock_args)
    assert result == False
    assert error_log(f"Cannot setup ota server: /non/existent/path does not exist") in capsys.readouterr().out


def test_download_ota_fail_no_lock_folder(capsys, tmpdir):
    
    mock_args = MockArgs()
    mock_args.path = tmpdir


    with patch("cogniceptshell.ota_updater.OTAUpdater.create_ota_lock_folder", Mock(return_value=False)):
        updater = OTAUpdater()
        result = updater.setup_ota_server(mock_args)

        assert result == False
        assert error_log("Could not setup ota lock folder") in capsys.readouterr().out

def test_setup_ota_fail_empty_list_objects(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": None})
    mock_boto3_client.list_objects_v2 = mock_list_objects

    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client):
        updater = OTAUpdater()
        result = updater.setup_ota_server(mock_args)

        assert result == False
        assert error_log("Could not setup ota service: Empty response") in capsys.readouterr().out

def test_setup_ota_fail_download_fail(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": [{"Key": "auto_update_server.service"}]})
    mock_boto3_client.list_objects_v2 = mock_list_objects

    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client):
        updater = OTAUpdater()   
        result = updater.setup_ota_server(mock_args)    

        assert result == False
        assert error_log(f"Could not setup ota service: service file not found") in capsys.readouterr().out   

def test_setup_ota_populate_home_failed(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": [{"Key": "auto_update_server.service"}]})
    mock_boto3_client.list_objects_v2 = mock_list_objects
    mock_boto3_client.download_file = Mock()

    create_service_file(mock_args.path, "auto_update_server.service")
    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_home_in_service_file", Mock(return_value=False)):
        updater = OTAUpdater()   
        result = updater.setup_ota_server(mock_args)  

        assert result == False
        assert error_log("Could not setup ota server: Failed to populate HOME in service file") in capsys.readouterr().out

def test_setup_ota_populate_user_failed(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": [{"Key": "auto_update_server.service"}]})
    mock_boto3_client.list_objects_v2 = mock_list_objects
    mock_boto3_client.download_file = Mock()

    create_service_file(mock_args.path, "auto_update_server.service")
    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_user_in_service_file", Mock(return_value=False)):
        updater = OTAUpdater()   
        result = updater.setup_ota_server(mock_args)  

        assert result == False
        assert error_log("Could not setup ota server: Failed to populate USER in service file") in capsys.readouterr().out

def test_setup_ota_failed_to_copy_file(capsys, tmpdir):
    mock_args = MockArgs()
    mock_args.path = tmpdir

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": [{"Key": "auto_update_server.service"}]})
    mock_boto3_client.list_objects_v2 = mock_list_objects
    mock_boto3_client.download_file = Mock()

    create_service_file(mock_args.path, "auto_update_server.service")
    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_home_in_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_user_in_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.copy_service_file", Mock(return_value=False)):
        updater = OTAUpdater()   
        result = updater.setup_ota_server(mock_args)  

        assert result == False
        assert error_log(f"Could not setup ota service: Failed to copy service file") in capsys.readouterr().out

def test_setup_ota_failed_to_reload_services(capsys, tmpdir):
    mock_args = MockArgs()
    mock_args.path = tmpdir

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": [{"Key": "auto_update_server.service"}]})
    mock_boto3_client.list_objects_v2 = mock_list_objects
    mock_boto3_client.download_file = Mock()

    create_service_file(mock_args.path, "auto_update_server.service")
    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_home_in_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_user_in_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.copy_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.reload_services", Mock(return_value=False)):

        updater = OTAUpdater()   
        result = updater.setup_ota_server(mock_args)  

        assert result == False
        assert error_log("Could not setup ota service: Failed to reload services") in capsys.readouterr().out

def test_setup_ota_failed_to_enable_services(capsys, tmpdir):
    mock_args = MockArgs()
    mock_args.path = tmpdir

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": [{"Key": "auto_update_server.service"}]})
    mock_boto3_client.list_objects_v2 = mock_list_objects
    mock_boto3_client.download_file = Mock()

    create_service_file(mock_args.path, "auto_update_server.service")
    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_home_in_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_user_in_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.copy_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.reload_services", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.enable_service", Mock(return_value=False)):

        updater = OTAUpdater()   
        result = updater.setup_ota_server(mock_args)  

        assert result == False
        assert error_log("Could not setup ota service: Failed to enable service") in capsys.readouterr().out

def test_setup_ota_failed_to_start_service(capsys, tmpdir):
    mock_args = MockArgs()
    mock_args.path = tmpdir

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": [{"Key": "auto_update_server.service"}]})
    mock_boto3_client.list_objects_v2 = mock_list_objects
    mock_boto3_client.download_file = Mock()

    create_service_file(mock_args.path, "auto_update_server.service")
    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_home_in_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_user_in_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.copy_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.reload_services", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.enable_service", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.start_service", Mock(return_value=False)):
    
        updater = OTAUpdater()   
        result = updater.setup_ota_server(mock_args)  

        assert result == False
        assert error_log("Could not setup ota service: Failed to start service") in capsys.readouterr().out

def test_setup_ota_success(capsys, tmpdir):
    mock_args = MockArgs()
    mock_args.path = tmpdir

    mock_boto3_client = Mock()
    mock_list_objects = Mock(return_value={"Contents": [{"Key": "auto_update_server.service"}]})
    mock_boto3_client.list_objects_v2 = mock_list_objects
    mock_boto3_client.download_file = Mock()

    create_service_file(mock_args.path, "auto_update_server.service")
    with patch("cogniceptshell.ota_updater.create_boto3_client", return_value=mock_boto3_client),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_home_in_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.populate_user_in_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.copy_service_file", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.reload_services", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.enable_service", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.start_service", Mock(return_value=True)):
    
        updater = OTAUpdater()   
        result = updater.setup_ota_server(mock_args)  

        assert result == True
        assert success_log("Sucessfully started the ota server") in capsys.readouterr().out

def test_disable_ota_disable_failed(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    with patch("cogniceptshell.ota_updater.OTAUpdater.disable_service", Mock(return_value=False)):

        updater = OTAUpdater()
        result = updater.disable_ota(mock_args)

        assert result == False
        assert error_log("Could not disable ota service") in capsys.readouterr().out

def test_disable_ota_stop_failed(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    with patch("cogniceptshell.ota_updater.OTAUpdater.disable_service", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.stop_service", Mock(return_value=False)):

        updater = OTAUpdater()
        result = updater.disable_ota(mock_args)

        assert result == False
        assert error_log("Could not stop ota service") in capsys.readouterr().out

def test_disable_ota_remove_zip_failed(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    with patch("cogniceptshell.ota_updater.OTAUpdater.disable_service", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.stop_service", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.remove_ota_zip", Mock(return_value=False)):

        updater = OTAUpdater()
        result = updater.disable_ota(mock_args)

        assert result == False
        assert error_log("Could not remove ota zip file") in capsys.readouterr().out

def test_disable_ota_remove_server_folder_failed(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    with patch("cogniceptshell.ota_updater.OTAUpdater.disable_service", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.stop_service", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.remove_ota_zip", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.remove_ota_folder", Mock(return_value=False)):

        updater = OTAUpdater()
        result = updater.disable_ota(mock_args)

        assert result == False
        assert error_log("Could not remove ota server source") in capsys.readouterr().out

def test_disable_ota_remove_service_file_failed(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    with patch("cogniceptshell.ota_updater.OTAUpdater.disable_service", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.stop_service", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.remove_ota_zip", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.remove_ota_folder", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.remove_service_file", Mock(return_value=False)):

        updater = OTAUpdater()
        result = updater.disable_ota(mock_args)

        assert result == False
        assert error_log("Failed to delete service file") in capsys.readouterr().out

def test_disable_ota_success(capsys, tmpdir):

    mock_args = MockArgs()
    mock_args.path = tmpdir

    with patch("cogniceptshell.ota_updater.OTAUpdater.disable_service", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.stop_service", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.remove_ota_zip", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.remove_ota_folder", Mock(return_value=True)),\
        patch("cogniceptshell.ota_updater.OTAUpdater.remove_service_file", Mock(return_value=True)):

        updater = OTAUpdater()
        result = updater.disable_ota(mock_args)

        assert result == True
        assert success_log("Successfully disabled and removed OTA server") in capsys.readouterr().out


def test_copy_service_file_fail():
    with patch("subprocess.check_call", Mock(side_effect=subprocess.CalledProcessError(1, "cp"))): 
        updater = OTAUpdater()
        assert updater.copy_service_file("test_file") == False

def test_copy_service_file_success():
    with patch("subprocess.check_call", Mock(return_value=0)):  
        updater = OTAUpdater()
        assert updater.copy_service_file("test_file") == True


def test_reload_service_fail():
    with patch("subprocess.check_call", Mock(side_effect=subprocess.CalledProcessError(1, "reload"))): 
        updater = OTAUpdater()
        assert updater.reload_services() == False

def test_reload_service_success():
    with patch("subprocess.check_call", Mock(return_value=0)):  
        updater = OTAUpdater()
        assert updater.reload_services() == True


def test_enable_service_fail():
    with patch("subprocess.check_call", Mock(side_effect=subprocess.CalledProcessError(1, "reload"))): 
        updater = OTAUpdater()
        assert updater.enable_service() == False

def test_enable_service_success():
    with patch("subprocess.check_call", Mock(return_value=0)):  
        updater = OTAUpdater()
        assert updater.enable_service() == True

def test_start_service_fail():
    with patch("subprocess.check_call", Mock(side_effect=subprocess.CalledProcessError(1, "reload"))): 
        updater = OTAUpdater()
        assert updater.start_service() == False

def test_start_service_success():
    with patch("subprocess.check_call", Mock(return_value=0)):  
        updater = OTAUpdater()
        assert updater.start_service() == True

def test_disable_service_fail():
    with patch("subprocess.check_call", Mock(side_effect=subprocess.CalledProcessError(1, "reload"))): 
        updater = OTAUpdater()
        assert updater.disable_service() == False

def test_disable_service_success():
    with patch("subprocess.check_call", Mock(return_value=0)):  
        updater = OTAUpdater()
        assert updater.disable_service() == True

def test_stop_service_fail():
    with patch("subprocess.check_call", Mock(side_effect=subprocess.CalledProcessError(1, "reload"))): 
        updater = OTAUpdater()
        assert updater.stop_service() == False

def test_stop_service_success():
    with patch("subprocess.check_call", Mock(return_value=0)):  
        updater = OTAUpdater()
        assert updater.stop_service() == True