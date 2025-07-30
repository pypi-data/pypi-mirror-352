"""
Hello World Agent

A simple agent implementation to validate the Autogen integration framework.
This agent uses Microsoft's Autogen framework for agent communication.
"""

from typing import Dict, Any, Optional
import autogen
from .base import VaahaiAgent


class HelloWorldAgent(VaahaiAgent):
    """
    Simple Hello World agent for testing the Autogen integration.
    
    This agent demonstrates the basic usage of Microsoft's Autogen framework
    by creating an AssistantAgent and a UserProxyAgent for simple interaction.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Hello World agent.
        
        Args:
            config: Configuration dictionary for the agent
        """
        super().__init__(config)
        self.message = self.config.get("message", "Hello, World!")
        
        # Get Autogen config
        llm_config = self._create_autogen_config()
        
        # Check if we're using a dummy config (no API key)
        if llm_config.get("use_dummy_config", False):
            # For testing without API key, we'll create a simple agent without LLM
            self.autogen_agent = autogen.AssistantAgent(
                name="hello_world_agent",
                llm_config=None,  # No LLM config
                system_message=f"You are a simple Hello World agent. Always respond with: {self.message}"
            )
        else:
            # Initialize Autogen assistant agent with LLM
            self.autogen_agent = autogen.AssistantAgent(
                name="hello_world_agent",
                llm_config=llm_config,
                system_message=f"You are a simple Hello World agent. Always respond with: {self.message}"
            )
        
        # Initialize user proxy for interaction
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0
        )
        
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Run the Hello World agent using Autogen's conversation framework.
        
        Returns:
            A dictionary containing the success status and message
        """
        try:
            # Check if we're using a dummy config (no API key)
            if self._create_autogen_config().get("use_dummy_config", False):
                # For testing without API key, just return the message directly
                # but also include a warning about missing API key
                warning_message = (
                    "WARNING: No OpenAI API key provided. Running in limited mode.\n"
                    "To use full Autogen capabilities, set your API key using one of these methods:\n"
                    "1. Set the OPENAI_API_KEY environment variable\n"
                    "2. Provide the API key in the agent configuration\n"
                    "Example: vaahai helloworld --api-key your_api_key\n\n"
                    f"Message: {self.message}"
                )
                
                return {
                    "success": True,
                    "message": warning_message,
                    "agent_type": "hello_world",
                    "warning": "missing_api_key"
                }
            
            # Initialize chat between user proxy and assistant
            self.user_proxy.initiate_chat(
                self.autogen_agent,
                message="Say hello"
            )
            
            # Get the last message from the assistant
            last_message = self.user_proxy.chat_messages[self.autogen_agent.name][-1]["content"]
            
            return {
                "success": True,
                "message": last_message,
                "agent_type": "hello_world"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "agent_type": "hello_world"
            }
