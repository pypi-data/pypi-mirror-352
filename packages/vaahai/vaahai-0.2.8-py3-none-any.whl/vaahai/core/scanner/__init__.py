"""
Code Scanner module for identifying and processing code files.

This module provides functionality to scan directories, resolve file paths,
filter files based on inclusion/exclusion rules, and extract file metadata.
"""

from vaahai.core.scanner.scanner import CodeScanner, FileInfo
from vaahai.core.scanner.filters import FileFilter, LanguageFilter, SizeFilter

# Create a singleton instance of the CodeScanner
code_scanner = CodeScanner()

__all__ = ["code_scanner", "CodeScanner", "FileInfo", "FileFilter", "LanguageFilter", "SizeFilter"]
