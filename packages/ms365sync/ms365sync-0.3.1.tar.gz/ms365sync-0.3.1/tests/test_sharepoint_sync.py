"""
Tests for SharePointSync functionality.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, cast
from unittest.mock import Mock, patch

import pytest
import requests

from ms365sync import SharePointSync


class TestSharePointSync:
    """Test cases for SharePointSync class."""

    @pytest.fixture(autouse=True)
    def setup_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Set up required environment variables for tests."""
        monkeypatch.setenv("TENANT_ID", "test_tenant_id")
        monkeypatch.setenv("CLIENT_ID", "test_client_id")
        monkeypatch.setenv("CLIENT_SECRET", "test_client_secret")

    @pytest.fixture
    def mock_syncer(self) -> SharePointSync:
        """Create a mock SharePointSync instance for testing."""
        syncer = SharePointSync.__new__(SharePointSync)
        syncer.tenant_id = "test_tenant_id"
        syncer.client_id = "test_client_id"
        syncer.client_secret = "test_client_secret"
        syncer.sharepoint_host = "test.sharepoint.com"
        syncer.site_name = "Test Site"
        syncer.doc_library = "Test Library"
        syncer.site_id = "test_site_id"
        syncer.drive_id = "test_drive_id"
        syncer.headers = {"Authorization": "Bearer test_token"}

        # Set up temporary paths
        temp_dir = Path(tempfile.mkdtemp())
        syncer.local_root = temp_dir / "data"
        syncer.local_root.mkdir(parents=True, exist_ok=True)
        syncer.sync_logs_dir = temp_dir / "logs"
        syncer.sync_logs_dir.mkdir(parents=True, exist_ok=True)
        syncer.permissions_file = temp_dir / ".permissions.json"

        # Setup logging (since we're bypassing __init__)
        syncer._setup_logging()

        return syncer

    # ============ Initialization Tests ============

    @patch("ms365sync.sharepoint_sync.msal.ConfidentialClientApplication")
    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_init_success(self, mock_get: Mock, mock_msal_app: Mock) -> None:
        """Test successful SharePointSync initialization."""
        # Mock MSAL authentication
        mock_app_instance = Mock()
        mock_app_instance.acquire_token_for_client.return_value = {
            "access_token": "test_token"
        }
        mock_msal_app.return_value = mock_app_instance

        # Mock site and drive API calls
        mock_site_response = Mock()
        mock_site_response.json.return_value = {"id": "test_site_id"}
        mock_site_response.raise_for_status = Mock()

        mock_drives_response = Mock()
        mock_drives_response.json.return_value = {
            "value": [{"id": "test_drive_id", "name": "Test Library"}]
        }
        mock_drives_response.raise_for_status = Mock()

        mock_get.side_effect = [mock_site_response, mock_drives_response]

        # Test initialization
        syncer = SharePointSync(
            sharepoint_host="test.sharepoint.com",
            site_name="Test Site",
            doc_library="Test Library",
        )

        assert syncer.site_id == "test_site_id"
        assert syncer.drive_id == "test_drive_id"
        assert "Authorization" in syncer.headers
        assert syncer.headers["Authorization"] == "Bearer test_token"

    def test_init_missing_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test initialization failure with missing credentials."""
        # Remove environment variables
        monkeypatch.delenv("TENANT_ID", raising=False)
        monkeypatch.delenv("CLIENT_ID", raising=False)
        monkeypatch.delenv("CLIENT_SECRET", raising=False)

        with pytest.raises(
            ValueError, match="Missing required authentication parameters"
        ):
            SharePointSync(
                sharepoint_host="test.sharepoint.com",
                site_name="Test Site",
                doc_library="Test Library",
            )

    @patch("ms365sync.sharepoint_sync.msal.ConfidentialClientApplication")
    def test_init_auth_failure(self, mock_msal_app: Mock) -> None:
        """Test initialization failure during authentication."""
        mock_app_instance = Mock()
        mock_app_instance.acquire_token_for_client.return_value = {
            "error": "invalid_client",
            "error_description": "Invalid client credentials",
        }
        mock_msal_app.return_value = mock_app_instance

        with pytest.raises(
            ValueError, match="Authentication failed: Invalid client credentials"
        ):
            SharePointSync(
                sharepoint_host="test.sharepoint.com",
                site_name="Test Site",
                doc_library="Test Library",
            )

    @patch("ms365sync.sharepoint_sync.msal.ConfidentialClientApplication")
    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_init_site_not_found(self, mock_get: Mock, mock_msal_app: Mock) -> None:
        """Test initialization failure when site is not found."""
        # Mock MSAL authentication
        mock_app_instance = Mock()
        mock_app_instance.acquire_token_for_client.return_value = {
            "access_token": "test_token"
        }
        mock_msal_app.return_value = mock_app_instance

        # Mock site API call failure
        mock_get.side_effect = requests.exceptions.RequestException("Site not found")

        with pytest.raises(ValueError, match="API request failed for get site"):
            SharePointSync(
                sharepoint_host="test.sharepoint.com",
                site_name="NonExistent Site",
                doc_library="Test Library",
            )

    @patch("ms365sync.sharepoint_sync.msal.ConfidentialClientApplication")
    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_init_library_not_found(self, mock_get: Mock, mock_msal_app: Mock) -> None:
        """Test initialization failure when document library is not found."""
        # Mock MSAL authentication
        mock_app_instance = Mock()
        mock_app_instance.acquire_token_for_client.return_value = {
            "access_token": "test_token"
        }
        mock_msal_app.return_value = mock_app_instance

        # Mock site and drive API calls
        mock_site_response = Mock()
        mock_site_response.json.return_value = {"id": "test_site_id"}
        mock_site_response.raise_for_status = Mock()

        mock_drives_response = Mock()
        mock_drives_response.json.return_value = {
            "value": [{"id": "other_drive_id", "name": "Other Library"}]
        }
        mock_drives_response.raise_for_status = Mock()

        mock_get.side_effect = [mock_site_response, mock_drives_response]

        with pytest.raises(
            ValueError, match="Document library 'Test Library' not found"
        ):
            SharePointSync(
                sharepoint_host="test.sharepoint.com",
                site_name="Test Site",
                doc_library="Test Library",
            )

    def test_init_with_custom_paths(self) -> None:
        """Test SharePointSync initialization with custom paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            local_root = Path(temp_dir) / "downloads"
            sync_logs_dir = Path(temp_dir) / "logs"

            with patch(
                "ms365sync.sharepoint_sync.msal.ConfidentialClientApplication"
            ) as mock_msal_app, patch(
                "ms365sync.sharepoint_sync.requests.get"
            ) as mock_get:
                # Mock MSAL authentication
                mock_app_instance = Mock()
                mock_app_instance.acquire_token_for_client.return_value = {
                    "access_token": "test_token"
                }
                mock_msal_app.return_value = mock_app_instance

                # Mock site and drive API calls
                mock_site_response = Mock()
                mock_site_response.json.return_value = {"id": "test_site_id"}
                mock_site_response.raise_for_status = Mock()

                mock_drives_response = Mock()
                mock_drives_response.json.return_value = {
                    "value": [{"id": "test_drive_id", "name": "Test Library"}]
                }
                mock_drives_response.raise_for_status = Mock()

                mock_get.side_effect = [mock_site_response, mock_drives_response]

                # Test initialization with custom paths
                syncer = SharePointSync(
                    sharepoint_host="test.sharepoint.com",
                    site_name="Test Site",
                    doc_library="Test Library",
                    local_root=local_root,
                    sync_logs_dir=sync_logs_dir,
                )

                assert syncer.local_root == local_root
                assert syncer.sync_logs_dir == sync_logs_dir
                assert (
                    syncer.permissions_file == local_root.parent / ".permissions.json"
                )

    # ============ File Comparison Tests ============

    def test_compare_files_empty(self, mock_syncer: SharePointSync) -> None:
        """Test file comparison with empty file lists."""
        added, modified, deleted = mock_syncer.compare_files({}, {})

        assert added == []
        assert modified == []
        assert deleted == []

    def test_compare_files_added(self, mock_syncer: SharePointSync) -> None:
        """Test file comparison with added files."""
        sp_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {"size": 1000, "last_modified": "2024-01-01T10:00:00Z"}
        }
        local_files: Dict[str, Dict[str, Any]] = {}

        added, modified, deleted = mock_syncer.compare_files(sp_files, local_files)

        assert added == ["test.pdf"]
        assert modified == []
        assert deleted == []

    def test_compare_files_deleted(self, mock_syncer: SharePointSync) -> None:
        """Test file comparison with deleted files."""
        sp_files: Dict[str, Dict[str, Any]] = {}
        local_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {"size": 1000, "last_modified": "2024-01-01T10:00:00Z"}
        }

        added, modified, deleted = mock_syncer.compare_files(sp_files, local_files)

        assert added == []
        assert modified == []
        assert deleted == ["test.pdf"]

    def test_compare_files_modified_by_size(self, mock_syncer: SharePointSync) -> None:
        """Test file comparison with files modified by size."""
        sp_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {"size": 2000, "last_modified": "2024-01-01T10:00:00Z"}
        }
        local_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {"size": 1000, "last_modified": "2024-01-01T10:00:00Z"}
        }

        added, modified, deleted = mock_syncer.compare_files(sp_files, local_files)

        assert added == []
        assert modified == ["test.pdf"]
        assert deleted == []

    def test_compare_files_modified_by_time(self, mock_syncer: SharePointSync) -> None:
        """Test file comparison with files modified by timestamp."""
        sp_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {"size": 1000, "last_modified": "2024-01-01T11:00:00Z"}
        }
        local_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {"size": 1000, "last_modified": "2024-01-01T10:00:00Z"}
        }

        added, modified, deleted = mock_syncer.compare_files(sp_files, local_files)

        assert added == []
        assert modified == ["test.pdf"]
        assert deleted == []

    def test_compare_files_unchanged(self, mock_syncer: SharePointSync) -> None:
        """Test file comparison with unchanged files."""
        sp_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {"size": 1000, "last_modified": "2024-01-01T10:00:00Z"}
        }
        local_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {"size": 1000, "last_modified": "2024-01-01T10:00:00Z"}
        }

        added, modified, deleted = mock_syncer.compare_files(sp_files, local_files)

        assert added == []
        assert modified == []
        assert deleted == []

    # ============ Permission Comparison Tests ============

    def test_compare_permissions_no_changes(self, mock_syncer: SharePointSync) -> None:
        """Test permission comparison with no changes."""
        sp_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {"permissions": ["Owner:::Full Control", "Team:::Edit"]}
        }
        current_permissions: Dict[str, List[str]] = {
            "test.pdf": ["Owner:::Full Control", "Team:::Edit"]
        }

        changes = mock_syncer.compare_permissions(sp_files, current_permissions)

        assert changes == {}

    def test_compare_permissions_with_changes(
        self, mock_syncer: SharePointSync
    ) -> None:
        """Test permission comparison with changes."""
        sp_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {
                "permissions": ["Owner:::Full Control", "Team:::Edit", "User:::View"]
            }
        }
        current_permissions: Dict[str, List[str]] = {
            "test.pdf": ["Owner:::Full Control", "OldUser:::Edit"]
        }

        changes = mock_syncer.compare_permissions(sp_files, current_permissions)

        assert "test.pdf" in changes
        assert set(changes["test.pdf"]["added"]) == {"Team:::Edit", "User:::View"}
        assert changes["test.pdf"]["removed"] == ["OldUser:::Edit"]
        assert set(changes["test.pdf"]["current"]) == {
            "Owner:::Full Control",
            "Team:::Edit",
            "User:::View",
        }

    def test_compare_permissions_new_file(self, mock_syncer: SharePointSync) -> None:
        """Test permission comparison for new file."""
        sp_files: Dict[str, Dict[str, Any]] = {
            "new.pdf": {"permissions": ["Owner:::Full Control", "Team:::Edit"]}
        }
        current_permissions: Dict[str, List[str]] = {}

        changes = mock_syncer.compare_permissions(sp_files, current_permissions)

        assert "new.pdf" in changes
        assert set(changes["new.pdf"]["added"]) == {
            "Owner:::Full Control",
            "Team:::Edit",
        }
        assert changes["new.pdf"]["removed"] == []

    # ============ Local File Management Tests ============

    def test_get_local_files_empty_directory(self, mock_syncer: SharePointSync) -> None:
        """Test getting local files from empty directory."""
        files = mock_syncer.get_local_files()
        assert files == {}

    def test_get_local_files_with_files(self, mock_syncer: SharePointSync) -> None:
        """Test getting local files from directory with files."""
        # Create test files
        test_file = mock_syncer.local_root / "test.pdf"
        test_file.write_text("test content")

        # Create subdirectory with file
        subdir = mock_syncer.local_root / "subdir"
        subdir.mkdir()
        sub_file = subdir / "sub.pdf"
        sub_file.write_text("sub content")

        files = mock_syncer.get_local_files()

        assert "test.pdf" in files
        assert "subdir/sub.pdf" in files
        assert files["test.pdf"]["size"] == len("test content")
        assert files["subdir/sub.pdf"]["size"] == len("sub content")
        assert "last_modified" in files["test.pdf"]
        assert "last_modified" in files["subdir/sub.pdf"]

    def test_get_local_files_nonexistent_directory(
        self, mock_syncer: SharePointSync
    ) -> None:
        """Test getting local files when directory doesn't exist."""
        # Remove the directory
        import shutil

        shutil.rmtree(mock_syncer.local_root)

        files = mock_syncer.get_local_files()

        assert files == {}
        assert mock_syncer.local_root.exists()  # Should be created

    # ============ Permission Persistence Tests ============

    def test_load_permissions_empty(self, mock_syncer: SharePointSync) -> None:
        """Test loading permissions from non-existent file."""
        permissions = mock_syncer.load_permissions()
        assert permissions == {}

    def test_load_permissions_existing(self, mock_syncer: SharePointSync) -> None:
        """Test loading permissions from existing file."""
        test_permissions = {"test.pdf": ["Owner:::Full Control", "Team:::Edit"]}

        with open(mock_syncer.permissions_file, "w") as f:
            json.dump(test_permissions, f)

        permissions = mock_syncer.load_permissions()
        assert permissions == test_permissions

    def test_load_permissions_invalid_json(self, mock_syncer: SharePointSync) -> None:
        """Test loading permissions from corrupted JSON file."""
        # Write invalid JSON
        with open(mock_syncer.permissions_file, "w") as f:
            f.write("invalid json content")

        permissions = mock_syncer.load_permissions()
        assert permissions == {}

    def test_save_permissions(self, mock_syncer: SharePointSync) -> None:
        """Test saving permissions to file."""
        test_permissions = {"test.pdf": ["Owner:::Full Control", "Team:::Edit"]}

        mock_syncer.save_permissions(test_permissions)

        assert mock_syncer.permissions_file.exists()

        with open(mock_syncer.permissions_file, "r") as f:
            saved_permissions = json.load(f)

        assert saved_permissions == test_permissions

    # ============ File Download Tests ============

    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_download_file_success(
        self, mock_get: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test successful file download."""
        # Mock successful download
        mock_response = Mock()
        mock_response.content = b"test file content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        sp_file = {
            "relative_path": "test.pdf",
            "download_url": "http://example.com/download",
        }

        result = mock_syncer.download_file(sp_file)

        assert result is True
        local_file = mock_syncer.local_root / "test.pdf"
        assert local_file.exists()
        assert local_file.read_bytes() == b"test file content"

    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_download_file_with_subdirectory(
        self, mock_get: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test file download with subdirectory creation."""
        # Mock successful download
        mock_response = Mock()
        mock_response.content = b"test file content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        sp_file = {
            "relative_path": "folder/subfolder/test.pdf",
            "download_url": "http://example.com/download",
        }

        result = mock_syncer.download_file(sp_file)

        assert result is True
        local_file = mock_syncer.local_root / "folder/subfolder/test.pdf"
        assert local_file.exists()
        assert local_file.read_bytes() == b"test file content"

    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_download_file_failure(
        self, mock_get: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test file download failure."""
        # Mock download failure
        mock_get.side_effect = requests.exceptions.RequestException("Download failed")

        sp_file = {
            "relative_path": "test.pdf",
            "download_url": "http://example.com/download",
        }

        result = mock_syncer.download_file(sp_file)

        assert result is False
        local_file = mock_syncer.local_root / "test.pdf"
        assert not local_file.exists()

    # ============ SharePoint API Tests ============

    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_get_file_permissions_success(
        self, mock_get: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test successful file permissions retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": [
                {
                    "roles": ["owner"],
                    "grantedTo": {"user": {"displayName": "John Doe"}},
                },
                {
                    "roles": ["write"],
                    "grantedTo": {"user": {"displayName": "Jane Smith"}},
                },
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        permissions = mock_syncer.get_file_permissions("test_item_id")

        assert "John Doe:::Full Control" in permissions
        assert "Jane Smith:::Edit" in permissions

    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_get_file_permissions_with_groups(
        self, mock_get: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test file permissions retrieval with groups."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": [
                {
                    "roles": ["read"],
                    "grantedToIdentities": [
                        {"group": {"displayName": "Marketing Team"}},
                        {"user": {"displayName": "John Doe"}},
                    ],
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        permissions = mock_syncer.get_file_permissions("test_item_id")

        assert "Marketing Team:::View" in permissions
        assert "John Doe:::View" in permissions

    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_get_file_permissions_failure(
        self, mock_get: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test file permissions retrieval failure."""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        permissions = mock_syncer.get_file_permissions("test_item_id")

        assert permissions == []

    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_get_sharepoint_files_success(
        self, mock_get: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test successful SharePoint files retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": [
                {
                    "id": "file1",
                    "name": "test.pdf",
                    "size": 1000,
                    "lastModifiedDateTime": "2024-01-01T10:00:00Z",
                    "@microsoft.graph.downloadUrl": "http://example.com/download",
                    "file": {},
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock get_file_permissions
        setattr(
            mock_syncer,
            "get_file_permissions",
            Mock(return_value=["Owner:::Full Control"]),
        )

        files = mock_syncer.get_sharepoint_files()

        assert "test.pdf" in files
        assert files["test.pdf"]["id"] == "file1"
        assert files["test.pdf"]["size"] == 1000
        assert files["test.pdf"]["permissions"] == ["Owner:::Full Control"]

    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_get_sharepoint_files_with_folders(
        self, mock_get: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test SharePoint files retrieval with recursive folder processing."""
        # Mock root folder response
        root_response = Mock()
        root_response.json.return_value = {
            "value": [
                {"id": "folder1", "name": "subfolder", "folder": {}},
                {
                    "id": "file1",
                    "name": "root.pdf",
                    "size": 1000,
                    "lastModifiedDateTime": "2024-01-01T10:00:00Z",
                    "@microsoft.graph.downloadUrl": "http://example.com/download1",
                    "file": {},
                },
            ]
        }
        root_response.raise_for_status = Mock()

        # Mock subfolder response
        subfolder_response = Mock()
        subfolder_response.json.return_value = {
            "value": [
                {
                    "id": "file2",
                    "name": "sub.pdf",
                    "size": 2000,
                    "lastModifiedDateTime": "2024-01-01T11:00:00Z",
                    "@microsoft.graph.downloadUrl": "http://example.com/download2",
                    "file": {},
                }
            ]
        }
        subfolder_response.raise_for_status = Mock()

        mock_get.side_effect = [root_response, subfolder_response]

        # Mock get_file_permissions
        setattr(
            mock_syncer,
            "get_file_permissions",
            Mock(return_value=["Owner:::Full Control"]),
        )

        files = mock_syncer.get_sharepoint_files()

        assert "root.pdf" in files
        assert "subfolder/sub.pdf" in files
        assert files["root.pdf"]["size"] == 1000
        assert files["subfolder/sub.pdf"]["size"] == 2000

    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_get_sharepoint_files_failure(
        self, mock_get: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test SharePoint files retrieval failure."""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        files = mock_syncer.get_sharepoint_files()

        assert files == {}

    # ============ Full Sync Integration Tests ============

    @patch("ms365sync.sharepoint_sync.print_file_tree")
    def test_sync_with_added_files(
        self, mock_print_tree: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test sync with added files generates correct changes."""
        # Mock the methods
        setattr(
            mock_syncer,
            "get_sharepoint_files",
            Mock(
                return_value={
                    "new_file.pdf": {
                        "id": "file1",
                        "name": "new_file.pdf",
                        "size": 1000,
                        "last_modified": "2024-01-01T10:00:00Z",
                        "download_url": "http://example.com/download",
                        "relative_path": "new_file.pdf",
                        "permissions": ["Owner:::Full Control", "Team:::Edit"],
                    }
                }
            ),
        )

        setattr(mock_syncer, "get_local_files", Mock(return_value={}))
        setattr(mock_syncer, "download_file", Mock(return_value=True))

        # Run sync
        result = mock_syncer.sync()

        # Check the results
        assert isinstance(result["added"], list)
        assert "new_file.pdf" in result["added"]
        assert result["total_files"] == 1

        # Check that rag_changes contains proper structure
        rag_changes = cast(Dict[str, Any], result["rag_changes"])
        assert "new_file.pdf" in rag_changes["added"]
        assert rag_changes["added"]["new_file.pdf"]["permissions"] == [
            "Owner:::Full Control",
            "Team:::Edit",
        ]

        # Verify changes file was created
        assert "changes_file" in result
        changes_file = Path(cast(str, result["changes_file"]))
        assert changes_file.exists()

    @patch("ms365sync.sharepoint_sync.print_file_tree")
    def test_sync_with_deleted_files(
        self, mock_print_tree: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test sync with deleted files."""
        # Set up existing permissions
        existing_permissions = {
            "deleted_file.pdf": ["Owner:::Full Control", "Team:::Edit"]
        }
        mock_syncer.save_permissions(existing_permissions)

        # Mock no files in SharePoint
        setattr(mock_syncer, "get_sharepoint_files", Mock(return_value={}))

        # Mock local files (file exists locally but not in SharePoint)
        deleted_file = mock_syncer.local_root / "deleted_file.pdf"
        deleted_file.write_text("test content")

        setattr(
            mock_syncer,
            "get_local_files",
            Mock(
                return_value={
                    "deleted_file.pdf": {
                        "size": 100,
                        "last_modified": "2024-01-01T10:00:00Z",
                        "local_path": deleted_file,
                    }
                }
            ),
        )

        # Run sync
        result = mock_syncer.sync()

        # Check deletion
        assert "deleted_file.pdf" in cast(List[str], result["deleted"])

        rag_changes = cast(Dict[str, Any], result["rag_changes"])
        assert "deleted_file.pdf" in rag_changes["deleted"]
        assert rag_changes["deleted"]["deleted_file.pdf"]["permissions"] == [
            "Owner:::Full Control",
            "Team:::Edit",
        ]

        # Check that file was actually deleted
        assert not deleted_file.exists()

    @patch("ms365sync.sharepoint_sync.print_file_tree")
    def test_sync_with_permission_changes_only(
        self, mock_print_tree: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test sync with permission-only changes."""
        # Set up existing permissions
        existing_permissions = {
            "existing_file.pdf": ["Owner:::Full Control", "OldUser:::Edit"]
        }
        mock_syncer.save_permissions(existing_permissions)

        # Mock SharePoint files with updated permissions
        setattr(
            mock_syncer,
            "get_sharepoint_files",
            Mock(
                return_value={
                    "existing_file.pdf": {
                        "id": "file1",
                        "name": "existing_file.pdf",
                        "size": 1000,
                        "last_modified": "2024-01-01T10:00:00Z",
                        "download_url": "http://example.com/download",
                        "relative_path": "existing_file.pdf",
                        "permissions": ["Owner:::Full Control", "NewUser:::View"],
                    }
                }
            ),
        )

        # Mock local files (same file exists locally)
        setattr(
            mock_syncer,
            "get_local_files",
            Mock(
                return_value={
                    "existing_file.pdf": {
                        "size": 1000,
                        "last_modified": "2024-01-01T10:00:00Z",
                        "local_path": mock_syncer.local_root / "existing_file.pdf",
                    }
                }
            ),
        )

        # Run sync
        result = mock_syncer.sync()

        # Check permission changes
        rag_changes = cast(Dict[str, Any], result["rag_changes"])
        assert "existing_file.pdf" in rag_changes["permission_only_changes"]

        perm_change = rag_changes["permission_only_changes"]["existing_file.pdf"][
            "permission_changes"
        ]
        assert "NewUser:::View" in perm_change["added"]
        assert "OldUser:::Edit" in perm_change["removed"]
        assert set(perm_change["current"]) == {"Owner:::Full Control", "NewUser:::View"}

    @patch("ms365sync.sharepoint_sync.print_file_tree")
    def test_sync_changes_file_format(
        self, mock_print_tree: Mock, mock_syncer: SharePointSync
    ) -> None:
        """Test that sync changes file has correct format."""
        # Simple sync setup
        setattr(
            mock_syncer,
            "get_sharepoint_files",
            Mock(
                return_value={
                    "test_file.pdf": {
                        "id": "file1",
                        "name": "test_file.pdf",
                        "size": 1000,
                        "last_modified": "2024-01-01T10:00:00Z",
                        "download_url": "http://example.com/download",
                        "relative_path": "test_file.pdf",
                        "permissions": ["Owner:::Full Control"],
                    }
                }
            ),
        )

        setattr(mock_syncer, "get_local_files", Mock(return_value={}))
        setattr(mock_syncer, "download_file", Mock(return_value=True))

        # Run sync
        result = mock_syncer.sync()

        # Check that changes file was created
        changes_file = Path(cast(str, result["changes_file"]))
        assert changes_file.exists()

        # Load and verify the changes file content
        with open(changes_file, "r") as f:
            data = json.load(f)

        assert "timestamp" in data
        assert "summary" in data
        assert "changes" in data

        # Check summary
        summary = data["summary"]
        assert summary["total_files"] == 1
        assert summary["added_count"] == 1
        assert summary["modified_count"] == 0
        assert summary["deleted_count"] == 0
        assert summary["permission_only_changes_count"] == 0

        # Check changes structure
        changes = data["changes"]
        assert "added" in changes
        assert "modified" in changes
        assert "deleted" in changes
        assert "permission_only_changes" in changes

        # Check added file details
        assert "test_file.pdf" in changes["added"]
        added_file = changes["added"]["test_file.pdf"]
        assert added_file["permissions"] == ["Owner:::Full Control"]
        assert "file_path" in added_file
