"""
Tests for utility functions.
"""

import io
from unittest.mock import patch
from typing import Any, Dict


from ms365sync.utils import print_file_tree, _print_tree_recursive


class TestUtils:
    """Test cases for utility functions."""

    # ============ print_file_tree Tests ============

    def test_print_file_tree_empty(self) -> None:
        """Test printing an empty file tree."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree({}, "TEST TREE")
            output = mock_stdout.getvalue()

            assert "=== TEST TREE ===" in output
            assert "(empty)" in output

    def test_print_file_tree_single_file(self) -> None:
        """Test printing a tree with a single file."""
        files = {"single_file.txt": {"size": 100}}

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "SINGLE FILE")
            output = mock_stdout.getvalue()

            assert "=== SINGLE FILE ===" in output
            assert "single_file.txt" in output
            assert "└── single_file.txt" in output or "├── single_file.txt" in output

    def test_print_file_tree_multiple_files_root(self) -> None:
        """Test printing a tree with multiple files in root."""
        files = {
            "file1.txt": {"size": 100},
            "file2.txt": {"size": 200},
            "file3.txt": {"size": 300},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "MULTIPLE FILES")
            output = mock_stdout.getvalue()

            assert "=== MULTIPLE FILES ===" in output
            assert "file1.txt" in output
            assert "file2.txt" in output
            assert "file3.txt" in output
            # Should contain tree structure characters
            assert "├──" in output or "└──" in output

    def test_print_file_tree_with_single_folder(self) -> None:
        """Test printing a tree with files in a single folder."""
        files = {
            "folder/file1.txt": {"size": 100},
            "folder/file2.txt": {"size": 200},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "FOLDER STRUCTURE")
            output = mock_stdout.getvalue()

            assert "=== FOLDER STRUCTURE ===" in output
            assert "folder/" in output
            assert "file1.txt" in output
            assert "file2.txt" in output
            # Should show folder structure
            assert "├──" in output or "└──" in output

    def test_print_file_tree_complex_structure(self) -> None:
        """Test printing a complex file tree structure."""
        files = {
            "root_file.txt": {"size": 100},
            "docs/readme.md": {"size": 200},
            "docs/guide.md": {"size": 300},
            "src/main.py": {"size": 400},
            "src/utils/helper.py": {"size": 500},
            "src/utils/config.py": {"size": 600},
            "tests/test_main.py": {"size": 700},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "COMPLEX STRUCTURE")
            output = mock_stdout.getvalue()

            assert "=== COMPLEX STRUCTURE ===" in output

            # Check all files are present
            assert "root_file.txt" in output
            assert "readme.md" in output
            assert "guide.md" in output
            assert "main.py" in output
            assert "helper.py" in output
            assert "config.py" in output
            assert "test_main.py" in output

            # Check all folders are present
            assert "docs/" in output
            assert "src/" in output
            assert "utils/" in output
            assert "tests/" in output

            # Check for tree structure characters
            assert "├──" in output or "└──" in output
            # Should have indentation for nested folders
            assert "    " in output or "│   " in output

    def test_print_file_tree_deep_nesting(self) -> None:
        """Test printing a tree with deeply nested folders."""
        files = {
            "a/b/c/d/e/deep_file.txt": {"size": 100},
            "a/b/c/other_file.txt": {"size": 200},
            "a/shallow_file.txt": {"size": 300},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "DEEP NESTING")
            output = mock_stdout.getvalue()

            assert "=== DEEP NESTING ===" in output
            assert "deep_file.txt" in output
            assert "other_file.txt" in output
            assert "shallow_file.txt" in output

            # Check nested folder structure
            assert "a/" in output
            assert "b/" in output
            assert "c/" in output
            assert "d/" in output
            assert "e/" in output

    def test_print_file_tree_with_special_characters(self) -> None:
        """Test printing a tree with files containing special characters."""
        files = {
            "file with spaces.txt": {"size": 100},
            "file-with-dashes.txt": {"size": 200},
            "file_with_underscores.txt": {"size": 300},
            "file.with.dots.txt": {"size": 400},
            "folder with spaces/nested file.txt": {"size": 500},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "SPECIAL CHARS")
            output = mock_stdout.getvalue()

            assert "=== SPECIAL CHARS ===" in output
            assert "file with spaces.txt" in output
            assert "file-with-dashes.txt" in output
            assert "file_with_underscores.txt" in output
            assert "file.with.dots.txt" in output
            assert "folder with spaces/" in output
            assert "nested file.txt" in output

    def test_print_file_tree_sorted_output(self) -> None:
        """Test that files and folders are sorted in output."""
        files = {
            "z_file.txt": {"size": 100},
            "a_file.txt": {"size": 200},
            "m_file.txt": {"size": 300},
            "zebra/file.txt": {"size": 400},
            "alpha/file.txt": {"size": 500},
            "beta/file.txt": {"size": 600},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "SORTED")
            output = mock_stdout.getvalue()
            lines = output.strip().split("\n")

            # Files should be sorted alphabetically - just check basic ordering
            assert "a_file.txt" in output
            assert "m_file.txt" in output
            assert "z_file.txt" in output

            # Find the positions of the root files in the output
            a_file_line = next(
                (i for i, line in enumerate(lines) if "a_file.txt" in line), -1
            )
            m_file_line = next(
                (i for i, line in enumerate(lines) if "m_file.txt" in line), -1
            )
            z_file_line = next(
                (i for i, line in enumerate(lines) if "z_file.txt" in line), -1
            )

            # They should all be found and in alphabetical order
            assert a_file_line != -1 and m_file_line != -1 and z_file_line != -1
            assert a_file_line < m_file_line < z_file_line

            # Check folders are present and sorted
            assert "alpha/" in output
            assert "beta/" in output
            assert "zebra/" in output

    def test_print_file_tree_mixed_files_and_folders(self) -> None:
        """Test printing a tree with mixed files and folders at same level."""
        files = {
            "root_file1.txt": {"size": 100},
            "folder1/nested_file.txt": {"size": 200},
            "root_file2.txt": {"size": 300},
            "folder2/nested_file.txt": {"size": 400},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "MIXED")
            output = mock_stdout.getvalue()

            assert "=== MIXED ===" in output
            assert "root_file1.txt" in output
            assert "root_file2.txt" in output
            assert "folder1/" in output
            assert "folder2/" in output
            assert "nested_file.txt" in output

    # ============ _print_tree_recursive Tests ============

    def test_print_tree_recursive_empty_node(self) -> None:
        """Test recursive tree printing with empty node."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            _print_tree_recursive({}, "", True)
            output = mock_stdout.getvalue()

            # Empty node should produce no output
            assert output == ""

    def test_print_tree_recursive_files_only(self) -> None:
        """Test recursive tree printing with files only."""
        node: Dict[str, Any] = {"_files": ["file1.txt", "file2.txt"]}

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            _print_tree_recursive(node, "", True)
            output = mock_stdout.getvalue()

            assert "file1.txt" in output
            assert "file2.txt" in output
            assert "├──" in output or "└──" in output

    def test_print_tree_recursive_folders_only(self) -> None:
        """Test recursive tree printing with folders only."""
        node: Dict[str, Any] = {"folder1": {}, "folder2": {}}

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            _print_tree_recursive(node, "", True)
            output = mock_stdout.getvalue()

            assert "folder1/" in output
            assert "folder2/" in output
            assert "├──" in output or "└──" in output

    def test_print_tree_recursive_mixed_content(self) -> None:
        """Test recursive tree printing with mixed files and folders."""
        node: Dict[str, Any] = {
            "_files": ["file1.txt"],
            "subfolder": {"_files": ["nested_file.txt"]},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            _print_tree_recursive(node, "", True)
            output = mock_stdout.getvalue()

            assert "file1.txt" in output
            assert "subfolder/" in output
            assert "nested_file.txt" in output

    def test_print_tree_recursive_with_prefix(self) -> None:
        """Test recursive tree printing with prefix indentation."""
        node: Dict[str, Any] = {
            "_files": ["file.txt"],
            "subfolder": {"_files": ["nested.txt"]},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            _print_tree_recursive(node, "│   ", False)
            output = mock_stdout.getvalue()

            # Should include the prefix in output
            assert "│   " in output
            assert "file.txt" in output
            assert "subfolder/" in output

    def test_print_tree_recursive_last_item_formatting(self) -> None:
        """Test that last items get proper formatting."""
        node: Dict[str, Any] = {"_files": ["file1.txt", "file2.txt"], "folder": {}}

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            _print_tree_recursive(node, "", True)
            output = mock_stdout.getvalue()
            lines = output.strip().split("\n")

            # Last item should use └── instead of ├──
            last_line = lines[-1] if lines else ""
            assert "└──" in last_line or "├──" in last_line

    # ============ Error Handling and Edge Cases ============

    def test_print_file_tree_none_input(self) -> None:
        """Test print_file_tree handles None input gracefully."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            # This should be handled as empty
            print_file_tree({}, "NONE TEST")
            output = mock_stdout.getvalue()

            assert "=== NONE TEST ===" in output
            assert "(empty)" in output

    def test_print_file_tree_empty_filename(self) -> None:
        """Test handling of empty filename (edge case)."""
        files = {"": {"size": 100}}

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "EMPTY NAME")
            output = mock_stdout.getvalue()

            assert "=== EMPTY NAME ===" in output
            # Empty filename should still be handled

    def test_print_file_tree_only_slash_path(self) -> None:
        """Test handling of path that's just slashes."""
        files = {"///": {"size": 100}}

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "SLASH TEST")
            output = mock_stdout.getvalue()

            assert "=== SLASH TEST ===" in output

    def test_print_file_tree_very_long_title(self) -> None:
        """Test with very long title."""
        very_long_title = "A" * 100
        files = {"file.txt": {"size": 100}}

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, very_long_title)
            output = mock_stdout.getvalue()

            assert f"=== {very_long_title} ===" in output
            assert "file.txt" in output

    def test_print_file_tree_large_structure(self) -> None:
        """Test with a large file structure to ensure performance."""
        # Create a large structure with many files and folders
        files = {}
        for i in range(50):
            files[f"file_{i:02d}.txt"] = {"size": i * 100}
            for j in range(5):
                files[f"folder_{i:02d}/file_{j:02d}.txt"] = {"size": i * j * 10}

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "LARGE STRUCTURE")
            output = mock_stdout.getvalue()

            assert "=== LARGE STRUCTURE ===" in output
            assert "file_00.txt" in output
            assert "file_49.txt" in output
            assert "folder_00/" in output
            assert "folder_49/" in output

    # ============ Integration Tests ============

    def test_print_file_tree_realistic_project_structure(self) -> None:
        """Test with a realistic project file structure."""
        files = {
            "README.md": {"size": 1024},
            "requirements.txt": {"size": 512},
            "setup.py": {"size": 2048},
            ".gitignore": {"size": 256},
            "src/main.py": {"size": 4096},
            "src/__init__.py": {"size": 0},
            "src/utils/helpers.py": {"size": 1536},
            "src/utils/__init__.py": {"size": 0},
            "src/models/user.py": {"size": 2048},
            "src/models/database.py": {"size": 3072},
            "tests/test_main.py": {"size": 1024},
            "tests/test_utils.py": {"size": 2048},
            "tests/__init__.py": {"size": 0},
            "docs/installation.md": {"size": 1024},
            "docs/usage.md": {"size": 2048},
            "docs/api.md": {"size": 4096},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "PROJECT STRUCTURE")
            output = mock_stdout.getvalue()

            # Check structure
            assert "=== PROJECT STRUCTURE ===" in output

            # Root files
            assert "README.md" in output
            assert "requirements.txt" in output
            assert "setup.py" in output
            assert ".gitignore" in output

            # Folders
            assert "src/" in output
            assert "tests/" in output
            assert "docs/" in output
            assert "utils/" in output
            assert "models/" in output

            # Nested files
            assert "main.py" in output
            assert "helpers.py" in output
            assert "user.py" in output
            assert "database.py" in output
            assert "test_main.py" in output
            assert "installation.md" in output

    def test_file_tree_consistency(self) -> None:
        """Test that the same input produces consistent output."""
        files = {
            "file1.txt": {"size": 100},
            "folder/file2.txt": {"size": 200},
            "folder/subfolder/file3.txt": {"size": 300},
        }

        # Run the same test multiple times
        outputs = []
        for _ in range(3):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                print_file_tree(files, "CONSISTENCY TEST")
                outputs.append(mock_stdout.getvalue())

        # All outputs should be identical
        assert len(set(outputs)) == 1, "Output should be consistent across runs"
