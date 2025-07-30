#!/usr/bin/env python3
"""
Tests for the GitignoreParser class.
"""

import os
import tempfile
import unittest
from codeqa.gitignore_parser import GitignoreParser


class TestGitignoreParser(unittest.TestCase):
    """Test cases for GitignoreParser."""

    def test_parse_gitignore_file(self):
        """Test parsing a .gitignore file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gitignore', delete=False) as f:
            f.write("""# Python patterns
__pycache__/
*.pyc
*.pyo

# Virtual environments
venv/
env/
.venv/

# IDE files
.idea/
.vscode/
*.swp

# Build artifacts
build/
dist/
*.egg-info/

# Test coverage
.coverage
htmlcov/

# Logs
*.log
logs/

# OS files
.DS_Store
Thumbs.db

# Negation pattern (should be skipped)
!important.log

# Root-relative pattern
/config.local

# Comments and empty lines should be ignored
# This is a comment

# Another comment
""")
            f.flush()
            
            patterns = GitignoreParser.parse_gitignore_file(f.name)
            
            # Clean up
            os.unlink(f.name)
        
        # Check that patterns were parsed correctly
        self.assertIn('__pycache__', patterns)
        self.assertIn('*.pyc', patterns)
        self.assertIn('venv', patterns)
        self.assertIn('.idea', patterns)
        self.assertIn('build', patterns)
        self.assertIn('.coverage', patterns)
        self.assertIn('*.log', patterns)
        self.assertIn('.DS_Store', patterns)
        
        # Root-relative pattern should have the leading slash removed
        self.assertIn('config.local', patterns)
        
        # Negation patterns should not be included
        self.assertNotIn('!important.log', patterns)
        
        # Comments should not be included
        self.assertFalse(any(p.startswith('#') for p in patterns))
        
        # Empty strings should not be included
        self.assertNotIn('', patterns)

    def test_filter_patterns(self):
        """Test filtering questionable patterns."""
        test_patterns = [
            '__pycache__',
            '*.pyc',
            'venv',
            '.env',  # Questionable
            '.env.local',  # Questionable
            'node_modules',  # Questionable (already excluded by ruff)
            '.idea',  # Questionable
            'build',
            'dist',
            '*.log',  # Questionable
            '.DS_Store',  # Questionable
        ]
        
        # Test with filtering enabled (default)
        filtered = GitignoreParser.filter_patterns(test_patterns, include_all=False)
        
        # These should be kept
        self.assertIn('__pycache__', filtered)
        self.assertIn('*.pyc', filtered)
        self.assertIn('venv', filtered)
        self.assertIn('build', filtered)
        self.assertIn('dist', filtered)
        
        # These should be filtered out
        self.assertNotIn('.env', filtered)
        self.assertNotIn('.env.local', filtered)
        self.assertNotIn('node_modules', filtered)
        self.assertNotIn('.idea', filtered)
        self.assertNotIn('*.log', filtered)
        self.assertNotIn('.DS_Store', filtered)
        
        # Test with no filtering
        all_patterns = GitignoreParser.filter_patterns(test_patterns, include_all=True)
        self.assertEqual(len(all_patterns), len(test_patterns))

    def test_merge_with_defaults(self):
        """Test merging gitignore patterns with defaults."""
        gitignore_patterns = ['__pycache__', '*.pyc', 'venv', 'custom_dir']
        default_patterns = ['migrations', '.coverage', '*.db', '*.log', '__pycache__']
        
        merged = GitignoreParser.merge_with_defaults(gitignore_patterns, default_patterns)
        
        # Should contain all unique patterns
        self.assertIn('__pycache__', merged)
        self.assertIn('*.pyc', merged)
        self.assertIn('venv', merged)
        self.assertIn('custom_dir', merged)
        self.assertIn('migrations', merged)
        self.assertIn('.coverage', merged)
        self.assertIn('*.db', merged)
        self.assertIn('*.log', merged)
        
        # Should not have duplicates
        self.assertEqual(merged.count('__pycache__'), 1)
        
        # Gitignore patterns should come first
        self.assertEqual(merged.index('custom_dir'), 3)
        self.assertGreater(merged.index('migrations'), merged.index('custom_dir'))

    def test_suggest_additional_patterns(self):
        """Test pattern suggestions based on existing patterns."""
        # Python project patterns
        python_patterns = ['*.pyc', '__pycache__', 'venv']
        suggestions = GitignoreParser.suggest_additional_patterns(python_patterns)
        
        # Should suggest common Python patterns
        self.assertIn('.coverage', suggestions)
        self.assertIn('htmlcov/', suggestions)
        self.assertIn('*.egg-info/', suggestions)
        self.assertIn('.pytest_cache/', suggestions)
        
        # Should not suggest patterns already present
        self.assertNotIn('*.pyc', suggestions)
        self.assertNotIn('__pycache__', suggestions)
        self.assertNotIn('venv', suggestions)
        
        # JavaScript project patterns
        js_patterns = ['node_modules/', '*.log']
        suggestions = GitignoreParser.suggest_additional_patterns(js_patterns)
        
        # Should suggest common JS patterns
        self.assertIn('dist/', suggestions)
        self.assertIn('build/', suggestions)
        self.assertIn('coverage/', suggestions)

    def test_find_gitignore_files(self):
        """Test finding .gitignore files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a .gitignore in the root
            gitignore_path = os.path.join(tmpdir, '.gitignore')
            with open(gitignore_path, 'w') as f:
                f.write("*.pyc\n")
            
            # Find gitignore files
            files = GitignoreParser.find_gitignore_files(tmpdir)
            
            # Should find the root .gitignore
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0], gitignore_path)

    def test_empty_gitignore(self):
        """Test handling empty .gitignore file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gitignore', delete=False) as f:
            f.write("")
            f.flush()
            
            patterns = GitignoreParser.parse_gitignore_file(f.name)
            
            # Clean up
            os.unlink(f.name)
        
        # Should return empty list
        self.assertEqual(patterns, [])

    def test_nonexistent_gitignore(self):
        """Test handling non-existent .gitignore file."""
        patterns = GitignoreParser.parse_gitignore_file('/nonexistent/.gitignore')
        
        # Should return empty list
        self.assertEqual(patterns, [])

    def test_complex_gitignore_patterns(self):
        """Test parsing complex .gitignore patterns."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gitignore', delete=False) as f:
            f.write("""# Complex patterns
**/temp/
*.tmp
!keep.tmp
/root-only.txt
subdir/specific.txt
*.py[cod]
.env*
!.env.example
""")
            f.flush()
            
            patterns = GitignoreParser.parse_gitignore_file(f.name)
            
            # Clean up
            os.unlink(f.name)
        
        # Check patterns
        self.assertIn('**/temp', patterns)
        self.assertIn('*.tmp', patterns)
        self.assertIn('root-only.txt', patterns)
        self.assertIn('subdir/specific.txt', patterns)
        self.assertIn('*.py[cod]', patterns)
        self.assertIn('.env*', patterns)
        
        # Negation patterns should be skipped
        self.assertNotIn('!keep.tmp', patterns)
        self.assertNotIn('!.env.example', patterns)


if __name__ == '__main__':
    unittest.main()