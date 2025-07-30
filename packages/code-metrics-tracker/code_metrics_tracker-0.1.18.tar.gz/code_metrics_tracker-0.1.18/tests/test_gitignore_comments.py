#!/usr/bin/env python3
"""
Test that comments are properly stripped from .gitignore patterns.
"""

import unittest
from codeqa.gitignore_parser import GitignoreParser


class TestGitignoreComments(unittest.TestCase):
    """Test comment stripping from .gitignore patterns."""
    
    def test_strip_inline_comments(self):
        """Test that inline comments are stripped from patterns."""
        test_cases = [
            ("*.pyc # Python bytecode", "*.pyc"),
            ("venv/ # Virtual environment", "venv"),
            (".coverage # Coverage data", ".coverage"),
            ("data/exports/ # Generated data", "data/exports"),
            ("file#withpound", "file#withpound"),  # No space before #
            ("file #comment", "file"),
            ("  pattern  # comment  ", "pattern"),
            ("# full line comment", None),  # Should be skipped
            ("", None),  # Empty line should be skipped
        ]
        
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gitignore', delete=False) as f:
            # Write test patterns
            f.write("# This is a comment\n")
            f.write("\n")  # Empty line
            f.write("*.pyc # Python bytecode\n")
            f.write("venv/ # Virtual environment\n")
            f.write(".coverage # Coverage data\n")
            f.write("data/exports/ # Generated data\n")
            f.write("file#withpound\n")
            f.write("file #comment\n")
            f.write("  pattern  # comment  \n")
            f.flush()
            
            # Parse the file
            patterns = GitignoreParser.parse_gitignore_file(f.name)
            
        # Clean up
        os.unlink(f.name)
        
        # Expected patterns (without comments)
        expected = [
            "*.pyc",
            "venv",
            ".coverage", 
            "data/exports",
            "file#withpound",
            "file",
            "pattern"
        ]
        
        self.assertEqual(patterns, expected)
        
    def test_complex_patterns_with_comments(self):
        """Test more complex patterns with comments."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gitignore', delete=False) as f:
            f.write("# Build outputs\n")
            f.write("dist/ # Distribution files\n")
            f.write("build/ # Build artifacts\n")
            f.write("*.egg-info/ # Package metadata\n")
            f.write("\n")
            f.write("# IDE files\n")
            f.write(".idea/ # IntelliJ IDEA\n")
            f.write(".vscode/ # Visual Studio Code\n")
            f.write("\n")
            f.write("# Data files\n")
            f.write("*.db # SQLite databases\n")
            f.write("*.log # Log files\n")
            f.write("data/simplepay/exports/ # If this directory is used for generated exports\n")
            f.flush()
            
            patterns = GitignoreParser.parse_gitignore_file(f.name)
            
        os.unlink(f.name)
        
        expected = [
            "dist",
            "build",
            "*.egg-info",
            ".idea",
            ".vscode",
            "*.db",
            "*.log",
            "data/simplepay/exports"
        ]
        
        self.assertEqual(patterns, expected)
        
        # Verify no patterns contain comments
        for pattern in patterns:
            self.assertNotIn(" #", pattern)
            self.assertNotIn("# ", pattern)


if __name__ == "__main__":
    unittest.main()