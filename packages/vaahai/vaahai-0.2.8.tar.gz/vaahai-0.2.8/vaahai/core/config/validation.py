"""
Configuration validation for Vaahai.

This module handles validating configuration values against their expected types and constraints.
"""

from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin, get_type_hints

from pydantic import BaseModel, ValidationError

from vaahai.core.config.enums import ReviewDepth, ReviewFocus, OutputFormat
from vaahai.core.config.models import VaahaiConfig


def validate_config_value(config: VaahaiConfig, key: str, value: Any) -> None:
    """
    Validate a configuration value against its expected type and constraints.
    
    Args:
        config: Current configuration object
        key: Configuration key using dot notation
        value: Value to validate
        
    Raises:
        ValueError: If the value is invalid
    """
    # Handle custom section specially - no validation
    if key.startswith("custom."):
        return
        
    # Split the key into parts
    parts = key.split(".")
    
    # Handle top-level keys
    if len(parts) == 1:
        if parts[0] not in VaahaiConfig.model_fields:
            raise ValueError(f"Unknown configuration key: {key}")
        return
        
    # Handle nested keys
    section, field = parts[0], parts[1]
    
    # Validate section
    if section not in VaahaiConfig.model_fields:
        raise ValueError(f"Unknown configuration section: {section}")
        
    # Get the section model
    section_model = VaahaiConfig.model_fields[section].annotation
    
    # Validate field
    if field not in section_model.model_fields:
        raise ValueError(f"Unknown configuration field: {key}")
        
    # Get the field type
    field_info = section_model.model_fields[field]
    field_type = field_info.annotation
    
    # Validate enum values
    if field_type == ReviewDepth:
        if not isinstance(value, ReviewDepth) and value not in [e.value for e in ReviewDepth]:
            raise ValueError(f"{key}: Value must be one of: {', '.join([repr(e.value) for e in ReviewDepth])}")
    elif field_type == ReviewFocus:
        if not isinstance(value, ReviewFocus) and value not in [e.value for e in ReviewFocus]:
            raise ValueError(f"{key}: Value must be one of: {', '.join([repr(e.value) for e in ReviewFocus])}")
    elif field_type == OutputFormat:
        if not isinstance(value, OutputFormat) and value not in [e.value for e in OutputFormat]:
            raise ValueError(f"{key}: Value must be one of: {', '.join([repr(e.value) for e in OutputFormat])}")
    # Validate boolean values
    elif field_type == bool:
        if not isinstance(value, bool) and not (isinstance(value, str) and value.lower() in ("true", "false", "yes", "no", "1", "0", "y", "n")):
            raise ValueError(f"{key}: Value must be a boolean")
    # Validate list values
    elif get_origin(field_type) == list:
        if not isinstance(value, list):
            raise ValueError(f"{key}: Value must be a list")
    # Validate string values
    elif field_type == str:
        if not isinstance(value, str):
            raise ValueError(f"{key}: Value must be a string")
    # Validate integer values
    elif field_type == int:
        if not isinstance(value, int) and not (isinstance(value, str) and value.isdigit()):
            raise ValueError(f"{key}: Value must be an integer")
    # Validate float values
    elif field_type == float:
        try:
            float(value)
        except (ValueError, TypeError):
            raise ValueError(f"{key}: Value must be a number")


def validate_config(config: VaahaiConfig) -> List[str]:
    """
    Validate the entire configuration and return a list of validation errors.
    
    Args:
        config: Configuration object to validate
        
    Returns:
        List of validation error messages, empty if configuration is valid
    """
    errors = []
    
    # Convert config to dict for validation
    config_dict = config.model_dump()
    
    # Validate each section
    for section, section_data in config_dict.items():
        if section in ("schema_version", "custom", "log_level", "cache_dir"):
            continue
            
        if not isinstance(section_data, dict):
            continue
            
        # Get the section model
        section_model = VaahaiConfig.model_fields[section].annotation
        
        # Validate each field in the section
        for field, value in section_data.items():
            key = f"{section}.{field}"
            try:
                validate_config_value(config, key, value)
            except ValueError as e:
                errors.append(str(e))
                
    # Also try full Pydantic validation
    try:
        VaahaiConfig.model_validate(config_dict)
    except ValidationError as e:
        for error in e.errors():
            loc = ".".join(str(loc_part) for loc_part in error["loc"])
            errors.append(f"{loc}: {error['msg']}")
            
    return errors
