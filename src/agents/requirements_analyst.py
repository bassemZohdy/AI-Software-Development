"""
Requirements Analyst Agent - Specialized for gathering and analyzing requirements.
"""
from typing import Optional, List, Dict, Any
from .base_agent import BaseAgent


class RequirementsAnalystAgent(BaseAgent):
    """
    Requirements Analyst Agent that captures unambiguous, testable requirements.
    Has internet access for research and specialized requirement gathering tools.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        custom_tools: Optional[List[str]] = None,
        config_override: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Requirements Analyst Agent.
        
        Args:
            model: Specific model for requirements analysis (e.g., 'gpt-4', 'claude-3')
            custom_tools: Additional tools beyond the default ones
            config_override: Override specific configuration values
        """
        super().__init__(model, custom_tools, config_override)
    
    def get_config_name(self) -> str:
        """Return the YAML config file name."""
        return "requirements_analyst"
    
    def get_default_tools(self) -> List[str]:
        """
        Default tools for requirements analysis.
        
        Returns:
            List of tool names for requirements gathering
        """
        return [
            "internet_search",      # Research similar projects and best practices
            "write_file",          # Create requirement documents
            "read_file",           # Read existing documentation
            "edit_file",           # Update requirement files
            "write_todos",         # Plan requirement gathering tasks
        ]
    
    def get_specialized_capabilities(self) -> List[str]:
        """
        Get specialized capabilities of this agent.
        
        Returns:
            List of specialized capabilities
        """
        return [
            "Requirements elicitation and analysis",
            "User story creation with acceptance criteria",
            "Requirements traceability (REQ-IDs)",
            "Non-functional requirements specification",
            "Stakeholder analysis and communication",
            "Requirements validation and verification"
        ]
