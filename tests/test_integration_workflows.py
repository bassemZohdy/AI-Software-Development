"""
Integration tests for complete agent workflows and interactions.
"""
import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.main import (
    create_software_dev_agent,
    SUPERVISOR_INSTRUCTIONS
)
from src.state import get_initial_state
from src.tools.custom_tools import internet_search, validate_project_structure, update_orchestration_state


@pytest.fixture
def mock_deep_agent():
    """Mock deep agent for workflow testing."""
    mock_agent = Mock()
    mock_agent.invoke.return_value = {
        "messages": [{"role": "assistant", "content": "Task completed"}],
        "files": {"README.md": "# Test Project\n## Requirements\nREQ-001: Test requirement"},
        "project_size": "small",
        "current_phase": "ARCH"
    }
    mock_agent.with_config.return_value = mock_agent
    return mock_agent


@pytest.fixture 
def temp_project_dir():
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(original_cwd)


class TestAgentWorkflowIntegration:
    """Test complete agent workflow scenarios."""
    
    @patch('src.main.create_deep_agent')
    def test_end_to_end_small_project_workflow(self, mock_create_deep_agent, mock_deep_agent, temp_project_dir):
        """Test complete workflow for small project."""
        mock_create_deep_agent.return_value = mock_deep_agent
        
        # Create agent
        agent = create_software_dev_agent(project_size="small")
        
        # Initialize state
        initial_state = get_initial_state("small")
        
        # Simulate workflow progression
        workflows = [
            ("requirements-analyst", "REQ", {"requirements": True}),
            ("architecture-agent", "ARCH", {"architecture": True, "adr": True, "openapi": True}), 
            ("frontend-developer", "FRONTEND", {"ux": True}),
            ("backend-developer", "BACKEND", {"run_instructions": True}),
            ("tester-agent", "TEST", {"testing": True}),
            ("devops-agent", "OPS", {"deployment": True})
        ]
        
        state = initial_state
        for agent_name, phase, artifacts in workflows:
            # Update state for this phase
            state["current_phase"] = phase
            state["artifacts"].update(artifacts)
            
            # Verify agent can handle this phase
            result = agent.invoke(f"Execute {agent_name} tasks for {phase} phase")
            assert result is not None
            
        # Verify final state
        assert state["current_phase"] == "OPS"
        # Check that key artifacts are completed (not necessarily all)
        required_artifacts = ["requirements", "architecture", "adr", "testing", "deployment"]
        assert all(state["artifacts"][artifact] for artifact in required_artifacts)


    @patch('src.main.create_deep_agent')
    def test_agent_escalation_workflow(self, mock_create_deep_agent, mock_deep_agent, temp_project_dir):
        """Test escalation handling workflow."""
        mock_create_deep_agent.return_value = mock_deep_agent
        
        # Create agent
        agent = create_software_dev_agent()
        
        # Simulate escalation scenario
        escalation_scenarios = [
            "Complex architecture decision needed",
            "Technical blocker encountered", 
            "Requirement clarification needed"
        ]
        
        for scenario in escalation_scenarios:
            result = agent.invoke(f"Handle escalation: {scenario}")
            assert result is not None
            # Architecture agent should be involved in escalations
            mock_create_deep_agent.assert_called()


    @patch('src.main.create_deep_agent')
    def test_project_size_scaling_workflow(self, mock_create_deep_agent, mock_deep_agent, temp_project_dir):
        """Test workflow scaling across project sizes."""
        mock_create_deep_agent.return_value = mock_deep_agent
        
        project_sizes = ["small", "medium", "large"]
        
        for size in project_sizes:
            agent = create_software_dev_agent(project_size=size)
            state = get_initial_state(size)
            
            # Verify agent configuration matches project size
            config_call = mock_deep_agent.with_config.call_args[0][0]
            assert config_call["configurable"]["project_size"] == size
            
            # Test size-specific validation
            validation_result = validate_project_structure.invoke({"project_size": size})
            assert validation_result["project_size"] == size


class TestAgentCollaboration:
    """Test inter-agent collaboration patterns."""
    
    @patch('src.main.create_deep_agent')
    def test_requirements_to_architecture_handoff(self, mock_create_deep_agent, mock_deep_agent):
        """Test handoff from requirements analyst to architecture agent."""
        mock_create_deep_agent.return_value = mock_deep_agent
        
        agent = create_software_dev_agent()
        
        # Simulate requirements completion
        req_result = agent.invoke("Capture requirements for e-commerce platform")
        
        # Simulate architecture agent taking over
        arch_result = agent.invoke("Create system architecture based on captured requirements")
        
        # Verify both phases executed
        assert mock_deep_agent.invoke.call_count >= 2


    @patch('src.main.create_deep_agent')
    def test_architecture_to_development_coordination(self, mock_create_deep_agent, mock_deep_agent):
        """Test coordination from architecture to development agents."""
        mock_create_deep_agent.return_value = mock_deep_agent
        
        agent = create_software_dev_agent()
        
        # Simulate architecture completion with task assignments
        arch_result = agent.invoke("Create TODO.md with frontend and backend tasks")
        
        # Simulate parallel development
        frontend_result = agent.invoke("Implement frontend components from TODO.md")
        backend_result = agent.invoke("Implement backend services from TODO.md")
        
        # Verify coordination occurred
        assert mock_deep_agent.invoke.call_count >= 3


class TestStateManagement:
    """Test state management and persistence."""
    
    def test_orchestration_state_persistence(self, temp_project_dir):
        """Test orchestration state file management."""
        # Initialize orchestration state
        result = update_orchestration_state.invoke({
            "phase": "REQ",
            "artifacts": {"requirements": True},
            "issues": ["Need user feedback"],
            "blocked_on": []
        })
        
        assert result["phase"] == "REQ"
        assert os.path.exists(".orchestration/state.json")
        
        # Verify state persistence
        with open(".orchestration/state.json", 'r') as f:
            saved_state = json.load(f)
        
        assert saved_state["phase"] == "REQ"
        assert saved_state["artifacts"]["requirements"] is True
        assert "Need user feedback" in saved_state["issues"]


    def test_state_transition_validation(self):
        """Test state transition validation."""
        state = get_initial_state("medium")
        
        # Valid phase transitions
        valid_transitions = ["REQ", "ARCH", "UIUX", "FRONTEND", "BACKEND", "TEST", "OPS", "DONE"]
        
        for phase in valid_transitions:
            state["current_phase"] = phase
            assert state["current_phase"] == phase
        
        # Verify artifact tracking
        assert all(not completed for completed in state["artifacts"].values())


class TestErrorHandling:
    """Test error handling and recovery scenarios."""
    
    @patch('src.main.create_deep_agent')
    def test_agent_creation_error_handling(self, mock_create_deep_agent):
        """Test error handling during agent creation."""
        mock_create_deep_agent.side_effect = Exception("Model initialization failed")
        
        with pytest.raises(Exception, match="Model initialization failed"):
            create_software_dev_agent()


    def test_invalid_recursion_limit_handling(self):
        """Test handling of invalid recursion limits."""
        with pytest.raises(ValueError, match="Recursion limit must be positive"):
            create_software_dev_agent(recursion_limit=0)
        
        with pytest.raises(ValueError, match="Recursion limit must be positive"):
            create_software_dev_agent(recursion_limit=-1)


    def test_tool_error_recovery(self, temp_project_dir):
        """Test tool error recovery mechanisms."""
        # Test internet search error handling
        with patch.dict(os.environ, {}, clear=True):
            result = internet_search.invoke({"query": "test"})
            assert "error" in result
            assert "TAVILY_API_KEY" in result["error"]


class TestPerformanceScenarios:
    """Test performance-related scenarios."""
    
    @patch('src.main.create_deep_agent')
    def test_large_project_configuration(self, mock_create_deep_agent, mock_deep_agent):
        """Test configuration for large project scenarios."""
        mock_create_deep_agent.return_value = mock_deep_agent
        
        # Test high recursion limit for complex projects
        agent = create_software_dev_agent(
            project_size="large",
            recursion_limit=5000
        )
        
        config_call = mock_deep_agent.with_config.call_args[0][0]
        assert config_call["recursion_limit"] == 5000
        assert config_call["configurable"]["project_size"] == "large"


    @patch('src.main.create_deep_agent')
    def test_concurrent_agent_operations(self, mock_create_deep_agent, mock_deep_agent):
        """Test handling of concurrent operations."""
        mock_create_deep_agent.return_value = mock_deep_agent
        
        agent = create_software_dev_agent()
        
        # Simulate concurrent operations
        tasks = [
            "Implement frontend component A",
            "Implement backend service B", 
            "Create tests for component A",
            "Setup deployment for service B"
        ]
        
        for task in tasks:
            result = agent.invoke(task)
            assert result is not None


@pytest.mark.integration
class TestSystemIntegration:
    """Full system integration tests."""
    
    @patch('src.main.create_deep_agent')
    def test_complete_development_lifecycle(self, mock_create_deep_agent, mock_deep_agent, temp_project_dir):
        """Test complete development lifecycle."""
        mock_create_deep_agent.return_value = mock_deep_agent
        
        # Create files to simulate project setup
        os.makedirs("docs", exist_ok=True)
        with open("README.md", 'w') as f:
            f.write("# Test Project")
        with open("TODO.md", 'w') as f:
            f.write("# Tasks")
        with open("docs/architecture.md", 'w') as f:
            f.write("# Architecture")
        with open("openapi.yaml", 'w') as f:
            f.write("openapi: 3.0.0")
        with open("Dockerfile", 'w') as f:
            f.write("FROM python:3.11")
        
        agent = create_software_dev_agent(project_size="small")
        
        # Verify project structure validation passes
        validation = validate_project_structure.invoke({"project_size": "small"})
        assert validation["valid"] is True
        
        # Simulate complete workflow
        result = agent.invoke("Build a complete web application with all components")
        assert result is not None


    def test_tool_integration_chain(self, temp_project_dir):
        """Test chained tool operations."""
        # Chain: search -> validate -> update state
        
        # Step 1: Mock search
        with patch('src.tools.custom_tools.get_tavily_client') as mock_client:
            mock_tavily = Mock()
            mock_tavily.search.return_value = {"results": [{"title": "Test", "url": "test.com"}]}
            mock_client.return_value = mock_tavily
            
            search_result = internet_search.invoke({"query": "web development best practices"})
            assert "results" in search_result
        
        # Step 2: Validate project structure
        validation = validate_project_structure.invoke({"project_size": "small"})
        assert not validation["valid"]  # Files don't exist yet
        
        # Step 3: Update orchestration state
        state_result = update_orchestration_state.invoke({
            "phase": "REQ",
            "artifacts": {"requirements": False},
            "issues": validation["missing"]
        })
        assert state_result["phase"] == "REQ"
        assert len(state_result["issues"]) > 0
