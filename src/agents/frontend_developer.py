"""
Frontend Developer Agent - Specialized for client-side development.
"""
from typing import Optional, List, Dict, Any
from .base_agent import BaseAgent


class FrontendDeveloperAgent(BaseAgent):
    """
    Frontend Developer Agent that implements client-side code and user interfaces.
    Optimized for modern frontend frameworks and UI/UX implementation.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        custom_tools: Optional[List[str]] = None,
        config_override: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Frontend Developer Agent.
        
        Args:
            model: Specific model for frontend development (e.g., 'claude-3-sonnet', 'gpt-4')
            custom_tools: Additional tools beyond the default ones
            config_override: Override specific configuration values
        """
        super().__init__(model, custom_tools, config_override)
    
    def get_config_name(self) -> str:
        """Return the YAML config file name."""
        return "frontend_developer"
    
    def get_default_tools(self) -> List[str]:
        """
        Default tools for frontend development.
        
        Returns:
            List of tool names for client-side development
        """
        return [
            "write_file",          # Create frontend components and code
            "read_file",           # Read existing frontend code
            "edit_file",           # Update frontend files
            "write_todos",         # Plan frontend implementation tasks
        ]
    
    def get_specialized_capabilities(self) -> List[str]:
        """
        Get specialized capabilities of this agent.
        
        Returns:
            List of specialized capabilities
        """
        return [
            "React/Vue/Angular component development",
            "Responsive design implementation",
            "CSS/SCSS/Tailwind styling",
            "JavaScript/TypeScript development",
            "Frontend testing (Jest, Cypress)",
            "Build tool configuration (Webpack, Vite)",
            "Accessibility (a11y) implementation",
            "Performance optimization"
        ]
