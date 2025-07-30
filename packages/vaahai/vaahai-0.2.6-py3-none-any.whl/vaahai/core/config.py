"""
Configuration management for Vaahai.

This module is maintained for backward compatibility.
All functionality has been moved to the vaahai.core.config package.
"""

import warnings

# Import and re-export everything from the new package
from vaahai.core.config import (
    config_manager,
    ConfigManager,
    VaahaiConfig,
    LLMConfig,
    ReviewConfig,
    AnalyzeConfig,
    DocumentConfig,
    ExplainConfig,
    ReviewDepth,
    ReviewFocus,
    OutputFormat,
    validate_config,
    validate_config_value,
    migrate_schema,
    CURRENT_SCHEMA_VERSION,
)

# Emit a deprecation warning
warnings.warn(
    "The vaahai.core.config module is deprecated. "
    "Please import from vaahai.core.config package instead.",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility, create an instance that can be imported directly
# This ensures that code importing from the old location still works
__all__ = [
    "config_manager",
    "ConfigManager",
    "VaahaiConfig",
    "LLMConfig",
    "ReviewConfig",
    "AnalyzeConfig",
    "DocumentConfig",
    "ExplainConfig",
    "ReviewDepth",
    "ReviewFocus",
    "OutputFormat",
    "validate_config",
    "validate_config_value",
    "migrate_schema",
    "CURRENT_SCHEMA_VERSION",
]
