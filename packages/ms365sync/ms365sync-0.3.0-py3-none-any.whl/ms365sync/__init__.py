"""
MS365Sync - A Python library for syncing files between Microsoft 365
SharePoint and local storage.

This library provides a simple interface to sync files between SharePoint
document libraries and local directories, with support for detecting changes
and maintaining file hierarchies.
"""

from .sharepoint_sync import SharePointSync

__version__ = "0.3.0"
__all__ = ["SharePointSync"]
