# MS365Sync

A Python library for syncing files between Microsoft 365 SharePoint and local storage.

## Features

- 🔄 **Two-way sync detection**: Automatically detects added, modified, and deleted files
- 📁 **Hierarchical support**: Maintains folder structures during sync
- 🔐 **OAuth2 authentication**: Secure authentication using Microsoft Graph API
- 🔓 **Permissions tracking**: Maintains a `.permissions.json` file with file-level permissions
- 📊 **Detailed logging**: Comprehensive sync reports and file trees
- 🚀 **CLI and library**: Use as a command-line tool or import as a Python library
- ⚡ **Efficient**: Only downloads changed files to minimize bandwidth usage

## Installation

### From PyPI (when published)

```bash
pip install ms365sync
```

### From source

```bash
git clone https://github.com/yourusername/ms365sync.git
cd ms365sync
pip install -e .
```

### Development installation

```bash
git clone https://github.com/yourusername/ms365sync.git
cd ms365sync
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in your project directory with the following variables:

```env
TENANT_ID=your-azure-tenant-id
CLIENT_ID=your-azure-app-client-id
CLIENT_SECRET=your-azure-app-client-secret
```

### Azure App Registration

1. Go to the [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Set application type to "Web"
5. Under "API permissions", add:
   - `Sites.Read.All` (to read SharePoint sites)
   - `Files.Read.All` (to read files)
   - `Files.ReadWrite.All` (if you need write access)
6. Generate a client secret under "Certificates & secrets"
7. Copy the Application (client) ID, Directory (tenant) ID, and client secret

## Usage

### Command Line Interface

```bash
# Basic sync
ms365sync

# Verbose output
ms365sync --verbose

# Dry run (see what would be synced)
ms365sync --dry-run

# Use custom config file
ms365sync --config /path/to/your/.env
```

### Python Library

```python
from ms365sync import SharePointSync

# Initialize the sync client
syncer = SharePointSync()

# Perform sync and get changes
changes = syncer.sync()

print(f"Added: {len(changes['added'])} files")
print(f"Modified: {len(changes['modified'])} files")
print(f"Deleted: {len(changes['deleted'])} files")
```

### Advanced Usage

```python
from ms365sync import SharePointSync
import os

# Custom configuration
os.environ['TENANT_ID'] = 'your-tenant-id'
os.environ['CLIENT_ID'] = 'your-client-id'
os.environ['CLIENT_SECRET'] = 'your-client-secret'

syncer = SharePointSync()

# Get SharePoint files without syncing
sp_files = syncer.get_sharepoint_files()
print(f"Found {len(sp_files)} files in SharePoint")

# Get local files
local_files = syncer.get_local_files()
print(f"Found {len(local_files)} local files")

# Compare without syncing
added, modified, deleted = syncer.compare_files(sp_files, local_files)
print(f"Would add: {len(added)}, modify: {len(modified)}, delete: {len(deleted)}")
```

## Configuration Options

The library uses the following configuration variables (set in `.env` or environment):

| Variable | Description | Required |
|----------|-------------|----------|
| `TENANT_ID` | Azure Active Directory tenant ID | Yes |
| `CLIENT_ID` | Azure app registration client ID | Yes |
| `CLIENT_SECRET` | Azure app registration client secret | Yes |

The following constants can be modified in the code:

```python
SHAREPOINT_HOST = "your-sharepoint-site.sharepoint.com"
SITE_NAME = "Your Site Name"  # Display name as seen in SharePoint
DOC_LIBRARY = "Your Document Library"  # Display name
LOCAL_ROOT = pathlib.Path("ms365_data/data")  # Local destination folder
```

## File Structure

```
ms365sync/
├── __init__.py          # Package initialization
├── sharepoint_sync.py   # Main sync logic
└── cli.py              # Command-line interface

ms365_data/             # Data folder (in .gitignore)
├── data/               # Downloaded files from SharePoint
└── .permissions.json   # File permissions tracking

sync_logs/              # Sync change logs (JSON)
```

## Permissions Tracking

The library automatically tracks permissions for all synced files in a `.permissions.json` file located in the `ms365_data` directory. This file:

- Contains file paths as keys and permission lists as values
- Updates automatically when files are added, modified, or deleted
- Stores permissions in a simple format: "Display Name:::Permission Level"
- Permission levels include: Full Control, Edit, View

Example `.permissions.json` structure:
```json
{
  "Documents/Report.pdf": [
    "Phi Chat Test Site Owners:::Full Control",
    "AI Team:::Edit",
    "Phi Chat Test Site Visitors:::View"
  ],
  "Projects/Presentation.pptx": [
    "Project Managers:::Full Control",
    "Team Members:::Edit",
    "Sharing Link (view, anonymous):::View"
  ]
}
```

## Sync Process

1. **Authentication**: Connects to Microsoft Graph API using OAuth2
2. **Discovery**: Recursively scans SharePoint document library
3. **Permissions**: Fetches permissions for each file
4. **Comparison**: Compares SharePoint files with local files by size and modification date
5. **Sync**: Downloads new/modified files, deletes files removed from SharePoint
6. **Permissions Update**: Updates `.permissions.json` with current permissions
7. **Logging**: Saves detailed change log to `sync_logs/sync_changes_TIMESTAMP.json`

## RAG Database Integration

The sync process generates a comprehensive `sync_changes_TIMESTAMP.json` file designed for RAG database updates. This file contains:

### Structure
```json
{
  "timestamp": "2024-01-20_14-30-45",
  "summary": {
    "total_files": 42,
    "added_count": 3,
    "modified_count": 2,
    "deleted_count": 1,
    "permission_only_changes_count": 4
  },
  "changes": {
    "added": {
      "path/to/new/file.pdf": {
        "permissions": [
          "Team Owners:::Full Control",
          "Team Members:::Edit"
        ],
        "file_path": "ms365_data/data/path/to/new/file.pdf"
      }
    },
    "modified": {
      "path/to/modified/file.docx": {
        "content_changed": true,
        "permissions_changed": true,
        "file_path": "ms365_data/data/path/to/modified/file.docx",
        "permission_changes": {
          "added": ["New User:::View"],
          "removed": ["Old User:::Edit"],
          "current": ["Team Owners:::Full Control", "New User:::View"]
        }
      }
    },
    "permission_only_changes": {
      "path/to/unchanged/file.xlsx": {
        "permission_changes": {
          "added": ["Marketing Team:::Edit"],
          "removed": ["Sales Team:::View"],
          "current": ["Owners:::Full Control", "Marketing Team:::Edit"]
        },
        "file_path": "ms365_data/data/path/to/unchanged/file.xlsx"
      }
    },
    "deleted": {
      "path/to/deleted/file.pptx": {
        "permissions": [
          "Team Owners:::Full Control",
          "All Users:::View"
        ]
      }
    }
  }
}
```

### Using sync_changes.json for RAG Updates

1. **Added Files**: Ingest the file content and add all listed permissions
2. **Modified Files**: 
   - If `content_changed` is true, re-ingest the file content
   - If `permissions_changed` is true, update permissions (add/remove as specified)
3. **Permission-Only Changes**: Update permissions without re-ingesting content
4. **Deleted Files**: Remove from RAG database and remove all associated permissions

See `examples/rag_sync_example.py` for a complete example of processing sync changes.

## Error Handling

The library includes comprehensive error handling:

- **Authentication errors**: Clear messages for invalid credentials
- **Network errors**: Retry logic for temporary connection issues
- **File system errors**: Graceful handling of permission issues
- **API errors**: Proper handling of SharePoint/Graph API limitations

## Development

### Setting up development environment

```bash
git clone https://github.com/yourusername/ms365sync.git
cd ms365sync
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

### Code formatting

```bash
black ms365sync/
isort ms365sync/
```

### Type checking

```bash
mypy ms365sync/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 0.1.0
- Initial release
- Basic SharePoint to local sync functionality
- CLI interface
- Comprehensive logging and error handling
- File permissions tracking

## Roadmap

- [ ] Implement dry-run mode
- [ ] Add configuration file support (YAML/JSON)
- [ ] Implement upload functionality (local to SharePoint)
- [ ] Add filtering options (file types, patterns)
- [ ] Add scheduled sync support
- [ ] Implement incremental sync optimization
- [ ] Add progress bars for large syncs
- [ ] Support for multiple SharePoint sites
- [ ] Permission change notifications 