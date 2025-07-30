import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

import msal
import requests
from dotenv import load_dotenv

from .utils import print_file_tree

load_dotenv()

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"
SCOPE = ["https://graph.microsoft.com/.default"]


class SharePointSync:
    def __init__(
        self,
        sharepoint_host: str,
        site_name: str,
        doc_library: str,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        local_root: Path = Path("ms365_data/data"),
        sync_logs_dir: Path = Path("sync_logs"),
    ):
        """
        Initialize SharePoint sync client.

        Args:
            sharepoint_host: SharePoint hostname (e.g., yourcompany.sharepoint.com)
            site_name: SharePoint site display name
            doc_library: Document library display name
            tenant_id: Azure tenant ID (defaults to TENANT_ID env var)
            client_id: Azure client ID (defaults to CLIENT_ID env var)
            client_secret: Azure client secret (defaults to CLIENT_SECRET env var)
            local_root: Local directory path (defaults to "ms365_data/data")
            sync_logs_dir: Directory for sync logs (defaults to "sync_logs")
        """
        # Configuration with fallbacks to environment variables or defaults
        self.tenant_id = tenant_id or os.environ.get("TENANT_ID")
        self.client_id = client_id or os.environ.get("CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("CLIENT_SECRET")

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError(
                "Missing required authentication parameters. "
                "Provide tenant_id, client_id, and client_secret, "
                "or set TENANT_ID, CLIENT_ID, and CLIENT_SECRET "
                "environment variables."
            )

        self.sharepoint_host = sharepoint_host
        self.site_name = site_name
        self.doc_library = doc_library

        self.local_root = local_root
        self.sync_logs_dir = sync_logs_dir
        self.permissions_file = self.local_root.parent / ".permissions.json"

        self._setup_logging()
        self.setup_auth()
        self.setup_site()

    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _make_api_request(self, url: str, operation_name: str) -> Dict[str, Any]:
        """Make API request with consistent error handling"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to {operation_name}: {e}")
            raise ValueError(f"API request failed for {operation_name}: {e}")

    def setup_auth(self) -> None:
        """Initialize authentication"""
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret,
        )

        token = app.acquire_token_for_client(scopes=SCOPE)
        if "access_token" not in token:
            error_desc = token.get("error_description", "Unknown error")
            raise ValueError(f"Authentication failed: {error_desc}")

        self.headers = {"Authorization": f"Bearer {token['access_token']}"}

    def setup_site(self) -> None:
        """Get site and drive IDs"""
        try:
            site_url = (
                f"{GRAPH_ROOT}/sites/{self.sharepoint_host}:/sites/{self.site_name}"
            )
            site_data = self._make_api_request(site_url, f"get site '{self.site_name}'")
            self.site_id = site_data["id"]

            drives_url = f"{GRAPH_ROOT}/sites/{self.site_id}/drives"
            drives_data = self._make_api_request(drives_url, "get drives")
            drives_list = drives_data["value"]

            self.drive_id = next(
                (d["id"] for d in drives_list if d["name"] == self.doc_library), None
            )

            if not self.drive_id:
                available_drives = [d["name"] for d in drives_list]
                raise ValueError(
                    f"Document library '{self.doc_library}' not found. "
                    f"Available drives: {available_drives}"
                )

        except ValueError:
            # Re-raise ValueError (from _make_api_request or drive not found)
            raise
        except Exception as e:
            raise ValueError(f"Failed to connect to SharePoint: {e}")

    def get_file_permissions(self, item_id: str) -> List[str]:
        """Get simplified permissions for a specific file"""
        try:
            url = f"{GRAPH_ROOT}/drives/{self.drive_id}/items/{item_id}/permissions"
            response_data = self._make_api_request(
                url, f"get permissions for item {item_id}"
            )

            permissions = []
            seen_permissions = set()  # To avoid duplicates

            for perm in response_data.get("value", []):
                # Map roles to user-friendly permission levels
                roles = perm.get("roles", [])
                if "owner" in roles:
                    permission_level = "Full Control"
                elif "write" in roles:
                    permission_level = "Edit"
                elif "read" in roles:
                    permission_level = "View"
                else:
                    permission_level = "Unknown"

                # Get display name
                display_name = None

                if "grantedTo" in perm:
                    display_name = perm["grantedTo"]["user"].get(
                        "displayName", "Unknown User"
                    )
                elif "grantedToIdentities" in perm:
                    # Handle multiple identities
                    for identity in perm["grantedToIdentities"]:
                        if "user" in identity:
                            name = identity["user"].get("displayName", "Unknown User")
                            perm_string = f"{name}:::{permission_level}"
                            if perm_string not in seen_permissions:
                                permissions.append(perm_string)
                                seen_permissions.add(perm_string)
                        elif "group" in identity:
                            name = identity["group"].get("displayName", "Unknown Group")
                            perm_string = f"{name}:::{permission_level}"
                            if perm_string not in seen_permissions:
                                permissions.append(perm_string)
                                seen_permissions.add(perm_string)
                    continue  # Skip to next permission since we handled this one
                elif "link" in perm:
                    # Handle sharing links
                    link_type = perm["link"].get("type", "unknown")
                    link_scope = perm["link"].get("scope", "unknown")
                    display_name = f"Sharing Link ({link_type}, {link_scope})"

                if display_name:
                    perm_string = f"{display_name}:::{permission_level}"
                    if perm_string not in seen_permissions:
                        permissions.append(perm_string)
                        seen_permissions.add(perm_string)

            return permissions
        except ValueError:
            # This will be logged by _make_api_request
            return []
        except Exception as e:
            self.logger.error(
                f"Unexpected error fetching permissions for item {item_id}: {e}"
            )
            return []

    def get_sharepoint_files(self, folder_path: str = "") -> Dict[str, dict]:
        """Recursively get all files from SharePoint with permissions"""
        files: Dict[str, dict] = {}

        # Get items in current folder
        url = f"{GRAPH_ROOT}/drives/{self.drive_id}/root"
        if folder_path:
            url += f":/{folder_path}:"
        url += "/children"

        try:
            items_data = self._make_api_request(
                url, f"get SharePoint files in folder '{folder_path or 'root'}'"
            )
            items = items_data.get("value", [])

            for item in items:
                if "folder" in item:
                    # Recursively process subfolders
                    subfolder_path = (
                        f"{folder_path}/{item['name']}" if folder_path else item["name"]
                    )
                    files.update(self.get_sharepoint_files(subfolder_path))
                elif "file" in item:
                    # Store file metadata
                    relative_path = (
                        f"{folder_path}/{item['name']}" if folder_path else item["name"]
                    )
                    files[relative_path] = {
                        "id": item["id"],
                        "name": item["name"],
                        "size": item["size"],
                        "last_modified": item["lastModifiedDateTime"],
                        "download_url": item.get("@microsoft.graph.downloadUrl"),
                        "relative_path": relative_path,
                        "permissions": self.get_file_permissions(item["id"]),
                    }
        except ValueError:
            # This will be logged by _make_api_request
            pass
        except Exception as e:
            self.logger.error(f"Unexpected error fetching SharePoint files: {e}")

        return files

    def get_local_files(self) -> Dict[str, dict]:
        """Get all local files with their metadata"""
        files: Dict[str, dict] = {}

        if not self.local_root.exists():
            self.local_root.mkdir(parents=True, exist_ok=True)
            return files

        for file_path in self.local_root.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(self.local_root)).replace(
                    os.sep, "/"
                )
                stat = file_path.stat()
                files[relative_path] = {
                    "size": stat.st_size,
                    "last_modified": (
                        datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z"
                    ),
                    "local_path": file_path,
                }

        return files

    def download_file(self, sp_file: dict) -> bool:
        """Download a file from SharePoint"""
        try:
            local_path = self.local_root / sp_file["relative_path"]
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            response = requests.get(sp_file["download_url"])
            response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(response.content)

            self.logger.info(f"Downloaded: {sp_file['relative_path']}")
            return True

        except Exception as e:
            self.logger.error(f"Error downloading {sp_file['relative_path']}: {e}")
            return False

    def compare_files(
        self, sp_files: Dict[str, dict], local_files: Dict[str, dict]
    ) -> Tuple[List[str], List[str], List[str]]:
        """Compare SharePoint and local files to detect changes"""
        added = []
        modified = []
        deleted = []

        # Find added and modified files
        for rel_path, sp_file in sp_files.items():
            if rel_path not in local_files:
                added.append(rel_path)
            else:
                local_file = local_files[rel_path]
                # Compare by size and last modified date
                sp_modified = datetime.fromisoformat(
                    sp_file["last_modified"].replace("Z", "+00:00")
                )
                local_modified = datetime.fromisoformat(
                    local_file["last_modified"].replace("Z", "+00:00")
                )

                if (
                    sp_file["size"] != local_file["size"]
                    or sp_modified > local_modified
                ):
                    modified.append(rel_path)

        # Find deleted files
        for rel_path in local_files:
            if rel_path not in sp_files:
                deleted.append(rel_path)

        return added, modified, deleted

    def compare_permissions(
        self, sp_files: Dict[str, dict], current_permissions: Dict[str, List[str]]
    ) -> Dict[str, Dict[str, List[str]]]:
        """Compare SharePoint permissions with stored permissions to detect changes"""
        permission_changes = {}

        for rel_path, sp_file in sp_files.items():
            sp_perms = set(sp_file["permissions"])
            stored_perms = set(current_permissions.get(rel_path, []))

            # Calculate added and removed permissions
            added_perms = list(sp_perms - stored_perms)
            removed_perms = list(stored_perms - sp_perms)

            # If there are any changes, record them
            if added_perms or removed_perms:
                permission_changes[rel_path] = {
                    "added": added_perms,
                    "removed": removed_perms,
                    "current": sp_file["permissions"],
                }

        return permission_changes

    def load_permissions(self) -> Dict[str, List[str]]:
        """Load existing permissions from JSON file"""
        if self.permissions_file.exists():
            try:
                with open(self.permissions_file, "r") as f:
                    return json.load(f)  # type: ignore[no-any-return]
            except json.JSONDecodeError:
                self.logger.warning("Error reading permissions file, starting fresh")
        return {}

    def save_permissions(self, permissions: Dict[str, List[str]]) -> None:
        """Save permissions to JSON file"""
        # Ensure ms365_data directory exists
        self.permissions_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.permissions_file, "w") as f:
            json.dump(permissions, f, indent=2)

    def sync(self) -> Dict[str, Union[List[str], int, str, Dict[str, Any]]]:
        """Main sync function - returns changes for RAG database updates"""
        self.logger.info("Starting SharePoint sync...")

        # Get file lists
        self.logger.info("Fetching SharePoint files...")
        sp_files = self.get_sharepoint_files()
        self.logger.info(f"Found {len(sp_files)} files in SharePoint")

        self.logger.info("Scanning local files...")
        local_files = self.get_local_files()
        self.logger.info(f"Found {len(local_files)} local files")

        # Print tree structures for debugging
        self.logger.debug("Printing file trees...")
        print_file_tree(sp_files, "SHAREPOINT FILE TREE")
        print_file_tree(local_files, "LOCAL FILE TREE")

        # Compare and detect changes
        added, modified, deleted = self.compare_files(sp_files, local_files)

        # Load existing permissions and check for permission changes
        permissions = self.load_permissions()
        permission_changes = self.compare_permissions(sp_files, permissions)

        self.logger.info("Changes detected:")
        self.logger.info(f"  Added: {len(added)}")
        self.logger.info(f"  Modified: {len(modified)}")
        self.logger.info(f"  Deleted: {len(deleted)}")
        self.logger.info(f"  Permission changes: {len(permission_changes)}")

        # Prepare detailed change information for RAG database
        rag_changes: Dict[str, Dict[str, Any]] = {
            "added": {},
            "modified": {},
            "deleted": {},
            "permission_only_changes": {},
        }

        # Process added files
        for rel_path in added:
            self.download_file(sp_files[rel_path])
            # Update permissions for this file
            permissions[rel_path] = sp_files[rel_path]["permissions"]
            # For added files, all permissions are new
            rag_changes["added"][rel_path] = {
                "permissions": sp_files[rel_path]["permissions"],
                "file_path": str(self.local_root / rel_path),
            }

        # Process modified files
        for rel_path in modified:
            self.download_file(sp_files[rel_path])
            # Update permissions for this file
            permissions[rel_path] = sp_files[rel_path]["permissions"]
            # Check if permissions also changed
            perm_info = permission_changes.get(rel_path)
            rag_changes["modified"][rel_path] = {
                "content_changed": True,
                "permissions_changed": perm_info is not None,
                "file_path": str(self.local_root / rel_path),
            }
            if perm_info:
                rag_changes["modified"][rel_path]["permission_changes"] = perm_info

        # Process permission-only changes
        for rel_path, perm_info in permission_changes.items():
            if rel_path not in added and rel_path not in modified:
                self.logger.info(f"Permission updated: {rel_path}")
                permissions[rel_path] = sp_files[rel_path]["permissions"]
                rag_changes["permission_only_changes"][rel_path] = {
                    "permission_changes": perm_info,
                    "file_path": str(self.local_root / rel_path),
                }

        # Process deleted files
        for rel_path in deleted:
            local_path = self.local_root / rel_path
            # Store permissions before deletion for RAG update
            deleted_permissions = permissions.get(rel_path, [])

            if local_path.exists():
                local_path.unlink()
                self.logger.info(f"Deleted: {rel_path}")

                # Remove empty directories
                parent = local_path.parent
                while parent != self.local_root and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent

            # Remove permissions for deleted files
            if rel_path in permissions:
                del permissions[rel_path]

            # Record deletion with permissions for RAG
            rag_changes["deleted"][rel_path] = {"permissions": deleted_permissions}

        # Save updated permissions
        self.save_permissions(permissions)
        self.logger.info(f"Permissions saved to: {self.permissions_file}")

        self.logger.info("Sync completed successfully!")

        # Create sync_logs directory outside download folder
        sync_logs_dir = self.sync_logs_dir
        sync_logs_dir.mkdir(exist_ok=True)

        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        changes_file = sync_logs_dir / f"sync_changes_{timestamp}.json"

        # Save comprehensive changes for RAG database updates
        rag_sync_data = {
            "timestamp": timestamp,
            "summary": {
                "total_files": len(sp_files),
                "added_count": len(added),
                "modified_count": len(modified),
                "deleted_count": len(deleted),
                "permission_only_changes_count": len(
                    rag_changes["permission_only_changes"]
                ),
            },
            "changes": rag_changes,
        }

        with open(changes_file, "w") as f:
            json.dump(rag_sync_data, f, indent=2)

        self.logger.info(f"Changes saved to: {changes_file}")

        # Return summary for backward compatibility
        return {
            "added": added,
            "modified": modified,
            "deleted": deleted,
            "permission_changed": list(permission_changes.keys()),
            "total_files": len(sp_files),
            "changes_file": str(changes_file),
            "rag_changes": rag_changes,
        }
