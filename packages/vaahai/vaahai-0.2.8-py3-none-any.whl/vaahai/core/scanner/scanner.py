"""
Code Scanner implementation for identifying and processing code files.
"""

import os
import glob
import fnmatch
import chardet
from pathlib import Path
from typing import List, Dict, Set, Optional, Union, Iterator, Any
from dataclasses import dataclass
import logging

from vaahai.core.scanner.filters import FileFilter

logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """Information about a scanned file."""
    path: str
    relative_path: str  # Path relative to the scan root
    size: int
    language: Optional[str] = None
    encoding: str = "utf-8"
    content: Optional[str] = None
    
    @property
    def extension(self) -> str:
        """Get the file extension."""
        return os.path.splitext(self.path)[1].lower()
    
    @property
    def filename(self) -> str:
        """Get the filename without path."""
        return os.path.basename(self.path)
    
    def load_content(self) -> str:
        """Load the file content with appropriate encoding."""
        if self.content is not None:
            return self.content
            
        try:
            with open(self.path, 'rb') as f:
                raw_content = f.read()
                
            # Detect encoding if not already known
            if self.encoding == "auto":
                detection = chardet.detect(raw_content)
                self.encoding = detection['encoding'] or 'utf-8'
                
            # Decode content with detected encoding
            self.content = raw_content.decode(self.encoding, errors='replace')
            return self.content
        except Exception as e:
            logger.error(f"Error loading content for {self.path}: {str(e)}")
            self.content = ""
            return ""


class CodeScanner:
    """
    Scanner for identifying and processing code files.
    
    Implements the singleton pattern to ensure only one scanner instance exists.
    """
    _instance = None
    
    # Default file extensions to include
    DEFAULT_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.cs', '.go', '.rb', '.php', '.html', '.css', '.scss', '.sass', '.less',
        '.md', '.rst', '.json', '.yaml', '.yml', '.toml', '.xml', '.sh', '.bash',
        '.sql', '.swift', '.kt', '.rs', '.dart'
    }
    
    # Default directories to exclude
    DEFAULT_EXCLUDE_DIRS = {
        '.git', '.svn', '.hg', 'node_modules', 'venv', '.venv', 'env',
        '__pycache__', '.pytest_cache', '.mypy_cache', '.idea', '.vscode',
        'build', 'dist', 'target', 'out', 'bin', 'obj', '.hidden'
    }
    
    # Language detection based on file extension
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.go': 'go',
        '.rb': 'ruby',
        '.php': 'php',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.md': 'markdown',
        '.rst': 'rst',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.xml': 'xml',
        '.sh': 'shell',
        '.bash': 'shell',
        '.sql': 'sql',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.rs': 'rust',
        '.dart': 'dart'
    }
    
    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of CodeScanner exists."""
        if cls._instance is None:
            cls._instance = super(CodeScanner, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the CodeScanner."""
        # Skip initialization if already initialized
        if getattr(self, '_initialized', False):
            return
            
        self._filters: List[FileFilter] = []
        self._include_extensions: Set[str] = self.DEFAULT_EXTENSIONS.copy()
        self._exclude_dirs: Set[str] = self.DEFAULT_EXCLUDE_DIRS.copy()
        self._exclude_patterns: List[str] = []
        self._include_patterns: List[str] = []
        self._max_file_size: int = 1024 * 1024  # 1MB default
        self._initialized = True
        
    def reset(self):
        """Reset scanner to default settings."""
        self._filters = []
        self._include_extensions = self.DEFAULT_EXTENSIONS.copy()
        self._exclude_dirs = self.DEFAULT_EXCLUDE_DIRS.copy()
        self._exclude_patterns = []
        self._include_patterns = []
        self._max_file_size = 1024 * 1024
        
    def add_filter(self, file_filter: FileFilter):
        """Add a filter to the scanner."""
        self._filters.append(file_filter)
        return self
        
    def set_include_extensions(self, extensions: List[str]):
        """Set file extensions to include."""
        self._include_extensions = {ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                                   for ext in extensions}
        return self
        
    def add_include_extensions(self, extensions: List[str]):
        """Add file extensions to include."""
        for ext in extensions:
            ext = ext.lower()
            if not ext.startswith('.'):
                ext = f'.{ext}'
            self._include_extensions.add(ext)
        return self
        
    def set_exclude_dirs(self, dirs: List[str]):
        """Set directories to exclude."""
        self._exclude_dirs = set(dirs)
        return self
        
    def add_exclude_dirs(self, dirs: List[str]):
        """Add directories to exclude."""
        self._exclude_dirs.update(dirs)
        return self
        
    def set_exclude_patterns(self, patterns: List[str]):
        """Set patterns to exclude."""
        self._exclude_patterns = patterns
        return self
        
    def add_exclude_pattern(self, pattern: str):
        """Add a pattern to exclude."""
        self._exclude_patterns.append(pattern)
        return self
        
    def set_include_patterns(self, patterns: List[str]):
        """Set patterns to include."""
        self._include_patterns = patterns
        return self
        
    def add_include_pattern(self, pattern: str):
        """Add a pattern to include."""
        self._include_patterns.append(pattern)
        return self
        
    def set_max_file_size(self, size_bytes: int):
        """Set maximum file size in bytes."""
        self._max_file_size = size_bytes
        return self
        
    def _is_excluded_dir(self, path: str) -> bool:
        """
        Check if a directory should be excluded.
        
        Args:
            path: Path to the directory
            
        Returns:
            True if the directory should be excluded, False otherwise
        """
        # Get the directory name (last part of the path)
        dir_name = os.path.basename(path)
        
        # Check if the directory name is in the excluded list
        if dir_name in self._exclude_dirs:
            return True
            
        # Also check if any part of the path matches excluded directories
        path_parts = Path(path).parts
        if any(excluded in path_parts for excluded in self._exclude_dirs):
            return True
            
        # Check if the path matches any exclude patterns
        if self._matches_pattern(path, self._exclude_patterns):
            return True
            
        return False
        
    def _matches_pattern(self, path: str, patterns: List[str]) -> bool:
        """Check if a path matches any of the patterns."""
        if not patterns:
            return False
            
        return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)
        
    def _should_include_file(self, path: str, size: int) -> bool:
        """Determine if a file should be included in scan results."""
        # Check file size
        if size > self._max_file_size:
            logger.debug(f"Skipping {path}: exceeds max file size ({size} > {self._max_file_size})")
            return False
            
        # Check if in excluded directory
        if self._is_excluded_dir(path):
            logger.debug(f"Skipping {path}: in excluded directory")
            return False
            
        # Check exclude patterns
        if self._matches_pattern(path, self._exclude_patterns):
            logger.debug(f"Skipping {path}: matches exclude pattern")
            return False
            
        # Check extension
        ext = os.path.splitext(path)[1].lower()
        extension_match = ext in self._include_extensions
        
        # Check include patterns
        pattern_match = self._matches_pattern(path, self._include_patterns)
        
        # If include patterns are specified, the file must match at least one
        if self._include_patterns:
            return pattern_match
        
        # If include extensions are specified, the file must match at least one
        if self._include_extensions:
            return extension_match
            
        # If neither include patterns nor extensions are specified, include the file
        return True
        
    def _detect_language(self, path: str) -> Optional[str]:
        """Detect the programming language based on file extension."""
        ext = os.path.splitext(path)[1].lower()
        return self.LANGUAGE_MAP.get(ext)
        
    def _detect_encoding(self, path: str) -> str:
        """Detect file encoding."""
        try:
            with open(path, 'rb') as f:
                raw_data = f.read(4096)  # Read first 4KB for detection
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception as e:
            logger.warning(f"Error detecting encoding for {path}: {str(e)}")
            return 'utf-8'
        
    def _create_file_info(self, path: str, root_path: str) -> FileInfo:
        """Create a FileInfo object for a file."""
        abs_path = os.path.abspath(path)
        rel_path = os.path.relpath(abs_path, os.path.abspath(root_path))
        size = os.path.getsize(abs_path)
        language = self._detect_language(abs_path)
        encoding = self._detect_encoding(abs_path)
        
        return FileInfo(
            path=abs_path,
            relative_path=rel_path,
            size=size,
            language=language,
            encoding=encoding
        )
        
    def _apply_filters(self, file_info: FileInfo) -> bool:
        """Apply all filters to a file."""
        return all(f.matches(file_info) for f in self._filters)
        
    def scan_path(self, path: str) -> List[FileInfo]:
        """
        Scan a path (file, directory, or glob pattern) and return matching files.
        
        Args:
            path: Path to scan (file, directory, or glob pattern)
            
        Returns:
            List of FileInfo objects for matching files
        """
        results: List[FileInfo] = []
        
        # Normalize path
        path = os.path.abspath(os.path.expanduser(path))
        
        # Handle glob patterns
        if any(char in path for char in ['*', '?', '[']):
            root_path = os.path.dirname(path) or '.'
            for file_path in glob.glob(path, recursive=True):
                if os.path.isfile(file_path):
                    try:
                        size = os.path.getsize(file_path)
                        if self._should_include_file(file_path, size):
                            file_info = self._create_file_info(file_path, root_path)
                            if self._apply_filters(file_info):
                                results.append(file_info)
                    except OSError as e:
                        logger.warning(f"Error accessing {file_path}: {str(e)}")
            return results
            
        # Handle single file
        if os.path.isfile(path):
            try:
                size = os.path.getsize(path)
                if self._should_include_file(path, size):
                    file_info = self._create_file_info(path, os.path.dirname(path) or '.')
                    if self._apply_filters(file_info):
                        results.append(file_info)
            except OSError as e:
                logger.warning(f"Error accessing {path}: {str(e)}")
            return results
            
        # Handle directory
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                # Modify dirs in-place to skip excluded directories
                dirs[:] = [d for d in dirs if not self._is_excluded_dir(os.path.join(root, d))]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        if self._should_include_file(file_path, size):
                            file_info = self._create_file_info(file_path, path)
                            if self._apply_filters(file_info):
                                results.append(file_info)
                    except OSError as e:
                        logger.warning(f"Error accessing {file_path}: {str(e)}")
            return results
            
        # Path doesn't exist
        logger.warning(f"Path does not exist: {path}")
        return []
        
    def scan_paths(self, paths: List[str]) -> List[FileInfo]:
        """
        Scan multiple paths and return matching files.
        
        Args:
            paths: List of paths to scan
            
        Returns:
            List of FileInfo objects for matching files
        """
        results = []
        for path in paths:
            results.extend(self.scan_path(path))
        return results
        
    def scan_and_load_content(self, paths: List[str]) -> List[FileInfo]:
        """
        Scan paths and load file content for all matching files.
        
        Args:
            paths: List of paths to scan
            
        Returns:
            List of FileInfo objects with content loaded
        """
        files = self.scan_paths(paths)
        for file in files:
            file.load_content()
        return files
