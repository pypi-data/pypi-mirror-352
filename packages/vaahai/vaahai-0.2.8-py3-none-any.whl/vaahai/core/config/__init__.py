"""
Vaahai configuration package.

This package provides a configuration management system for Vaahai with the following features:
- Loading configuration from multiple sources with proper precedence
- Validation of configuration values
- Schema versioning and migration for backward compatibility
- Saving configuration to user and project files
"""

from vaahai.core.config.enums import ReviewDepth, ReviewFocus, OutputFormat
from vaahai.core.config.models import (
    VaahaiConfig, LLMConfig, ReviewConfig, AnalyzeConfig, 
    DocumentConfig, ExplainConfig, CURRENT_SCHEMA_VERSION
)
from vaahai.core.config.manager import ConfigManager
from vaahai.core.config.validation import validate_config, validate_config_value
from vaahai.core.config.migration import migrate_schema

# Create a singleton instance of the ConfigManager
config_manager = ConfigManager()

# Export the singleton instance as the default export
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
