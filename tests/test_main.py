"""
Tests for the main agent creation and configuration.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.main import (
    create_software_dev_agent,
    get_requirements_analyst_subagent,
    get_architecture_agent_subagent,
    get_frontend_developer_subagent,
    get_backend_developer_subagent,
    get_tester_agent_subagent,
    get_devops_agent_subagent,
    SUPERVISOR_INSTRUCTIONS
)
from src.state import SoftwareDevState


class TestSubAgentConfigurations:
    """Test cases for sub-agent configurations."""
    
    def test_requirements_analyst_subagent(self):
        """Test requirements analyst sub-agent configuration."""
        subagent = get_requirements_analyst_subagent()
        
        assert subagent["name"] == "requirements-analyst"
        assert "requirements" in subagent["description"].lower()
        assert "internet access" in subagent["description"].lower()
        assert "internet_search" in subagent["tools"]
        assert "write_todos" in subagent["prompt"]
        assert "REQ-" in subagent["prompt"]  # Check for requirement ID format
    
    def test_architecture_agent_subagent(self):
        """Test architecture agent sub-agent configuration."""
        subagent = get_architecture_agent_subagent()
        
        assert subagent["name"] == "architecture-agent"
        assert "architecture" in subagent["description"].lower()
        assert "escalations" in subagent["description"].lower()
        assert "internet_search" in subagent["tools"]
        assert "validate_project_structure" in subagent["tools"]
        assert "TODO.md" in subagent["prompt"]
        assert "ADR" in subagent["prompt"]
    
    def test_frontend_developer_subagent(self):
        """Test frontend developer sub-agent configuration."""
        subagent = get_frontend_developer_subagent()
        
        assert subagent["name"] == "frontend-developer"
        assert "client-side" in subagent["description"].lower()
        assert subagent["tools"] == []  # No special tools
        assert "FRONTEND:" in subagent["prompt"]
        assert "React" in subagent["prompt"] or "Vue" in subagent["prompt"]
    
    def test_backend_developer_subagent(self):
        """Test backend developer sub-agent configuration."""
        subagent = get_backend_developer_subagent()
        
        assert subagent["name"] == "backend-developer"
        assert "server-side" in subagent["description"].lower()
        assert subagent["tools"] == []  # No special tools
        assert "BACKEND:" in subagent["prompt"]
        assert "## Run" in subagent["prompt"]
    
    def test_tester_agent_subagent(self):
        """Test tester agent sub-agent configuration."""
        subagent = get_tester_agent_subagent()
        
        assert subagent["name"] == "tester-agent"
        assert "tests" in subagent["description"].lower()
        assert "quality" in subagent["description"].lower()
        assert subagent["tools"] == []  # No special tools
        assert "TEST:" in subagent["prompt"]
        assert "## Testing" in subagent["prompt"]
    
    def test_devops_agent_subagent(self):
        """Test DevOps agent sub-agent configuration."""
        subagent = get_devops_agent_subagent()
        
        assert subagent["name"] == "devops-agent"
        assert "deployment" in subagent["description"].lower()
        assert "automation" in subagent["description"].lower()
        assert subagent["tools"] == []  # No special tools
        assert "OPS:" in subagent["prompt"]
        assert "## Deployment" in subagent["prompt"]


class TestSupervisorInstructions:
    """Test cases for supervisor instructions."""
    
    def test_supervisor_instructions_content(self):
        """Test supervisor instructions contain required elements."""
        instructions = SUPERVISOR_INSTRUCTIONS
        
        # Check workflow is defined
        assert "requirements-analyst" in instructions
        assert "architecture-agent" in instructions
        assert "frontend-developer" in instructions
        assert "backend-developer" in instructions
        assert "tester-agent" in instructions
        assert "devops-agent" in instructions
        
        # Check project sizes are defined
        assert "small:" in instructions
        assert "medium:" in instructions
        assert "large:" in instructions
        
        # Check tool usage is mentioned
        assert "write_todos" in instructions
        assert "task:" in instructions
        assert "validate_project_structure" in instructions
        
        # Check quality gates are mentioned
        assert "Quality gates" in instructions or "QUALITY GATES" in instructions
        assert "README" in instructions
        assert "TODO.md" in instructions


class TestCreateSoftwareDevAgent:
    """Test cases for main agent creation function."""
    
    @patch('src.main.create_deep_agent')
    def test_create_software_dev_agent_default(self, mock_create_deep_agent):
        """Test creating agent with default parameters."""
        mock_agent = Mock()
        mock_agent.with_config.return_value = mock_agent
        mock_create_deep_agent.return_value = mock_agent
        
        result = create_software_dev_agent()
        
        # Verify create_deep_agent was called
        mock_create_deep_agent.assert_called_once()
        args, kwargs = mock_create_deep_agent.call_args
        
        # Check tools were passed
        assert len(kwargs["tools"]) == 3  # internet_search, validate_project_structure, update_orchestration_state
        
        # Check instructions were passed
        assert kwargs["instructions"] == SUPERVISOR_INSTRUCTIONS
        
        # Check subagents were configured
        assert len(kwargs["subagents"]) == 6
        subagent_names = [agent["name"] for agent in kwargs["subagents"]]
        assert "requirements-analyst" in subagent_names
        assert "architecture-agent" in subagent_names
        
        # Check state schema
        assert kwargs["state_schema"] == SoftwareDevState
        
        # Check agent configuration
        mock_agent.with_config.assert_called_once()
        config = mock_agent.with_config.call_args[0][0]
        assert config["recursion_limit"] == 1000
        assert config["configurable"]["project_size"] == "small"
    
    @patch('src.main.create_deep_agent')
    def test_create_software_dev_agent_custom_params(self, mock_create_deep_agent):
        """Test creating agent with custom parameters."""
        mock_agent = Mock()
        mock_agent.with_config.return_value = mock_agent
        mock_create_deep_agent.return_value = mock_agent
        
        result = create_software_dev_agent(
            model="custom-model",
            project_size="large",
            recursion_limit=2000
        )
        
        args, kwargs = mock_create_deep_agent.call_args
        
        # Check custom model was passed
        assert kwargs["model"] == "custom-model"
        
        # Check configuration
        config = mock_agent.with_config.call_args[0][0]
        assert config["recursion_limit"] == 2000
        assert config["configurable"]["project_size"] == "large"
    
    def test_create_software_dev_agent_invalid_recursion_limit(self):
        """Test creating agent with invalid recursion limit."""
        with pytest.raises(ValueError, match="Recursion limit must be positive"):
            create_software_dev_agent(recursion_limit=0)
        
        with pytest.raises(ValueError, match="Recursion limit must be positive"):
            create_software_dev_agent(recursion_limit=-1)
    
    @patch('src.main.create_deep_agent')
    def test_create_software_dev_agent_creation_failure(self, mock_create_deep_agent):
        """Test handling of agent creation failure."""
        mock_create_deep_agent.side_effect = Exception("Creation failed")
        
        with pytest.raises(Exception, match="Creation failed"):
            create_software_dev_agent()
    
    @patch('src.main.logger')
    @patch('src.main.create_deep_agent')
    def test_create_software_dev_agent_logging(self, mock_create_deep_agent, mock_logger):
        """Test that proper logging occurs during agent creation."""
        mock_agent = Mock()
        mock_agent.with_config.return_value = mock_agent
        mock_create_deep_agent.return_value = mock_agent
        
        create_software_dev_agent()
        
        # Check info logs were called
        mock_logger.info.assert_called()
        log_calls = [call.args[0] for call in mock_logger.info.call_args_list]
        
        # Should log about creating agent and successful creation
        assert any("Creating AI-Software-Development agent" in call for call in log_calls)
        assert any("successfully" in call for call in log_calls)


@pytest.mark.integration  
class TestMainIntegration:
    """Integration tests for main module."""
    
    @patch('src.main.create_deep_agent')
    def test_agent_creation_workflow(self, mock_create_deep_agent):
        """Test complete agent creation workflow."""
        mock_agent = Mock()
        mock_agent.with_config.return_value = mock_agent
        mock_create_deep_agent.return_value = mock_agent
        
        # Test different project sizes
        for project_size in ["small", "medium", "large"]:
            agent = create_software_dev_agent(project_size=project_size)
            
            assert agent is not None
            config = mock_agent.with_config.call_args[0][0]
            assert config["configurable"]["project_size"] == project_size
    
    @patch('src.main.create_deep_agent')
    def test_subagent_tools_assignment(self, mock_create_deep_agent):
        """Test that sub-agents get correct tool assignments."""
        mock_agent = Mock()
        mock_agent.with_config.return_value = mock_agent
        mock_create_deep_agent.return_value = mock_agent
        
        create_software_dev_agent()
        
        args, kwargs = mock_create_deep_agent.call_args
        subagents = kwargs["subagents"]
        
        # Find specific agents and check their tools
        analyst_agent = next(agent for agent in subagents if agent["name"] == "requirements-analyst")
        arch_agent = next(agent for agent in subagents if agent["name"] == "architecture-agent") 
        dev_agent = next(agent for agent in subagents if agent["name"] == "frontend-developer")
        
        # Analyst should have internet_search
        assert "internet_search" in analyst_agent["tools"]
        
        # Architecture agent should have multiple tools
        assert "internet_search" in arch_agent["tools"]
        assert "validate_project_structure" in arch_agent["tools"]
        
        # Developer agents should have no special tools
        assert dev_agent["tools"] == []


@pytest.mark.unit
class TestAgentValidation:
    """Unit tests for agent validation."""
    
    def test_all_subagents_have_required_fields(self):
        """Test that all sub-agents have required fields."""
        subagent_creators = [
            get_requirements_analyst_subagent,
            get_architecture_agent_subagent,
            get_frontend_developer_subagent,
            get_backend_developer_subagent,
            get_tester_agent_subagent,
            get_devops_agent_subagent
        ]
        
        for creator in subagent_creators:
            subagent = creator()
            
            # Required fields
            assert "name" in subagent
            assert "description" in subagent
            assert "prompt" in subagent
            assert "tools" in subagent
            
            # Field types
            assert isinstance(subagent["name"], str)
            assert isinstance(subagent["description"], str)
            assert isinstance(subagent["prompt"], str)
            assert isinstance(subagent["tools"], list)
            
            # Non-empty content
            assert len(subagent["name"]) > 0
            assert len(subagent["description"]) > 0
            assert len(subagent["prompt"]) > 0
    
    def test_subagent_names_are_unique(self):
        """Test that all sub-agent names are unique."""
        creators = [
            get_requirements_analyst_subagent,
            get_architecture_agent_subagent,
            get_frontend_developer_subagent,
            get_backend_developer_subagent,
            get_tester_agent_subagent,
            get_devops_agent_subagent
        ]
        
        names = [creator()["name"] for creator in creators]
        assert len(names) == len(set(names))  # All names should be unique
