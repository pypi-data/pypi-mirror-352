"""
Utility functions for MS365Sync.
"""

from typing import Any, Dict


def print_file_tree(files: Dict[str, dict], title: str) -> None:
    """Print a tree structure of files for debugging"""
    print(f"\n=== {title} ===")
    if not files:
        print("  (empty)")
        return

    # Group files by directory
    tree: Dict[str, Any] = {}
    for rel_path in sorted(files.keys()):
        parts = rel_path.split("/")
        current = tree

        # Build nested directory structure
        for i, part in enumerate(parts):
            if i == len(parts) - 1:  # This is a file
                if "_files" not in current:
                    current["_files"] = []
                current["_files"].append(part)
            else:  # This is a directory
                if part not in current:
                    current[part] = {}
                current = current[part]

    # Print the tree
    _print_tree_recursive(tree, "", True)


def _print_tree_recursive(node: Dict[str, Any], prefix: str, is_last: bool) -> None:
    """Recursively print tree structure"""
    # Print files in current directory
    if "_files" in node:
        files = sorted(node["_files"])
        dirs = sorted([k for k in node.keys() if k != "_files"])

        # Print files first
        for i, filename in enumerate(files):
            is_last_item = (i == len(files) - 1) and len(dirs) == 0
            file_prefix = "└── " if is_last_item else "├── "
            print(f"{prefix}{file_prefix}{filename}")

    # Print directories
    dirs = sorted([k for k in node.keys() if k != "_files"])
    for i, dirname in enumerate(dirs):
        is_last_dir = i == len(dirs) - 1
        dir_prefix = "└── " if is_last_dir else "├── "
        print(f"{prefix}{dir_prefix}{dirname}/")

        # Recurse into subdirectory
        next_prefix = prefix + ("    " if is_last_dir else "│   ")
        _print_tree_recursive(node[dirname], next_prefix, is_last_dir)
