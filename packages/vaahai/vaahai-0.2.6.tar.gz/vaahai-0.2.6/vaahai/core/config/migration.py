"""
Configuration schema migration for Vaahai.

This module handles migrating configuration data from older schema versions
to the current version, ensuring backward compatibility.
"""

from typing import Any, Dict

from vaahai.core.config.models import CURRENT_SCHEMA_VERSION


def migrate_schema(config_data: Dict[str, Any], source: str) -> Dict[str, Any]:
    """
    Migrate configuration data from older schema versions to the current version.
    
    Args:
        config_data: Configuration data to migrate
        source: Source of the configuration data
        
    Returns:
        Migrated configuration data
    """
    # Get the schema version from the config data, default to 0 if not present
    schema_version = config_data.get("schema_version", 0)
    
    # If already at current version, no migration needed
    if schema_version == CURRENT_SCHEMA_VERSION:
        return config_data
        
    # Make a copy of the config data to avoid modifying the original
    migrated_data = config_data.copy()
    
    # Apply migrations based on schema version
    if schema_version < 1:
        # Migration from version 0 to 1
        print(f"Migrating {source} from schema version {schema_version} to version 1")
        
        # Example migration: rename old_field to new_field
        if "old_field" in migrated_data:
            migrated_data["new_field"] = migrated_data.pop("old_field")
            
        # Example migration: move nested field to new location
        if "old_section" in migrated_data and "nested_field" in migrated_data["old_section"]:
            if "new_section" not in migrated_data:
                migrated_data["new_section"] = {}
            migrated_data["new_section"]["new_nested_field"] = migrated_data["old_section"].pop("nested_field")
            
        # Example migration: convert string to enum
        if "review" in migrated_data and "depth" in migrated_data["review"]:
            depth = migrated_data["review"]["depth"]
            if depth == "deep":
                migrated_data["review"]["depth"] = "thorough"
                
        # Set the schema version to 1
        migrated_data["schema_version"] = 1
    
    # Add more migrations as needed for future schema versions
    # if schema_version < 2:
    #     # Migration from version 1 to 2
    #     ...
    
    # Set the schema version to the current version
    migrated_data["schema_version"] = CURRENT_SCHEMA_VERSION
    
    return migrated_data
