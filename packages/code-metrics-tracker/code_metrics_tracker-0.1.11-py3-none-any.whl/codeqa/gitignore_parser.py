#!/usr/bin/env python3
"""
Parser for .gitignore files to extract exclude patterns for codeqa.

This module provides utilities to read .gitignore files and convert
their patterns to codeqa-compatible exclude patterns.
"""

import os
from typing import List, Set


class GitignoreParser:
    """Parse .gitignore files and convert patterns to codeqa format."""
    
    # Patterns that are typically in .gitignore but might not be suitable for code analysis
    # These are development/IDE specific files that might contain actual code to analyze
    QUESTIONABLE_PATTERNS = {
        '.env', '.env.local', '.env.development', '.env.test', '.env.production',
        '*.log', 'logs/', 'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*',
        '.DS_Store', 'Thumbs.db', 'desktop.ini',
        '.idea/', '.vscode/', '*.swp', '*.swo', '*~',
        'node_modules/',  # This is already excluded by ruff
        '.git/',  # This is already excluded by cloc
    }
    
    # Common build/artifact patterns that are definitely good to exclude
    RECOMMENDED_PATTERNS = {
        '__pycache__/', '*.pyc', '*.pyo', '*.pyd', '.Python',
        'build/', 'develop-eggs/', 'dist/', 'downloads/', 'eggs/',
        '.eggs/', 'lib/', 'lib64/', 'parts/', 'sdist/', 'var/',
        'wheels/', '*.egg-info/', '*.egg', 'MANIFEST',
        '.pytest_cache/', '.tox/', '.coverage', '.coverage.*',
        'htmlcov/', '.hypothesis/', '.mypy_cache/', '.ruff_cache/',
        'venv/', 'env/', 'ENV/', '.venv/', '.direnv/',
        '*.so', '*.dylib', '*.dll', '*.class', '*.o',
        'target/', '*.jar', '*.war', '*.ear',
        '_build/', '*.mo', '*.pot', 'docs/_build/',
        'instance/', '.webassets-cache',
    }
    
    @staticmethod
    def parse_gitignore_file(filepath: str) -> List[str]:
        """
        Parse a .gitignore file and extract patterns.
        
        Args:
            filepath: Path to the .gitignore file
            
        Returns:
            List of patterns from the .gitignore file
        """
        patterns = []
        
        if not os.path.exists(filepath):
            return patterns
        
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    # Strip whitespace
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Skip negation patterns (we can't handle these in codeqa)
                    if line.startswith('!'):
                        continue
                    
                    # Remove trailing slashes for consistency
                    # but remember if it was a directory pattern
                    is_dir = line.endswith('/')
                    pattern = line.rstrip('/')
                    
                    # Convert some gitignore-specific patterns
                    # In .gitignore, patterns starting with / are relative to the root
                    if pattern.startswith('/'):
                        pattern = pattern[1:]  # Remove leading slash
                    
                    # Add the pattern
                    if pattern:
                        patterns.append(pattern)
                        
        except Exception as e:
            print(f"Warning: Could not read .gitignore file: {e}")
        
        return patterns
    
    @staticmethod
    def filter_patterns(patterns: List[str], include_all: bool = False) -> List[str]:
        """
        Filter patterns to remove those that might not be suitable for code analysis.
        
        Args:
            patterns: List of patterns from .gitignore
            include_all: If True, include all patterns without filtering
            
        Returns:
            Filtered list of patterns
        """
        if include_all:
            return patterns
        
        filtered = []
        skipped = []
        
        for pattern in patterns:
            # Check if this pattern is questionable
            is_questionable = False
            
            # Remove trailing slashes for comparison
            pattern_clean = pattern.rstrip('/')
            
            for q_pattern in GitignoreParser.QUESTIONABLE_PATTERNS:
                q_pattern_clean = q_pattern.rstrip('/')
                
                # Check exact match or if it's a related pattern
                if (pattern_clean == q_pattern_clean or 
                    pattern == q_pattern or
                    (q_pattern.endswith('/') and pattern_clean == q_pattern_clean)):
                    is_questionable = True
                    skipped.append(pattern)
                    break
            
            if not is_questionable:
                filtered.append(pattern)
        
        if skipped:
            print(f"Note: Skipped some .gitignore patterns that might not be suitable for code analysis:")
            for pattern in skipped:
                print(f"  - {pattern}")
            print("Use --all-gitignore-patterns to include these patterns anyway.")
        
        return filtered
    
    @staticmethod
    def merge_with_defaults(gitignore_patterns: List[str], default_patterns: List[str]) -> List[str]:
        """
        Merge gitignore patterns with default patterns, removing duplicates.
        
        Args:
            gitignore_patterns: Patterns from .gitignore
            default_patterns: Default patterns from codeqa
            
        Returns:
            Merged list of unique patterns
        """
        # Use a set to remove duplicates, but preserve order
        seen = set()
        merged = []
        
        # Add gitignore patterns first (they take precedence)
        for pattern in gitignore_patterns:
            if pattern not in seen:
                seen.add(pattern)
                merged.append(pattern)
        
        # Add default patterns that aren't already present
        for pattern in default_patterns:
            if pattern not in seen:
                seen.add(pattern)
                merged.append(pattern)
        
        return merged
    
    @staticmethod
    def find_gitignore_files(root_dir: str) -> List[str]:
        """
        Find all .gitignore files in the project.
        
        Args:
            root_dir: Root directory to search from
            
        Returns:
            List of paths to .gitignore files
        """
        gitignore_files = []
        
        # Check root directory first
        root_gitignore = os.path.join(root_dir, '.gitignore')
        if os.path.exists(root_gitignore):
            gitignore_files.append(root_gitignore)
        
        # Note: We could search for .gitignore files in subdirectories,
        # but this gets complex as those patterns are relative to their location.
        # For now, we'll just use the root .gitignore
        
        return gitignore_files
    
    @staticmethod
    def suggest_additional_patterns(patterns: List[str]) -> List[str]:
        """
        Suggest additional patterns based on what's in .gitignore.
        
        Args:
            patterns: Current patterns
            
        Returns:
            List of suggested patterns to add
        """
        suggestions = []
        current_set = set(patterns)
        
        # If we see Python patterns, suggest common Python exclusions
        python_indicators = {'*.pyc', '__pycache__/', '*.pyo', 'venv/', '.venv/'}
        if any(p in current_set for p in python_indicators):
            python_suggestions = [
                '.coverage', 'htmlcov/', '*.egg-info/', '.pytest_cache/',
                '.mypy_cache/', '.ruff_cache/', '.tox/'
            ]
            for sugg in python_suggestions:
                if sugg not in current_set:
                    suggestions.append(sugg)
        
        # If we see JavaScript patterns, suggest common JS exclusions
        js_indicators = {'node_modules/', '*.log', 'npm-debug.log*'}
        if any(p in current_set for p in js_indicators):
            js_suggestions = [
                'dist/', 'build/', '.next/', 'out/', 'coverage/',
                '.cache/', '.parcel-cache/'
            ]
            for sugg in js_suggestions:
                if sugg not in current_set:
                    suggestions.append(sugg)
        
        return suggestions