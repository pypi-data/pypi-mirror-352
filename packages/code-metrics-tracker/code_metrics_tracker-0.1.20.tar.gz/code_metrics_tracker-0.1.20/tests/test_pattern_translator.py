#!/usr/bin/env python3
"""
Tests for the PatternTranslator class.

This tests the pattern translation functionality for converting
unified exclude patterns to tool-specific formats.
"""

import unittest
from codeqa.pattern_translator import PatternTranslator


class TestPatternTranslator(unittest.TestCase):
    """Test cases for PatternTranslator."""

    def test_glob_to_regex_simple_directory(self):
        """Test converting simple directory names to regex."""
        patterns = ["venv", "build", "dist"]
        regex = PatternTranslator.glob_to_regex(patterns)
        
        # Should match these directories anywhere in path
        self.assertIn("(^|/)venv(/|$)", regex)
        self.assertIn("(^|/)build(/|$)", regex)
        self.assertIn("(^|/)dist(/|$)", regex)
    
    def test_glob_to_regex_with_wildcards(self):
        """Test converting patterns with wildcards."""
        patterns = ["*env*", "*.pyc", "test_*"]
        regex = PatternTranslator.glob_to_regex(patterns)
        
        # *env* should match any directory containing 'env'
        self.assertIn("[^/]*env[^/]*", regex)
        # *.pyc should match .pyc files
        self.assertIn("[^/]*\\.pyc$", regex)
    
    def test_glob_to_regex_with_paths(self):
        """Test converting patterns with path separators."""
        patterns = ["src/test/", "*/migrations/*", "build/"]
        regex = PatternTranslator.glob_to_regex(patterns)
        
        # Should handle paths correctly
        self.assertIn("src/test", regex)
        self.assertIn("migrations", regex)
    
    def test_glob_to_regex_specific_files(self):
        """Test converting specific file patterns."""
        patterns = [".coverage", ".env", "*.db"]
        regex = PatternTranslator.glob_to_regex(patterns)
        
        # Specific files should match exactly
        self.assertIn("\\.coverage$", regex)
        self.assertIn("\\.env$", regex)
    
    def test_separate_file_dir_patterns(self):
        """Test separating file and directory patterns."""
        patterns = [
            "venv",           # directory
            "*.pyc",          # file extension
            ".coverage",      # specific file
            "migrations",     # directory
            "*/test/*",       # complex pattern
            "build/"          # directory with slash
        ]
        
        file_patterns, dir_patterns = PatternTranslator.separate_file_dir_patterns(patterns)
        
        # Check file patterns
        self.assertIn("*.pyc", file_patterns)
        self.assertIn(".coverage", file_patterns)
        self.assertIn("*/test/*", file_patterns)
        
        # Check directory patterns
        self.assertIn("venv", dir_patterns)
        self.assertIn("migrations", dir_patterns)
        self.assertIn("build", dir_patterns)
    
    def test_patterns_to_ruff_globs_simple_dirs(self):
        """Test converting simple directories to ruff globs."""
        patterns = ["venv", "build", "dist"]
        globs = PatternTranslator.patterns_to_ruff_globs(patterns)
        
        # Should create both directory and content patterns
        self.assertIn("**/venv/**", globs)
        self.assertIn("**/venv", globs)
        self.assertIn("**/build/**", globs)
        self.assertIn("**/build", globs)
    
    def test_patterns_to_ruff_globs_extensions(self):
        """Test converting file extensions to ruff globs."""
        patterns = ["*.pyc", "*.log", "*.db"]
        globs = PatternTranslator.patterns_to_ruff_globs(patterns)
        
        # Extensions should remain as-is
        self.assertIn("*.pyc", globs)
        self.assertIn("*.log", globs)
        self.assertIn("*.db", globs)
    
    def test_patterns_to_ruff_globs_mixed(self):
        """Test converting mixed patterns to ruff globs."""
        patterns = ["venv", "*.pyc", ".coverage", "src/test/"]
        globs = PatternTranslator.patterns_to_ruff_globs(patterns)
        
        # Check all pattern types
        self.assertIn("**/venv/**", globs)
        self.assertIn("*.pyc", globs)
        self.assertIn(".coverage", globs)
        self.assertIn("src/test", globs)
    
    def test_empty_patterns(self):
        """Test handling of empty patterns."""
        patterns = ["", "  ", "/"]
        
        # glob_to_regex should return empty string
        regex = PatternTranslator.glob_to_regex(patterns)
        self.assertEqual(regex, "")
        
        # separate_file_dir_patterns should return empty lists
        file_patterns, dir_patterns = PatternTranslator.separate_file_dir_patterns(patterns)
        self.assertEqual(file_patterns, [])
        self.assertEqual(dir_patterns, [])
        
        # patterns_to_ruff_globs should return empty list
        globs = PatternTranslator.patterns_to_ruff_globs(patterns)
        self.assertEqual(globs, [])
    
    def test_complex_real_world_patterns(self):
        """Test with real-world complex patterns."""
        patterns = [
            "venv",
            "*env*",
            "*.egg-info",
            ".coverage",
            "htmlcov",
            "*/migrations/*",
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
            "build/",
            "dist/",
            "wheelhouse"
        ]
        
        # Test regex conversion
        regex = PatternTranslator.glob_to_regex(patterns)
        self.assertIsInstance(regex, str)
        self.assertGreater(len(regex), 0)
        
        # Test file/dir separation
        file_patterns, dir_patterns = PatternTranslator.separate_file_dir_patterns(patterns)
        self.assertGreater(len(file_patterns), 0)
        self.assertGreater(len(dir_patterns), 0)
        
        # Test ruff globs
        globs = PatternTranslator.patterns_to_ruff_globs(patterns)
        self.assertGreater(len(globs), 0)


if __name__ == '__main__':
    unittest.main()