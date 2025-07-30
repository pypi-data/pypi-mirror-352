# MS365Sync

Sync files between Microsoft 365 SharePoint and your local machine with permission tracking.

## What it does

- Downloads files from SharePoint document libraries to local folders
- Tracks file permissions and detects changes
- Syncs only when files are modified (smart sync)
- Works via command line or Python code

## Quick Start

### 1. Install

```bash
pip install ms365sync
```

### 2. Setup Azure App

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Create new app registration
3. Add these API permissions: `Sites.Read.All`, `Files.Read.All` (Application permissions)
4. Create a client secret
5. Grant admin consent

### 3. Configure

Create a `.env` file:

```env
TENANT_ID=your-azure-tenant-id
CLIENT_ID=your-azure-client-id
CLIENT_SECRET=your-azure-client-secret
```

### 4. Use it

**Command line:**
```bash
ms365sync \
  --sharepoint-host "yourcompany.sharepoint.com" \
  --site-name "Your Site Name" \
  --doc-library "Documents"
```

**Python code:**
```python
from ms365sync import SharePointSync

sync = SharePointSync(
    sharepoint_host="yourcompany.sharepoint.com",
    site_name="Your Site Name", 
    doc_library="Documents"
)

changes = sync.sync()
print(f"Synced {changes['total_files']} files")
```

## What you get

After running sync:
```ms365_data/
├── data/               # Your SharePoint files
└── .permissions.json   # Permission tracking
sync_logs/              # Sync operation logs
```

## Need help?

- Check the `examples/` folder for more usage patterns
- Report issues: [GitHub Issues](https://github.com/Phi4AI/ms365sync/issues)
- Email: aiteam@phianalytica.com 
