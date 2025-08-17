"""
DevOps Agent - Specialized for deployment automation and operations.
"""
from typing import Optional, List, Dict, Any
from .base_agent import BaseAgent


class DevOpsAgent(BaseAgent):
    """
    DevOps Agent that provides deployment automation, CI/CD, and operations infrastructure.
    Specialized in containerization, orchestration, and infrastructure as code.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        custom_tools: Optional[List[str]] = None,
        config_override: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize DevOps Agent.
        
        Args:
            model: Specific model for DevOps tasks (e.g., 'gpt-4', 'claude-3-opus')
            custom_tools: Additional tools beyond the default ones
            config_override: Override specific configuration values
        """
        super().__init__(model, custom_tools, config_override)
    
    def get_config_name(self) -> str:
        """Return the YAML config file name."""
        return "devops_agent"
    
    def get_default_tools(self) -> List[str]:
        """
        Default tools for DevOps and operations.
        
        Returns:
            List of tool names for deployment and operations
        """
        return [
            "write_file",          # Create deployment and infrastructure files
            "read_file",           # Read existing configuration
            "edit_file",           # Update deployment files
            "write_todos",         # Plan DevOps tasks
        ]
    
    def get_specialized_capabilities(self) -> List[str]:
        """
        Get specialized capabilities of this agent.
        
        Returns:
            List of specialized capabilities
        """
        return [
            "Docker containerization and optimization",
            "Kubernetes orchestration and deployment",
            "CI/CD pipeline design (GitHub Actions, GitLab CI)",
            "Infrastructure as Code (Terraform, CloudFormation)",
            "Cloud platform deployment (AWS, GCP, Azure)",
            "Monitoring and logging setup (Prometheus, ELK)",
            "Security scanning and compliance",
            "Load balancing and scaling strategies"
        ]
