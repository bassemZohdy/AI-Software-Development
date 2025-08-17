"""
Base agent class for all specialized agents in the AI-Software-Development system.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from deepagents import SubAgent
from ..utils.config_loader import load_prompt_config, get_system_prompt


class BaseAgent(ABC):
    """
    Base class for all specialized agents.
    
    Each agent can have its own model, tools, and configuration.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        custom_tools: Optional[List[str]] = None,
        config_override: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            model: Specific model to use for this agent
            custom_tools: Additional tools beyond the default ones
            config_override: Override specific configuration values
        """
        self.model = model
        self.custom_tools = custom_tools or []
        self.config_override = config_override or {}
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        try:
            self._config = load_prompt_config(self.get_config_name())
            # Apply any overrides
            if self.config_override:
                self._config.update(self.config_override)
        except Exception as e:
            raise RuntimeError(f"Failed to load config for {self.__class__.__name__}: {e}")
    
    @abstractmethod
    def get_config_name(self) -> str:
        """Return the name of the YAML config file (without extension)."""
        pass
    
    @abstractmethod
    def get_default_tools(self) -> List[str]:
        """Return the default tools for this agent."""
        pass
    
    def get_tools(self) -> List[str]:
        """Get all tools for this agent (default + custom)."""
        tools = self.get_default_tools().copy()
        tools.extend(self.custom_tools)
        return list(set(tools))  # Remove duplicates
    
    def get_subagent_config(self) -> SubAgent:
        """
        Create the SubAgent configuration for Deep Agents.
        
        Returns:
            SubAgent configuration dictionary
        """
        config = {
            "name": self._config["name"].lower().replace(" ", "-"),
            "description": self._config["description"],
            "prompt": get_system_prompt(self._config),
            "tools": self.get_tools()
        }
        
        # Add model if specified
        if self.model:
            config["model"] = self.model
            
        return config
    
    def get_name(self) -> str:
        """Get the agent name."""
        return self._config["name"]
    
    def get_description(self) -> str:
        """Get the agent description."""
        return self._config["description"]
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.get_name()}', model='{self.model}')"
