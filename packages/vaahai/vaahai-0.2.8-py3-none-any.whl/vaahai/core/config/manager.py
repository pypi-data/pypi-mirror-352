"""
Configuration manager for Vaahai.

This module contains the ConfigManager class that handles loading, saving, and
accessing configuration from multiple sources with proper precedence.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import tomli
import tomli_w

from vaahai.core.config.enums import ReviewDepth, ReviewFocus, OutputFormat
from vaahai.core.config.models import (
    VaahaiConfig, LLMConfig, ReviewConfig, AnalyzeConfig, 
    DocumentConfig, ExplainConfig, CURRENT_SCHEMA_VERSION
)
from vaahai.core.config.migration import migrate_schema
from vaahai.core.config.validation import validate_config_value, validate_config


# Constants
DEFAULT_CONFIG_FILENAME = ".vaahai.toml"
ENV_PREFIX = "VAAHAI_"


class ConfigManager:
    """Configuration manager for Vaahai.
    
    Handles loading, saving, and accessing configuration from multiple sources.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the configuration manager."""
        if self._initialized:
            return
            
        self._config = VaahaiConfig()
        self._config_sources: Dict[str, str] = {}  # Tracks where each setting came from
        self._loaded = False
        self._initialize_sources()
        self._initialized = True
    
    def _initialize_sources(self) -> None:
        """Initialize the sources tracking dictionary with default values."""
        self._config_sources = {}
        
        # Add review.* keys explicitly
        for field in ReviewConfig.model_fields:
            self._config_sources[f"review.{field}"] = "default"
        
        # Add llm.* keys explicitly
        for field in LLMConfig.model_fields:
            self._config_sources[f"llm.{field}"] = "default"
            
        # Add analyze.* keys explicitly
        for field in AnalyzeConfig.model_fields:
            self._config_sources[f"analyze.{field}"] = "default"
            
        # Add document.* keys explicitly
        for field in DocumentConfig.model_fields:
            self._config_sources[f"document.{field}"] = "default"
            
        # Add explain.* keys explicitly
        for field in ExplainConfig.model_fields:
            self._config_sources[f"explain.{field}"] = "default"
    
    def load(self, cli_args: Optional[Dict[str, Any]] = None) -> None:
        """
        Load configuration from all sources with proper precedence.
        
        Args:
            cli_args: Optional dictionary of CLI arguments to override config
        """
        # Start with default values (already in self._config)
        self._initialize_sources()
        
        # Load from project config file (lowest precedence)
        self._load_from_project_config()
        
        # Load from user config file (overrides project config)
        self._load_from_user_config()
        
        # Load from environment variables (overrides user and project config)
        self._load_from_env()
        
        # Apply CLI arguments (highest precedence)
        if cli_args:
            self._apply_cli_args(cli_args)
            
        self._loaded = True
    
    def _load_from_user_config(self) -> None:
        """Load configuration from user config file."""
        # Resolve user config path dynamically
        user_config_dir = Path(os.environ.get("HOME", str(Path.home()))) / ".config" / "vaahai"
        user_config_file = user_config_dir / "config.toml"
        
        if user_config_file.exists():
            try:
                with open(user_config_file, "rb") as f:
                    config_data = tomli.load(f)
                
                # Check for schema version and migrate if needed
                config_data = migrate_schema(config_data, "user config")
                
                self._update_config(config_data, "user config")
            except Exception as e:
                print(f"Error loading user config: {str(e)}")
    
    def _load_from_project_config(self) -> None:
        """Load configuration from project config file."""
        project_config_file = Path(os.getcwd()) / DEFAULT_CONFIG_FILENAME
        if project_config_file.exists():
            try:
                with open(project_config_file, "rb") as f:
                    config_data = tomli.load(f)
                
                # Check for schema version and migrate if needed
                config_data = migrate_schema(config_data, "project config")
                
                self._update_config(config_data, "project config")
            except Exception as e:
                print(f"Error loading project config: {str(e)}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_vars = {}
        
        # Process environment variables with VAAHAI_ prefix
        for key, value in os.environ.items():
            if key.startswith(ENV_PREFIX):
                # Convert VAAHAI_LLM_PROVIDER to llm.provider
                config_key = key[len(ENV_PREFIX):].lower().replace("_", ".")
                env_vars[config_key] = value
        
        if env_vars:
            # Convert string values to appropriate types
            processed_env_vars = {}
            for key, value in env_vars.items():
                # Handle enum values
                if key.endswith(".depth"):
                    try:
                        processed_env_vars[key] = ReviewDepth(value)
                    except ValueError:
                        print(f"Invalid depth value in environment: {value}")
                        continue
                elif key.endswith(".focus"):
                    try:
                        processed_env_vars[key] = ReviewFocus(value)
                    except ValueError:
                        print(f"Invalid focus value in environment: {value}")
                        continue
                elif key.endswith(".output_format"):
                    try:
                        processed_env_vars[key] = OutputFormat(value)
                    except ValueError:
                        print(f"Invalid output format in environment: {value}")
                        continue
                elif key.endswith(".interactive") or key.endswith(".save_history") or key.endswith(".private"):
                    processed_env_vars[key] = value.lower() in ("true", "yes", "1", "y")
                else:
                    processed_env_vars[key] = value
            
            # Update config with processed environment variables
            nested_env_vars = self._unflatten_dict(processed_env_vars)
            self._update_config(nested_env_vars, "environment")
    
    def _unflatten_dict(self, flat_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a flattened dictionary with dot notation to a nested dictionary.
        
        Args:
            flat_dict: Dictionary with keys using dot notation
            
        Returns:
            Nested dictionary
        """
        result = {}
        for key, value in flat_dict.items():
            parts = key.split(".")
            current = result
            
            # Navigate to the right place in the nested dict
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set the value
            current[parts[-1]] = value
            
        return result
    
    def _apply_cli_args(self, cli_args: Dict[str, Any]) -> None:
        """
        Apply CLI arguments to the configuration.
        
        Args:
            cli_args: Dictionary of CLI arguments
        """
        # Convert CLI args to nested dict
        nested_args = self._unflatten_dict(cli_args)
        
        # Update config with CLI args
        self._update_config(nested_args, "cli args")
    
    def _update_config(self, new_config: Dict[str, Any], source: str) -> None:
        """
        Update configuration with new values and track their source.
        
        Args:
            new_config: New configuration values
            source: Source of the configuration (e.g., "user config", "environment")
        """
        # Helper function to update nested dictionaries and track sources
        def update_nested(config_dict, update_dict, prefix=""):
            for key, value in update_dict.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict) and key in config_dict and key != "custom":
                    # Recursively update nested dictionaries
                    update_nested(config_dict[key], value, full_key)
                else:
                    # Update value and track source
                    if key == "custom" and isinstance(value, dict):
                        # Handle custom section specially
                        if "custom" not in config_dict:
                            config_dict["custom"] = {}
                        for custom_key, custom_value in value.items():
                            config_dict["custom"][custom_key] = custom_value
                            self._config_sources[f"custom.{custom_key}"] = source
                    else:
                        # Only update if the new source has higher precedence than the current source
                        current_source = self._config_sources.get(full_key, "unknown")
                        if self._source_has_higher_precedence(source, current_source):
                            config_dict[key] = value
                            self._config_sources[full_key] = source
        
        # Convert config to dict for updating
        config_dict = self._config.model_dump()
        update_nested(config_dict, new_config)
        
        # Update the config object with the modified dict
        self._config = VaahaiConfig.model_validate(config_dict)
    
    def _source_has_higher_precedence(self, new_source: str, current_source: str) -> bool:
        """
        Determine if a new source has higher precedence than the current source.
        
        Args:
            new_source: New configuration source
            current_source: Current configuration source
            
        Returns:
            True if new source has higher precedence, False otherwise
        """
        # Define precedence order (highest to lowest)
        precedence = [
            "cli args",
            "environment",
            "user config",
            "project config",
            "default",
            "unknown"
        ]
        
        try:
            new_index = precedence.index(new_source)
            current_index = precedence.index(current_source)
            return new_index < current_index
        except ValueError:
            # If source is not in the list, assume lowest precedence
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key using dot notation (e.g., "llm.provider")
            default: Default value if key is not found
            
        Returns:
            Configuration value or default if not found
        """
        if not self._loaded:
            self.load()
            
        # Handle custom section specially
        if key.startswith("custom."):
            _, custom_key = key.split(".", 1)
            return self._config.custom.get(custom_key, default)
            
        # Navigate through the nested config
        parts = key.split(".")
        current = self._config.model_dump()
        
        for part in parts:
            if part not in current:
                return default
            current = current[part]
            
        return current
    
    def get_source(self, key: str) -> str:
        """
        Get the source of a configuration value.
        
        Args:
            key: Configuration key using dot notation
            
        Returns:
            Source of the configuration value or "unknown"
        """
        if not self._loaded:
            self.load()
            
        return self._config_sources.get(key, "unknown")
    
    def set(self, key: str, value: Any, save: bool = False) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key using dot notation
            value: Value to set
            save: Whether to save to user config file
            
        Raises:
            ValueError: If the value is invalid for the specified key
        """
        if not self._loaded:
            self.load()
            
        # Validate the value
        validate_config_value(self._config, key, value)
            
        # Handle custom section specially
        if key.startswith("custom."):
            _, custom_key = key.split(".", 1)
            self._config.custom[custom_key] = value
            self._config_sources[key] = "user config"
            
            if save:
                self.save_user_config()
            return
            
        # Convert to dict for updating
        config_dict = self._config.model_dump()
        
        # Navigate to the right place in the nested dict
        parts = key.split(".")
        current = config_dict
        
        # Navigate to the parent of the target key
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
        
        # Update the config object and source tracking
        self._config = VaahaiConfig.model_validate(config_dict)
        self._config_sources[key] = "user config"
        
        # Save to file if requested
        if save:
            self.save_user_config()
    
    def validate_config(self) -> List[str]:
        """
        Validate the entire configuration and return a list of validation errors.
        
        Returns:
            List of validation error messages, empty if configuration is valid
        """
        return validate_config(self._config)
    
    def save_user_config(self) -> None:
        """Save current configuration to user config file."""
        # Resolve user config path dynamically
        user_config_dir = Path(os.environ.get("HOME", str(Path.home()))) / ".config" / "vaahai"
        user_config_file = user_config_dir / "config.toml"
        
        # Ensure directory exists
        user_config_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and ensure schema_version is set
        config_dict = self._config.model_dump()
        config_dict["schema_version"] = CURRENT_SCHEMA_VERSION
        
        # Clean up None values as they're not TOML serializable
        def clean_config(config_dict):
            result = {}
            for key, value in config_dict.items():
                if isinstance(value, dict):
                    cleaned = clean_config(value)
                    if cleaned:  # Only add non-empty dicts
                        result[key] = cleaned
                elif value is not None:
                    result[key] = value
            return result
        
        cleaned_config = clean_config(config_dict)
        cleaned_config["schema_version"] = CURRENT_SCHEMA_VERSION  # Ensure schema_version is preserved
        
        # Write to file
        with open(user_config_file, "wb") as f:
            tomli_w.dump(cleaned_config, f)
    
    def init_project_config(self, force: bool = False) -> bool:
        """
        Initialize a project configuration file in the current directory.
        
        Args:
            force: Whether to overwrite existing file
            
        Returns:
            True if file was created, False otherwise
        """
        project_config_file = Path(os.getcwd()) / DEFAULT_CONFIG_FILENAME
        
        if project_config_file.exists() and not force:
            return False
            
        # Create a default configuration
        config = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
            },
            "review": {
                "depth": "standard",
                "focus": "all",
            },
            "autogen": {
                "enabled": True,
                "default_model": "gpt-3.5-turbo",
                "temperature": 0,
                "use_docker": False,
            },
        }
        
        # Ensure parent directory exists
        project_config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the configuration
        with open(project_config_file, "wb") as f:
            tomli_w.dump(config, f)
            
        return True
    
    @property
    def config(self) -> VaahaiConfig:
        """Get the full configuration object."""
        if not self._loaded:
            self.load()
            
        return self._config
    
    def get_all_with_sources(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all configuration values with their sources.
        
        Returns:
            Dictionary mapping keys to dictionaries with 'value' and 'source' keys
        """
        if not self._loaded:
            self.load()
            
        result = {}
        
        # Helper function to flatten a nested dictionary with dot notation
        def _flatten_dict(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
            result = {}
            for key, value in d.items():
                new_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict) and key != "custom":
                    result.update(_flatten_dict(value, new_key))
                else:
                    result[new_key] = value
            return result
            
        # Flatten the config
        flat_config = _flatten_dict(self._config.model_dump())
        
        # Add custom fields
        for custom_key, custom_value in self._config.custom.items():
            flat_config[f"custom.{custom_key}"] = custom_value
            
        # Create result with values and sources
        for key, value in flat_config.items():
            result[key] = {
                "value": value,
                "source": self.get_source(key)
            }
            
        return result
