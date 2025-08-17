"""
Architecture Agent - Specialized for system design and technical coordination.
"""
from typing import Optional, List, Dict, Any
from .base_agent import BaseAgent


class ArchitectureAgent(BaseAgent):
    """
    Architecture Agent that defines system architecture, creates ADRs, and handles escalations.
    Has access to validation tools and orchestration capabilities.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        custom_tools: Optional[List[str]] = None,
        config_override: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Architecture Agent.
        
        Args:
            model: Specific model for architecture decisions (e.g., 'gpt-4', 'claude-3-opus')
            custom_tools: Additional tools beyond the default ones
            config_override: Override specific configuration values
        """
        super().__init__(model, custom_tools, config_override)
    
    def get_config_name(self) -> str:
        """Return the YAML config file name."""
        return "architecture_agent"
    
    def get_default_tools(self) -> List[str]:
        """
        Default tools for architecture and coordination.
        
        Returns:
            List of tool names for system architecture
        """
        return [
            "internet_search",              # Research architecture patterns
            "validate_project_structure",   # Ensure project compliance
            "update_orchestration_state",   # Track project progress
            "write_file",                   # Create architecture documents
            "read_file",                    # Read existing documentation
            "edit_file",                    # Update architecture files
            "write_todos",                  # Manage project task board
        ]
    
    def get_specialized_capabilities(self) -> List[str]:
        """
        Get specialized capabilities of this agent.
        
        Returns:
            List of specialized capabilities
        """
        return [
            "System architecture design",
            "Architecture Decision Records (ADR) creation",
            "Technical task coordination and delegation",
            "Project structure validation",
            "OpenAPI specification design",
            "Escalation handling and resolution",
            "Cross-team technical communication"
        ]
