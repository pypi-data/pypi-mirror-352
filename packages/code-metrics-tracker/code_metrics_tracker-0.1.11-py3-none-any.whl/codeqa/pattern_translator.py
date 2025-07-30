#!/usr/bin/env python3
"""
Pattern translator for converting between different pattern formats used by code analysis tools.

This module provides utilities to convert unified exclude patterns into tool-specific formats
for cloc, ruff, and radon.
"""

import re
from typing import List, Tuple


class PatternTranslator:
    """Translates exclude patterns between different tool formats."""
    
    @staticmethod
    def glob_to_regex(patterns: List[str]) -> str:
        """
        Convert glob patterns to a Perl-compatible regex for cloc.
        
        Args:
            patterns: List of glob patterns from codeqa.json
            
        Returns:
            A regex pattern string that can be used with cloc's --not-match-d option
        """
        regex_patterns = []
        
        for pattern in patterns:
            # Remove trailing slashes
            pattern = pattern.rstrip('/')
            
            # Skip empty patterns or whitespace-only patterns
            if not pattern or not pattern.strip():
                continue
            
            # Escape special regex characters except * and ?
            # We need to be careful not to escape the glob wildcards
            escaped = re.escape(pattern)
            # Unescape the wildcards that we want to convert
            escaped = escaped.replace(r'\*', '*').replace(r'\?', '?')
            
            # Convert glob wildcards to regex
            # ** matches any number of directories
            regex = escaped.replace('**', '.*')
            # * matches any characters except /
            regex = regex.replace('*', '[^/]*')
            # ? matches single character except /
            regex = regex.replace('?', '[^/]')
            
            # Handle different pattern types
            if '/' not in pattern and '.' not in pattern:
                # Simple directory name - match anywhere in path
                # e.g., "venv" should match /path/to/venv/ and /venv/subdir/
                regex = f'(^|/){regex}(/|$)'
            elif pattern.startswith('*.'):
                # File extension - match at end of filename
                # e.g., "*.pyc" should match any .pyc file
                regex = f'{regex}$'
            elif '/' in pattern:
                # Path pattern - match as specified
                # Could be absolute or relative
                if pattern.startswith('/'):
                    # Absolute path
                    regex = f'^{regex}'
                else:
                    # Relative path - can appear anywhere
                    regex = f'(^|/){regex}'
            else:
                # Other patterns with dots but no slashes
                # e.g., ".coverage" - match exactly
                regex = f'(^|/){regex}$'
            
            regex_patterns.append(regex)
        
        # Join all patterns with OR
        return '|'.join(regex_patterns) if regex_patterns else ''
    
    @staticmethod
    def separate_file_dir_patterns(patterns: List[str]) -> Tuple[List[str], List[str]]:
        """
        Separate file and directory patterns for radon.
        
        Args:
            patterns: List of patterns from codeqa.json
            
        Returns:
            Tuple of (file_patterns, directory_patterns)
        """
        file_patterns = []
        dir_patterns = []
        
        for pattern in patterns:
            # Remove trailing slashes
            pattern = pattern.rstrip('/')
            
            # Skip empty patterns or whitespace-only patterns
            if not pattern or not pattern.strip():
                continue
            
            # Determine if it's a file or directory pattern
            if pattern.startswith('*.'):
                # File extension pattern
                file_patterns.append(pattern)
            elif '.' in pattern and '/' not in pattern:
                # Likely a specific file like .coverage
                file_patterns.append(pattern)
            elif '*' in pattern and '/' in pattern:
                # Complex pattern with wildcards and paths
                # These usually work better as file patterns in radon
                file_patterns.append(pattern)
            else:
                # Directory pattern
                # Remove any wildcards for directory patterns
                clean_dir = pattern.replace('*', '')
                if clean_dir:
                    dir_patterns.append(clean_dir)
        
        return file_patterns, dir_patterns
    
    @staticmethod
    def patterns_to_ruff_globs(patterns: List[str]) -> List[str]:
        """
        Convert patterns to proper glob patterns for ruff.
        
        Args:
            patterns: List of patterns from codeqa.json
            
        Returns:
            List of glob patterns suitable for ruff's --exclude option
        """
        ruff_patterns = []
        
        for pattern in patterns:
            # Remove trailing slashes
            pattern = pattern.rstrip('/')
            
            # Skip empty patterns or whitespace-only patterns
            if not pattern or not pattern.strip():
                continue
            
            # Handle different pattern types
            if pattern.startswith('*.'):
                # File extension - already in glob format
                ruff_patterns.append(pattern)
            elif '/' not in pattern and '.' not in pattern:
                # Simple directory name - match anywhere
                ruff_patterns.append(f'**/{pattern}/**')
                # Also match the directory itself
                ruff_patterns.append(f'**/{pattern}')
            elif pattern.startswith('./'):
                # Relative path starting with ./
                ruff_patterns.append(pattern[2:])
            else:
                # Keep as-is for other patterns
                ruff_patterns.append(pattern)
        
        return ruff_patterns