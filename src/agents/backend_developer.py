"""
Backend Developer Agent - Specialized for server-side development.
"""
from typing import Optional, List, Dict, Any
from .base_agent import BaseAgent


class BackendDeveloperAgent(BaseAgent):
    """
    Backend Developer Agent that implements server-side code, APIs, and backend services.
    Optimized for API development, database design, and server architecture.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        custom_tools: Optional[List[str]] = None,
        config_override: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Backend Developer Agent.
        
        Args:
            model: Specific model for backend development (e.g., 'gpt-4', 'claude-3-opus')
            custom_tools: Additional tools beyond the default ones
            config_override: Override specific configuration values
        """
        super().__init__(model, custom_tools, config_override)
    
    def get_config_name(self) -> str:
        """Return the YAML config file name."""
        return "backend_developer"
    
    def get_default_tools(self) -> List[str]:
        """
        Default tools for backend development.
        
        Returns:
            List of tool names for server-side development
        """
        return [
            "write_file",          # Create backend services and code
            "read_file",           # Read existing backend code
            "edit_file",           # Update backend files
            "write_todos",         # Plan backend implementation tasks
        ]
    
    def get_specialized_capabilities(self) -> List[str]:
        """
        Get specialized capabilities of this agent.
        
        Returns:
            List of specialized capabilities
        """
        return [
            "REST/GraphQL API development",
            "Database schema design and optimization",
            "Authentication and authorization systems",
            "Microservices architecture",
            "Python/Node.js/Java backend development",
            "ORM and database integration",
            "API security and validation",
            "Performance optimization and caching",
            "Message queues and async processing"
        ]
