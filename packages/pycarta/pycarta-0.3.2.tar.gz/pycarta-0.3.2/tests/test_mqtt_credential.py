import pytest
from unittest.mock import patch, Mock, mock_open
import os

# Constants for testing
TEST_TAG = "test-tag"
TEST_FILE_TYPES = ["broker_address", "certificate", "private_key", "ca_certificate"]
TEST_FILE_CONTENT = {
    "broker_address": "broker_address_content",
    "certificate": "certificate_content",
    "private_key": "private_key_content",
    "ca_certificate": "ca_certificate_content"
}
TEST_FILE_PATHS = {
    "broker_address": "dummy/broker_address.pem",
    "certificate": "dummy/certificate.pem.crt",
    "private_key": "dummy/private_key.pem.key",
    "ca_certificate": "dummy/ca_certificate.pem"
}

def create_mock_file(name, file_id, path):
    """
    Helper function to create a mock file object with specified attributes.
    """
    mock_file = Mock()
    mock_file.id = file_id
    mock_file.name = name
    mock_file.path = path
    return mock_file

@pytest.fixture
def mock_agent():
    """
    Fixture to mock the pycarta.mqtt.credential.get_agent.
    """
    with patch('pycarta.mqtt.credential.get_agent') as mock_get_agent:
        agent = Mock()
        mock_get_agent.return_value = agent
        yield agent

@pytest.fixture
def mock_list_files():
    """
    Fixture to mock the list_files function from pycarta.admin.file.
    """
    with patch('pycarta.mqtt.credential.list_files') as mock_list:
        yield mock_list

@pytest.fixture
def mock_get_file():
    """
    Fixture to mock the get_file function from pycarta.admin.file.
    """
    with patch('pycarta.mqtt.credential.get_file') as mock_get:
        yield mock_get


def test_upload_mqtt_credentials_success(mock_agent, mock_list_files):
    """
    Test successful upload of MQTT credentials from file paths.
    """
    # Mock that no files currently exist
    mock_list_files.return_value = []

    # Mock responses
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_agent.post.return_value = mock_response
    mock_agent.patch.return_value = mock_response

    # Mock file opening (any file read returns "dummy_content")
    m = mock_open(read_data="dummy_content")
    with patch("builtins.open", m):
        # Import after mocking
        import pycarta.mqtt.credential as credential

        # Perform upload
        success = credential.upload_mqtt_credentials(
            file_paths=TEST_FILE_PATHS,
            tag=TEST_TAG,
            overwrite=False
        )

    assert success
    # Since no existing files, each file is posted
    assert mock_agent.post.call_count == len(TEST_FILE_PATHS)
    mock_agent.patch.assert_not_called()

def test_upload_mqtt_credentials_overwrite(mock_agent, mock_list_files):
    """
    Test uploading MQTT credentials with overwrite enabled.
    """
    # Mock existing files
    existing_files = [
        create_mock_file("broker_address.pem", "id1", f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"),
        create_mock_file("certificate.pem", "id2", f"/mqtt_credentials/{TEST_TAG}/certificate.pem"),
        create_mock_file("private_key.pem", "id3", f"/mqtt_credentials/{TEST_TAG}/private_key.pem"),
        create_mock_file("ca_certificate.pem", "id4", f"/mqtt_credentials/{TEST_TAG}/ca_certificate.pem"),
    ]
    mock_list_files.return_value = existing_files

    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_agent.patch.return_value = mock_response

    # Mock file opening
    m = mock_open(read_data="new_dummy_content")
    with patch("builtins.open", m):
        import pycarta.mqtt.credential as credential
        success = credential.upload_mqtt_credentials(
            file_paths=TEST_FILE_PATHS,
            tag=TEST_TAG,
            overwrite=True
        )

    assert success
    # Overwrite => use PATCH for all existing files
    assert mock_agent.patch.call_count == len(TEST_FILE_PATHS)
    mock_agent.post.assert_not_called()

def test_upload_mqtt_credentials_skip_existing(mock_agent, mock_list_files):
    """
    Test uploading MQTT credentials without overwrite when files already exist.
    """
    existing_files = [
        create_mock_file("broker_address.pem", "id1", f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"),
        create_mock_file("certificate.pem", "id2", f"/mqtt_credentials/{TEST_TAG}/certificate.pem"),
        create_mock_file("private_key.pem", "id3", f"/mqtt_credentials/{TEST_TAG}/private_key.pem"),
        create_mock_file("ca_certificate.pem", "id4", f"/mqtt_credentials/{TEST_TAG}/ca_certificate.pem"),
    ]
    mock_list_files.return_value = existing_files

    import pycarta.mqtt.credential as credential
    success = credential.upload_mqtt_credentials(
        file_paths=TEST_FILE_PATHS, 
        tag=TEST_TAG, 
        overwrite=False
    )

    # Since they exist and overwrite=False, we skip
    assert not success
    mock_agent.post.assert_not_called()
    mock_agent.patch.assert_not_called()

def test_upload_mqtt_credentials_file_not_found(mock_agent, mock_list_files):
    """
    Test uploading MQTT credentials when a file path does not exist.
    """
    mock_list_files.return_value = []  # No existing files

    def mock_file_open(file, mode='r', *args, **kwargs):
        # Raise FileNotFoundError for one file
        if file == TEST_FILE_PATHS["broker_address"]:
            raise FileNotFoundError
        else:
            return mock_open(read_data="dummy_content").return_value

    with patch("builtins.open", mock_file_open):
        import pycarta.mqtt.credential as credential
        success = credential.upload_mqtt_credentials(
            file_paths=TEST_FILE_PATHS, 
            tag=TEST_TAG, 
            overwrite=False
        )

    assert not success
    # 3 files posted successfully, 1 triggered FileNotFoundError
    assert mock_agent.post.call_count == len(TEST_FILE_PATHS) - 1
    mock_agent.patch.assert_not_called()

def test_retrieve_mqtt_credentials_success(mock_agent, mock_list_files, mock_get_file, tmp_path):
    """
    Test successful retrieval of MQTT credentials and saving to files.
    """
    existing_files = [
        create_mock_file("broker_address.pem", "id1", f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"),
        create_mock_file("certificate.pem", "id2", f"/mqtt_credentials/{TEST_TAG}/certificate.pem"),
        create_mock_file("private_key.pem", "id3", f"/mqtt_credentials/{TEST_TAG}/private_key.pem"),
        create_mock_file("ca_certificate.pem", "id4", f"/mqtt_credentials/{TEST_TAG}/ca_certificate.pem"),
    ]
    mock_list_files.return_value = existing_files

    def mock_agent_get(url, *args, **kwargs):
        # Return content based on ID
        file_id = url.split('/')[-1]
        if file_id == "id1":
            return Mock(status_code=200, text=TEST_FILE_CONTENT["broker_address"])
        elif file_id == "id2":
            return Mock(status_code=200, text=TEST_FILE_CONTENT["certificate"])
        elif file_id == "id3":
            return Mock(status_code=200, text=TEST_FILE_CONTENT["private_key"])
        elif file_id == "id4":
            return Mock(status_code=200, text=TEST_FILE_CONTENT["ca_certificate"])
        else:
            return Mock(status_code=404, text="Not Found")

    mock_agent.get.side_effect = mock_agent_get

    # Provide a temp directory for storing retrieved files
    file_paths_retrieved = {
        "broker_address": str(tmp_path / "retrieved" / "broker_address.pem"),
        "certificate": str(tmp_path / "retrieved" / "certificate.pem"),
        "private_key": str(tmp_path / "retrieved" / "private_key.pem"),
        "ca_certificate": str(tmp_path / "retrieved" / "ca_certificate.pem")
    }

    import pycarta.mqtt.credential as credential
    credentials = credential.retrieve_mqtt_credentials(
        tag=TEST_TAG, 
        file_paths=file_paths_retrieved
    )

    # The returned credentials should match our test content
    assert credentials == TEST_FILE_CONTENT

    # Also verify the files were actually written
    for file_type, file_path in file_paths_retrieved.items():
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            assert f.read() == TEST_FILE_CONTENT[file_type]

def test_retrieve_mqtt_credentials_missing_file(mock_agent, mock_list_files, mock_get_file):
    """
    Test retrieving MQTT credentials when a file is missing.
    """
    # Missing "certificate.pem"
    existing_files = [
        create_mock_file("broker_address.pem", "id1", f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"),
        create_mock_file("private_key.pem", "id3", f"/mqtt_credentials/{TEST_TAG}/private_key.pem"),
        create_mock_file("ca_certificate.pem", "id4", f"/mqtt_credentials/{TEST_TAG}/ca_certificate.pem"),
    ]
    mock_list_files.return_value = existing_files

    def mock_agent_get(url, *args, **kwargs):
        file_id = url.split('/')[-1]
        if file_id == "id1":
            return Mock(status_code=200, text=TEST_FILE_CONTENT["broker_address"])
        elif file_id == "id3":
            return Mock(status_code=200, text=TEST_FILE_CONTENT["private_key"])
        elif file_id == "id4":
            return Mock(status_code=200, text=TEST_FILE_CONTENT["ca_certificate"])
        else:
            return Mock(status_code=404, text="Not Found")

    mock_agent.get.side_effect = mock_agent_get

    import pycarta.mqtt.credential as credential
    credentials = credential.retrieve_mqtt_credentials(tag=TEST_TAG)
    # Because "certificate" is missing, retrieval should fail
    assert credentials is None

def test_delete_mqtt_credentials_success(mock_agent, mock_list_files):
    """
    Test successful deletion of all MQTT credentials.
    """
    existing_files = [
        create_mock_file("broker_address.pem", "id1", f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"),
        create_mock_file("certificate.pem", "id2", f"/mqtt_credentials/{TEST_TAG}/certificate.pem"),
        create_mock_file("private_key.pem", "id3", f"/mqtt_credentials/{TEST_TAG}/private_key.pem"),
        create_mock_file("ca_certificate.pem", "id4", f"/mqtt_credentials/{TEST_TAG}/ca_certificate.pem"),
    ]
    mock_list_files.return_value = existing_files

    # Mock successful deletion
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_agent.delete.return_value = mock_response

    import pycarta.mqtt.credential as credential
    success = credential.delete_mqtt_credentials(tag=TEST_TAG)

    assert success
    # Each file triggers a delete
    assert mock_agent.delete.call_count == len(TEST_FILE_TYPES)
    for file in existing_files:
        mock_agent.delete.assert_any_call(f"/files/Carta/file/{file.id}")

def test_delete_mqtt_credentials_partial_failure(mock_agent, mock_list_files):
    """
    Test deletion when some deletions fail.
    """
    existing_files = [
        create_mock_file("broker_address.pem", "id1", f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"),
        create_mock_file("certificate.pem", "id2", f"/mqtt_credentials/{TEST_TAG}/certificate.pem"),
    ]
    mock_list_files.return_value = existing_files

    def mock_agent_delete(url, *args, **kwargs):
        # The first deletion is successful, the second fails
        if "id1" in url:
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            return mock_resp
        else:
            mock_resp = Mock()
            mock_resp.raise_for_status.side_effect = Exception("Deletion failed")
            return mock_resp

    mock_agent.delete.side_effect = mock_agent_delete

    import pycarta.mqtt.credential as credential
    success = credential.delete_mqtt_credentials(tag=TEST_TAG)

    # Because one deletion fails, the overall success is False
    assert not success
    assert mock_agent.delete.call_count == len(existing_files)

def test_list_mqtt_credentials_success(mock_agent, mock_list_files):
    """
    Test successful listing of MQTT credentials.
    """
    existing_files = [
        create_mock_file("broker_address.pem", "id1", f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"),
        create_mock_file("certificate.pem", "id2", f"/mqtt_credentials/{TEST_TAG}/certificate.pem"),
    ]
    mock_list_files.return_value = existing_files

    import pycarta.mqtt.credential as credential
    credentials = credential.list_mqtt_credentials(tag=TEST_TAG)

    expected_credentials = {
        "broker_address": {
            "id": "id1",
            "name": "broker_address.pem",
            "path": f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"
        },
        "certificate": {
            "id": "id2",
            "name": "certificate.pem",
            "path": f"/mqtt_credentials/{TEST_TAG}/certificate.pem"
        }
    }
    assert credentials == expected_credentials

def test_list_mqtt_credentials_no_credentials(mock_agent, mock_list_files):
    """
    Test listing MQTT credentials when none exist.
    """
    mock_list_files.return_value = []

    import pycarta.mqtt.credential as credential
    credentials = credential.list_mqtt_credentials(tag=TEST_TAG)

    assert credentials == {}

def test_update_mqtt_credentials_success(mock_agent, mock_list_files):
    """
    Test successful update of MQTT credentials.
    """
    existing_files = [
        create_mock_file("broker_address.pem", "id1", f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"),
        create_mock_file("certificate.pem", "id2", f"/mqtt_credentials/{TEST_TAG}/certificate.pem"),
    ]
    mock_list_files.return_value = existing_files

    # Mock successful patch
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_agent.patch.return_value = mock_response

    new_content = "new_broker_address_content"
    m = mock_open(read_data=new_content)
    with patch("builtins.open", m):
        import pycarta.mqtt.credential as credential
        updates = {"broker_address": new_content}
        success = credential.update_mqtt_credentials(updates=updates, tag=TEST_TAG)

    assert success
    assert mock_agent.patch.call_count == 1
    mock_agent.patch.assert_called_with(
        f"/files/Carta/file/id1",
        files={"file": (f"{credential.MQTT_DIR}/{TEST_TAG}/broker_address.pem", new_content.encode("utf-8"), "application/octet-stream")}
    )

def test_update_mqtt_credentials_failure(mock_agent, mock_list_files):
    """
    Test updating MQTT credentials when an update fails.
    """
    existing_files = [
        create_mock_file("broker_address.pem", "id1", f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"),
    ]
    mock_list_files.return_value = existing_files

    # Mock a failing patch
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("Update failed")
    mock_agent.patch.return_value = mock_response

    new_content = "new_broker_address_content"
    m = mock_open(read_data=new_content)
    with patch("builtins.open", m):
        import pycarta.mqtt.credential as credential
        updates = {"broker_address": new_content}
        success = credential.update_mqtt_credentials(updates=updates, tag=TEST_TAG)

    assert not success
    assert mock_agent.patch.call_count == 1

def test_retrieve_mqtt_credentials_partial_failure(mock_agent, mock_list_files, mock_get_file, tmp_path):
    """
    Test retrieving MQTT credentials when some files fail to download.
    """
    existing_files = [
        create_mock_file("broker_address.pem", "id1", f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"),
        create_mock_file("certificate.pem", "id2", f"/mqtt_credentials/{TEST_TAG}/certificate.pem"),
    ]
    mock_list_files.return_value = existing_files

    def mock_agent_get(url, *args, **kwargs):
        # The second file fails to download
        file_id = url.split('/')[-1]
        if file_id == "id1":
            return Mock(status_code=200, text=TEST_FILE_CONTENT["broker_address"])
        elif file_id == "id2":
            raise Exception("Download failed")

    mock_agent.get.side_effect = mock_agent_get

    import pycarta.mqtt.credential as credential
    credentials = credential.retrieve_mqtt_credentials(tag=TEST_TAG)
    # Because certificate fails, overall retrieval returns None
    assert credentials is None

def test_upload_mqtt_credentials_from_strings_success(mock_agent, mock_list_files):
    """
    Test uploading MQTT credentials from provided strings.
    """
    mock_list_files.return_value = []
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_agent.post.return_value = mock_response

    credentials_dict = {
        "broker_address": "broker_address_content",
        "certificate": "certificate_content",
        "private_key": "private_key_content",
        "ca_certificate": "ca_certificate_content"
    }

    import pycarta.mqtt.credential as credential
    success = credential.upload_mqtt_credentials(
        credentials=credentials_dict,
        tag=TEST_TAG,
        overwrite=False
    )

    assert success
    assert mock_agent.post.call_count == len(credentials_dict)
    mock_agent.patch.assert_not_called()

def test_retrieve_mqtt_credentials_no_save(mock_agent, mock_list_files, mock_get_file):
    """
    Test retrieving MQTT credentials without saving to files.
    """
    # All 4 exist
    existing_files = [
        create_mock_file("broker_address.pem", "id1", f"/mqtt_credentials/{TEST_TAG}/broker_address.pem"),
        create_mock_file("certificate.pem", "id2", f"/mqtt_credentials/{TEST_TAG}/certificate.pem"),
        create_mock_file("private_key.pem", "id3", f"/mqtt_credentials/{TEST_TAG}/private_key.pem"),
        create_mock_file("ca_certificate.pem", "id4", f"/mqtt_credentials/{TEST_TAG}/ca_certificate.pem"),
    ]
    mock_list_files.return_value = existing_files

    # Return content for each file ID
    def mock_agent_get(url, *args, **kwargs):
        file_id = url.split('/')[-1]
        id_to_key = {
            "id1": "broker_address",
            "id2": "certificate",
            "id3": "private_key",
            "id4": "ca_certificate"
        }
        key = id_to_key.get(file_id, "")
        return Mock(status_code=200, text=TEST_FILE_CONTENT.get(key, ""))

    mock_agent.get.side_effect = mock_agent_get

    import pycarta.mqtt.credential as credential
    credentials = credential.retrieve_mqtt_credentials(tag=TEST_TAG)

    expected_credentials = {
        "broker_address": "broker_address_content",
        "certificate": "certificate_content",
        "private_key": "private_key_content",
        "ca_certificate": "ca_certificate_content"
    }
    assert credentials == expected_credentials
