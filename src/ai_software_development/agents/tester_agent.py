"""
Tester Agent - Specialized for quality assurance and testing.
"""
from typing import Optional, List, Dict, Any
from .base_agent import BaseAgent


class TesterAgent(BaseAgent):
    """
    Tester Agent that creates tests, validates implementation against requirements,
    and ensures quality. Specialized in test automation and quality assurance.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        custom_tools: Optional[List[str]] = None,
        config_override: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Tester Agent.
        
        Args:
            model: Specific model for testing and QA (e.g., 'gpt-4', 'claude-3-sonnet')
            custom_tools: Additional tools beyond the default ones
            config_override: Override specific configuration values
        """
        super().__init__(model, custom_tools, config_override)
    
    def get_config_name(self) -> str:
        """Return the YAML config file name."""
        return "tester_agent"
    
    def get_default_tools(self) -> List[str]:
        """
        Default tools for testing and quality assurance.
        
        Returns:
            List of tool names for testing
        """
        return [
            "write_file",          # Create test files and scripts
            "read_file",           # Read existing code and tests
            "edit_file",           # Update test files
            "write_todos",         # Plan testing tasks
        ]
    
    def get_specialized_capabilities(self) -> List[str]:
        """
        Get specialized capabilities of this agent.
        
        Returns:
            List of specialized capabilities
        """
        return [
            "Unit test creation (pytest, Jest, JUnit)",
            "Integration test development",
            "End-to-end test automation",
            "Test data generation and management",
            "Performance and load testing",
            "Security testing and validation",
            "Test coverage analysis",
            "CI/CD test integration",
            "Bug reporting and tracking"
        ]
