"""
Base agent class for Vaahai agents.

This module contains the base agent class that all Vaahai agents must inherit from.
"""

import os
from typing import Any, Dict, Optional

import autogen

from vaahai.core.config import config_manager


class VaahaiAgent:
    """
    Base class for all Vaahai agents, integrating with Microsoft's Autogen framework.
    
    All agents in Vaahai must use Autogen's framework classes to ensure proper
    multi-agent communication and orchestration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            config: Configuration dictionary for the agent
        """
        # Merge provided config with global config
        self.config = self._merge_with_global_config(config or {})
        self.autogen_agent = None  # Will be initialized by subclasses
        self.user_proxy = None  # Will be initialized by subclasses if needed
        
    def _merge_with_global_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge provided config with global config.
        
        Command-line arguments take precedence over global config.
        
        Args:
            config: Configuration dictionary from command-line arguments
            
        Returns:
            Merged configuration dictionary
        """
        merged_config = {}
        
        # Get API key from global config if available
        if config_manager.get("llm.api_key"):
            merged_config["api_key"] = config_manager.get("llm.api_key")
            
        # Get Autogen settings from global config
        if config_manager.get("autogen.enabled"):
            merged_config["autogen_enabled"] = config_manager.get("autogen.enabled")
        if config_manager.get("autogen.default_model"):
            merged_config["model"] = config_manager.get("autogen.default_model")
        if config_manager.get("autogen.temperature") is not None:
            merged_config["temperature"] = config_manager.get("autogen.temperature")
            
        # Override with environment variables if set
        if os.environ.get("OPENAI_API_KEY"):
            merged_config["api_key"] = os.environ.get("OPENAI_API_KEY")
            
        # Override with provided config (highest precedence)
        merged_config.update(config)
        
        return merged_config
        
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Run the agent.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            A dictionary containing the results
        """
        raise NotImplementedError("Subclasses must implement run method")
    
    def _create_autogen_config(self) -> Dict[str, Any]:
        """
        Create configuration for Autogen agents.
        
        Returns:
            A dictionary containing the Autogen configuration
        """
        # Check if we have an API key in the config or environment
        api_key = self.config.get("api_key", None)
        model = self.config.get("model", "gpt-3.5-turbo")
        temperature = self.config.get("temperature", 0)
        
        # If no API key is provided in config, use a dummy config for testing
        if not api_key:
            return {
                "config_list": [],  # Empty config list for testing
                "temperature": temperature,
                "use_dummy_config": True  # Flag to indicate we're using a dummy config
            }
        
        # Use the provided API key
        return {
            "config_list": [{"model": model, "api_key": api_key}],
            "temperature": temperature
        }
