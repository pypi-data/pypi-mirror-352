"""
Filters for the Code Scanner module.

This module provides filter classes that can be applied to the CodeScanner
to include or exclude files based on various criteria.
"""

from abc import ABC, abstractmethod
from typing import List, Set, Optional, Pattern, Union
import re
import os

class FileFilter(ABC):
    """Base abstract class for file filters."""
    
    @abstractmethod
    def matches(self, file_info) -> bool:
        """
        Check if a file matches this filter.
        
        Args:
            file_info: FileInfo object to check
            
        Returns:
            True if the file matches, False otherwise
        """
        pass


class LanguageFilter(FileFilter):
    """Filter files by programming language."""
    
    def __init__(self, languages: List[str], include: bool = True):
        """
        Initialize a language filter.
        
        Args:
            languages: List of language names to filter by
            include: If True, include matching languages; if False, exclude them
        """
        self.languages = set(lang.lower() for lang in languages)
        self.include = include
        
    def matches(self, file_info) -> bool:
        """Check if a file matches the language filter."""
        if file_info.language is None:
            return not self.include
            
        language_match = file_info.language.lower() in self.languages
        return language_match if self.include else not language_match


class SizeFilter(FileFilter):
    """Filter files by size."""
    
    def __init__(self, max_size: int):
        """
        Initialize a size filter.
        
        Args:
            max_size: Maximum file size in bytes
        """
        self.max_size = max_size
        
    def matches(self, file_info) -> bool:
        """Check if a file matches the size filter."""
        return file_info.size <= self.max_size


class ExtensionFilter(FileFilter):
    """Filter files by extension."""
    
    def __init__(self, extensions: List[str], include: bool = True):
        """
        Initialize an extension filter.
        
        Args:
            extensions: List of file extensions to filter by
            include: If True, include matching extensions; if False, exclude them
        """
        self.extensions = {ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                          for ext in extensions}
        self.include = include
        
    def matches(self, file_info) -> bool:
        """Check if a file matches the extension filter."""
        extension_match = file_info.extension in self.extensions
        return extension_match if self.include else not extension_match


class PatternFilter(FileFilter):
    """Filter files by name pattern."""
    
    def __init__(self, patterns: List[str], include: bool = True):
        """
        Initialize a pattern filter.
        
        Args:
            patterns: List of glob patterns to filter by
            include: If True, include matching patterns; if False, exclude them
        """
        import fnmatch
        self.patterns = patterns
        self.include = include
        self._fnmatch = fnmatch
        
    def matches(self, file_info) -> bool:
        """Check if a file matches any pattern."""
        for pattern in self.patterns:
            if self._fnmatch.fnmatch(file_info.path, pattern):
                return self.include
        return not self.include


class RegexFilter(FileFilter):
    """Filter files by regex pattern."""
    
    def __init__(self, regex: Union[str, Pattern], include: bool = True):
        """
        Initialize a regex filter.
        
        Args:
            regex: Regular expression pattern to filter by
            include: If True, include matching regex; if False, exclude them
        """
        if isinstance(regex, str):
            self.regex = re.compile(regex)
        else:
            self.regex = regex
        self.include = include
        
    def matches(self, file_info) -> bool:
        """Check if a file matches the regex."""
        match = bool(self.regex.search(file_info.path))
        return match if self.include else not match


class ContentFilter(FileFilter):
    """Filter files by content."""
    
    def __init__(self, pattern: Union[str, Pattern], include: bool = True, word_boundary: bool = True):
        """
        Initialize a content filter.
        
        Args:
            pattern: Regular expression pattern to search in file content
            include: If True, include files with matching content; if False, exclude them
            word_boundary: If True, adds word boundaries to string patterns
        """
        if isinstance(pattern, str):
            if word_boundary:
                # Add word boundaries to make the match more precise
                pattern = r'\b' + re.escape(pattern) + r'\b'
            self.pattern = re.compile(pattern)
        else:
            self.pattern = pattern
        self.include = include
        
    def matches(self, file_info) -> bool:
        """Check if file content matches the pattern."""
        # Load content if not already loaded
        content = file_info.load_content()
        match = bool(self.pattern.search(content))
        return match if self.include else not match


class CompositeFilter(FileFilter):
    """Combine multiple filters with AND or OR logic."""
    
    def __init__(self, filters: List[FileFilter], require_all: bool = True):
        """
        Initialize a composite filter.
        
        Args:
            filters: List of filters to combine
            require_all: If True, all filters must match (AND); 
                        if False, any filter can match (OR)
        """
        self.filters = filters
        self.require_all = require_all
        
    def matches(self, file_info) -> bool:
        """Check if a file matches the composite filter."""
        if self.require_all:
            return all(f.matches(file_info) for f in self.filters)
        else:
            return any(f.matches(file_info) for f in self.filters)
