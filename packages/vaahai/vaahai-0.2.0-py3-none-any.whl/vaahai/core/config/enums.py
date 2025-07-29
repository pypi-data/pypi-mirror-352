"""
Enum definitions for Vaahai configuration.

This module contains all enum types used in the configuration system.
"""

from enum import Enum


class ReviewDepth(str, Enum):
    """Review depth options."""
    QUICK = "quick"
    STANDARD = "standard"
    THOROUGH = "thorough"


class ReviewFocus(str, Enum):
    """Review focus options."""
    ALL = "all"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"


class OutputFormat(str, Enum):
    """Output format options."""
    TERMINAL = "terminal"
    MARKDOWN = "markdown"
    HTML = "html"
