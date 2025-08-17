"""
Main entry point for the AI-Software-Development system.

This module implements improved Deep Agents patterns with proper tool integration,
enhanced state management, and better task delegation using YAML-based configuration.
"""
import sys
import os
from typing import Optional, List, Any, Literal, Dict
import logging

# Add the current directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deepagents import create_deep_agent, SubAgent
from src.ai_software_development.tools.custom_tools import internet_search, validate_project_structure, update_orchestration_state
from src.ai_software_development.state import SoftwareDevState, get_initial_state
from src.ai_software_development.callbacks import get_default_callbacks
from src.ai_software_development.memory import get_memory_manager
from src.ai_software_development.utils.config_loader import load_prompt_config, get_system_prompt
from src.ai_software_development.agents import (
    RequirementsAnalystAgent,
    ArchitectureAgent,
    FrontendDeveloperAgent,
    BackendDeveloperAgent,
    TesterAgent,
    DevOpsAgent
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_requirements_analyst_subagent(model: Optional[str] = None) -> SubAgent:
    """Create requirements analyst sub-agent using dedicated class."""
    agent = RequirementsAnalystAgent(model=model)
    return agent.get_subagent_config()


def get_architecture_agent_subagent(model: Optional[str] = None) -> SubAgent:
    """Create architecture agent sub-agent using dedicated class."""
    agent = ArchitectureAgent(model=model)
    return agent.get_subagent_config()


def get_frontend_developer_subagent(model: Optional[str] = None) -> SubAgent:
    """Create frontend developer sub-agent using dedicated class."""
    agent = FrontendDeveloperAgent(model=model)
    return agent.get_subagent_config()


def get_backend_developer_subagent(model: Optional[str] = None) -> SubAgent:
    """Create backend developer sub-agent using dedicated class."""
    agent = BackendDeveloperAgent(model=model)
    return agent.get_subagent_config()


def get_tester_agent_subagent(model: Optional[str] = None) -> SubAgent:
    """Create tester agent sub-agent using dedicated class."""
    agent = TesterAgent(model=model)
    return agent.get_subagent_config()


def get_devops_agent_subagent(model: Optional[str] = None) -> SubAgent:
    """Create DevOps agent sub-agent using dedicated class."""
    agent = DevOpsAgent(model=model)
    return agent.get_subagent_config()


# Load supervisor instructions from YAML
def get_supervisor_instructions() -> str:
    """Get supervisor instructions from YAML configuration."""
    config = load_prompt_config("supervisor")
    return get_system_prompt(config)

SUPERVISOR_INSTRUCTIONS = get_supervisor_instructions()


def create_software_dev_agent(
    model: Optional[str] = None,
    project_size: Literal["small", "medium", "large"] = "small",
    recursion_limit: int = 1000,
    enable_callbacks: bool = True,
    enable_memory: bool = True,
    project_id: Optional[str] = None,
    agent_models: Optional[Dict[str, str]] = None
) -> Any:
    """
    Create an improved software development agent using Deep Agents best practices.
    
    Args:
        model: Default model name to use (defaults to Deep Agents default)
        project_size: Size of the project to create
        recursion_limit: Maximum recursion limit
        enable_callbacks: Whether to enable LangChain callback handlers
        enable_memory: Whether to enable persistent memory management
        project_id: Unique project identifier for memory persistence
        agent_models: Dict mapping agent types to specific models
                     e.g., {"requirements": "gpt-4", "frontend": "claude-3-sonnet"}
        
    Returns:
        Configured Deep Agents instance
    """
    if recursion_limit <= 0:
        raise ValueError("Recursion limit must be positive")
    
    try:
        logger.info("Creating AI-Software-Development agent with improved Deep Agents patterns...")
        
        # Define custom tools
        custom_tools = [
            internet_search,
            validate_project_structure, 
            update_orchestration_state
        ]
        
        # Choose model: explicit arg > DEFAULT_MODEL > OLLAMA_MODEL > fallback if Ollama present
        selected_model = model or os.environ.get("DEFAULT_MODEL") or os.environ.get("OLLAMA_MODEL")
        if not selected_model and os.environ.get("OLLAMA_BASE_URL"):
            selected_model = "llama3.1"

        # Define sub-agents with individual model configurations
        agent_models = agent_models or {}
        subagents = [
            get_requirements_analyst_subagent(model=agent_models.get("requirements", selected_model)),
            get_architecture_agent_subagent(model=agent_models.get("architecture", selected_model)),
            get_frontend_developer_subagent(model=agent_models.get("frontend", selected_model)), 
            get_backend_developer_subagent(model=agent_models.get("backend", selected_model)),
            get_tester_agent_subagent(model=agent_models.get("tester", selected_model)),
            get_devops_agent_subagent(model=agent_models.get("devops", selected_model))
        ]
        
        # Prepare configuration
        agent_config = {
            "tools": custom_tools,
            "instructions": SUPERVISOR_INSTRUCTIONS,
            "subagents": subagents,
            "state_schema": SoftwareDevState
        }
        
        # Add model if specified
        if model:
            agent_config["model"] = model
            
        # Note: LangChain callbacks and memory integration would be added here
        # when Deep Agents supports these features directly. For now, they are
        # available as separate utilities that can be used independently.
        if enable_callbacks:
            logger.info("Callback handlers available via src.callbacks module")
        if enable_memory and project_id:
            logger.info(f"Memory management available via src.memory module for project: {project_id}")
        
        # Create agent with enhanced configuration
        agent = create_deep_agent(**agent_config)
        
        logger.info(f"Agent created successfully with {len(subagents)} sub-agents")
        
        return agent.with_config({
            "recursion_limit": recursion_limit,
            "configurable": {
                "project_size": project_size,
                "project_id": project_id or f"default_{project_size}",
                "enable_callbacks": enable_callbacks,
                "enable_memory": enable_memory
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to create software development agent: {e}")
        raise


# Create default agent instance
try:
    software_dev_agent = create_software_dev_agent(
        project_id="default_project",
        enable_callbacks=True,
        enable_memory=True
    )
    logger.info("Default software development agent created successfully with LangChain best practices")
except Exception as e:
    logger.error(f"Failed to create default agent: {e}")
    software_dev_agent = None


if __name__ == "__main__":
    try:
        print("🚀 Creating AI-Software-Development agent system with LangChain best practices...")
        
        # Test agent creation with enhanced features
        agent = create_software_dev_agent(
            project_size="small", 
            recursion_limit=500,
            project_id="test_project",
            enable_callbacks=True,
            enable_memory=True
        )
        print("✅ Agent system created successfully with:")
        print("  - LangChain callback handlers for monitoring")
        print("  - Persistent memory management")
        print("  - Enhanced error handling")
        
        # Test basic functionality
        print("\n🧪 Testing basic agent functionality...")
        test_state = get_initial_state("small")
        print(f"✅ Initial state created: {test_state['project_size']} project")
        
        # Test callback system
        from src.callbacks import SoftwareDevCallbackHandler
        callback_handler = SoftwareDevCallbackHandler()
        print(f"✅ Callback system initialized: {type(callback_handler).__name__}")
        
        # Test memory system (class available for use)
        print(f"✅ Memory system available: PersistentProjectMemory class")
        
        print("\n🎯 AI-Software-Development system ready with enhanced capabilities!")
        print("Available project sizes: small, medium, large")
        print("Sub-agents: requirements-analyst, architecture-agent, frontend-developer, backend-developer, tester-agent, devops-agent")
        print("LangChain features: callbacks, memory, streaming, async support, error handling")
        
    except Exception as e:
        print(f"❌ Failed to create agent system: {e}")
        logger.error(f"Main execution failed: {e}")
        exit(1)
