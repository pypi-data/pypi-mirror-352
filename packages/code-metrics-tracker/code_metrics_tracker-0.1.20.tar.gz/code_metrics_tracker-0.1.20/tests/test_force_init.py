#!/usr/bin/env python3
"""
Test the --force flag for codeqa init command.
"""

import os
import json
import tempfile
import shutil
import unittest
from unittest.mock import patch

from codeqa.metrics import init_project


class TestForceInit(unittest.TestCase):
    """Test the force initialization functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        
    def test_force_backup_existing_config(self):
        """Test that --force backs up existing config."""
        # Create initial config
        config_data = {
            "include_paths": ["src"],
            "exclude_patterns": ["*.pyc", "venv/"]
        }
        
        with open("codeqa.json", "w") as f:
            json.dump(config_data, f)
            
        # Create .gitignore with comment
        with open(".gitignore", "w") as f:
            f.write("__pycache__/\n")
            f.write("*.py[cod] # Python bytecode files\n")
            f.write("venv/ # Virtual environment\n")
            f.write(".coverage # Coverage data\n")
            
        # Initialize with force
        init_project(from_gitignore=True, force=True)
        
        # Check backup was created
        self.assertTrue(os.path.exists("codeqa.json.bak"))
        
        # Check backup contains original data
        with open("codeqa.json.bak", "r") as f:
            backup_data = json.load(f)
        self.assertEqual(backup_data, config_data)
        
        # Check new config was created from .gitignore
        with open("codeqa.json", "r") as f:
            new_data = json.load(f)
        
        # Check comments were stripped
        self.assertIn("__pycache__", new_data["exclude_patterns"])
        self.assertIn("*.py[cod]", new_data["exclude_patterns"])
        self.assertIn("venv", new_data["exclude_patterns"])
        self.assertIn(".coverage", new_data["exclude_patterns"])
        
        # Make sure no comments in patterns
        for pattern in new_data["exclude_patterns"]:
            self.assertNotIn(" #", pattern)
            
    def test_force_multiple_backups(self):
        """Test that multiple backups are created with numbers."""
        # Create initial config
        with open("codeqa.json", "w") as f:
            json.dump({"test": 1}, f)
            
        # First force init
        init_project(force=True)
        self.assertTrue(os.path.exists("codeqa.json.bak"))
        
        # Second force init
        init_project(force=True)
        self.assertTrue(os.path.exists("codeqa.json.bak1"))
        
        # Third force init
        init_project(force=True)
        self.assertTrue(os.path.exists("codeqa.json.bak2"))
        
    def test_no_force_existing_config(self):
        """Test that without --force, existing config is not overwritten."""
        # Create existing config
        with open("codeqa.json", "w") as f:
            json.dump({"existing": True}, f)
            
        # Try to init without force
        with patch('builtins.print') as mock_print:
            init_project(from_gitignore=True)
            
        # Check that it printed the right message
        mock_print.assert_any_call("Configuration file already exists: codeqa.json")
        mock_print.assert_any_call("Use --force to backup and overwrite existing configuration")
        
        # Check config wasn't changed
        with open("codeqa.json", "r") as f:
            data = json.load(f)
        self.assertEqual(data, {"existing": True})


if __name__ == "__main__":
    unittest.main()