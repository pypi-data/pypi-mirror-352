"""
Command-line interface for MS365Sync.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .sharepoint_sync import SharePointSync


def main(args: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sync files between Microsoft 365 SharePoint and local storage"
    )

    # SharePoint configuration
    parser.add_argument(
        "--sharepoint-host",
        type=str,
        required=True,
        help="SharePoint hostname (e.g., yourcompany.sharepoint.com)",
    )

    parser.add_argument(
        "--site-name",
        type=str,
        required=True,
        help="SharePoint site display name",
    )

    parser.add_argument(
        "--doc-library",
        type=str,
        required=True,
        help="Document library display name",
    )

    # Authentication parameters (optional, can use env vars)
    parser.add_argument(
        "--tenant-id",
        type=str,
        help="Azure tenant ID (defaults to TENANT_ID env var)",
    )

    parser.add_argument(
        "--client-id",
        type=str,
        help="Azure client ID (defaults to CLIENT_ID env var)",
    )

    parser.add_argument(
        "--client-secret",
        type=str,
        help="Azure client secret (defaults to CLIENT_SECRET env var)",
    )

    # File system configuration
    parser.add_argument(
        "--local-root",
        type=Path,
        help="Local directory for downloaded files (default: ms365_data/data)",
    )

    parser.add_argument(
        "--sync-logs-dir",
        type=Path,
        help="Directory for sync log files (default: sync_logs)",
    )

    # Other options
    parser.add_argument(
        "--config",
        type=str,
        help="Path to .env configuration file (default: .env in current directory)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without actually downloading/deleting files",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="ms365sync {}".format(__import__("ms365sync").__version__),
    )

    parsed_args = parser.parse_args(args)

    try:
        # Set up environment if config file is specified
        if parsed_args.config:
            config_path = Path(parsed_args.config)
            if not config_path.exists():
                print(
                    f"Error: Configuration file {config_path} not found",
                    file=sys.stderr,
                )
                return 1

        # Initialize and run sync
        if parsed_args.verbose:
            print("Initializing SharePoint sync...")

        syncer = SharePointSync(
            sharepoint_host=parsed_args.sharepoint_host,
            site_name=parsed_args.site_name,
            doc_library=parsed_args.doc_library,
            tenant_id=parsed_args.tenant_id,
            client_id=parsed_args.client_id,
            client_secret=parsed_args.client_secret,
            local_root=parsed_args.local_root or Path("ms365_data/data"),
            sync_logs_dir=parsed_args.sync_logs_dir or Path("sync_logs"),
        )

        if parsed_args.dry_run:
            print("DRY RUN MODE: No files will be actually modified")
            # TODO: Implement dry-run functionality
            print("Dry-run mode not yet implemented")
            return 0

        changes = syncer.sync()

        if changes:
            print("\nSync completed successfully!")
            print("Total files synced: {}".format(changes.get("total_files", 0)))
            if changes.get("added"):
                added = changes["added"]
                if isinstance(added, list):
                    print(f"Files added: {len(added)}")
                    if parsed_args.verbose and added:
                        print("  Added files:")
                        for file_path in added[:5]:  # Show first 5
                            print(f"    - {file_path}")
                        if len(added) > 5:
                            print(f"    ... and {len(added) - 5} more")
            if changes.get("modified"):
                modified = changes["modified"]
                if isinstance(modified, list):
                    print(f"Files modified: {len(modified)}")
                    if parsed_args.verbose and modified:
                        print("  Modified files:")
                        for file_path in modified[:5]:  # Show first 5
                            print(f"    - {file_path}")
                        if len(modified) > 5:
                            print(f"    ... and {len(modified) - 5} more")
            if changes.get("deleted"):
                deleted = changes["deleted"]
                if isinstance(deleted, list):
                    print(f"Files deleted: {len(deleted)}")
                    if parsed_args.verbose and deleted:
                        print("  Deleted files:")
                        for file_path in deleted[:5]:  # Show first 5
                            print(f"    - {file_path}")
                        if len(deleted) > 5:
                            print(f"    ... and {len(deleted) - 5} more")
            if changes.get("permission_changed"):
                permission_changed = changes["permission_changed"]
                if isinstance(permission_changed, list):
                    print(f"Permission changes: {len(permission_changed)}")
                    if parsed_args.verbose and permission_changed:
                        print("  Files with permission changes:")
                        for file_path in permission_changed[:5]:  # Show first 5
                            print(f"    - {file_path}")
                        if len(permission_changed) > 5:
                            print(f"    ... and {len(permission_changed) - 5} more")

            # Show permissions file info
            permissions_file = Path("ms365_data/.permissions.json")
            if permissions_file.exists():
                print(f"\nPermissions tracking: {permissions_file}")
                if parsed_args.verbose:
                    import json

                    try:
                        with open(permissions_file, "r") as f:
                            permissions = json.load(f)
                        print(
                            f"  Total files with permissions tracked: {len(permissions)}"
                        )
                    except (json.JSONDecodeError, OSError):
                        print("  Could not read permissions file")
        else:
            print("Sync failed")
            return 1

        return 0

    except KeyboardInterrupt:
        print("\nSync interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if parsed_args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
