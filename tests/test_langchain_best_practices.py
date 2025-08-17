"""
Tests for LangChain best practices implementation.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from main import create_software_dev_agent
from src.tools.custom_tools import internet_search
from src.state import SoftwareDevState, get_initial_state


class TestLangChainPatterns:
    """Test LangChain best practice patterns."""
    
    def test_tool_schema_validation(self):
        """Test that tools have proper schema validation."""
        # Test internet_search tool schema
        tool = internet_search
        
        # Verify tool has proper name and description
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert tool.name == "internet_search"
        assert "web search" in tool.description.lower()
        
        # Verify tool has proper args schema
        assert hasattr(tool, 'args_schema')
        
        # Test tool with valid input
        with patch('src.tools.custom_tools.get_tavily_client') as mock_client:
            mock_tavily = Mock()
            mock_tavily.search.return_value = {"results": []}
            mock_client.return_value = mock_tavily
            
            result = tool.invoke({"query": "test", "max_results": 3})
            assert isinstance(result, dict)


    def test_state_schema_compliance(self):
        """Test state schema follows LangChain patterns."""
        state = get_initial_state("small")
        
        # Verify state is a proper dictionary
        assert isinstance(state, dict)
        
        # Verify required DeepAgentState fields
        assert "messages" in state
        assert "files" in state
        assert isinstance(state["messages"], list)
        assert isinstance(state["files"], dict)
        
        # Verify custom state fields
        assert "project_size" in state
        assert "current_phase" in state
        assert "artifacts" in state
        assert "issues" in state
        assert "blocked_on" in state


    @patch('main.create_deep_agent')
    def test_agent_configuration_patterns(self, mock_create_deep_agent):
        """Test agent follows proper configuration patterns."""
        mock_agent = Mock()
        mock_agent.with_config.return_value = mock_agent
        mock_create_deep_agent.return_value = mock_agent
        
        # Test with configuration
        agent = create_software_dev_agent(
            model="test-model",
            project_size="medium",
            recursion_limit=2000
        )
        
        # Verify create_deep_agent was called with proper arguments
        args, kwargs = mock_create_deep_agent.call_args
        
        # Check tools are provided
        assert "tools" in kwargs
        assert len(kwargs["tools"]) > 0
        
        # Check instructions are provided
        assert "instructions" in kwargs
        assert len(kwargs["instructions"]) > 0
        
        # Check subagents are provided
        assert "subagents" in kwargs
        assert len(kwargs["subagents"]) > 0
        
        # Check state schema is provided
        assert "state_schema" in kwargs
        assert kwargs["state_schema"] == SoftwareDevState
        
        # Check model is passed
        assert kwargs["model"] == "test-model"


class TestErrorHandlingPatterns:
    """Test error handling best practices."""
    
    def test_tool_error_handling(self):
        """Test tools handle errors gracefully."""
        # Test internet search with missing API key
        with patch.dict(os.environ, {}, clear=True):
            result = internet_search.invoke({"query": "test"})
            
            # Should return error dict, not raise exception
            assert isinstance(result, dict)
            assert "error" in result
            assert "results" in result
            assert result["results"] == []
    
    
    def test_validation_error_handling(self):
        """Test validation handles errors gracefully."""
        from src.tools.custom_tools import validate_project_structure
        
        # Test with invalid project size
        result = validate_project_structure.invoke({"project_size": "invalid"})
        
        assert isinstance(result, dict)
        assert result["valid"] is False
        assert "error" in result
    
    
    def test_state_error_recovery(self):
        """Test state management error recovery."""
        from src.tools.custom_tools import update_orchestration_state
        
        # Test with invalid JSON in existing file
        import tempfile
        import json
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create invalid JSON file
                os.makedirs(".orchestration", exist_ok=True)
                with open(".orchestration/state.json", 'w') as f:
                    f.write("invalid json content")
                
                # Should handle gracefully
                result = update_orchestration_state.invoke({
                    "phase": "TEST",
                    "artifacts": {"testing": True}
                })
                
                assert isinstance(result, dict)
                assert result["phase"] == "TEST"
                
            finally:
                os.chdir(original_cwd)


class TestMemoryAndContext:
    """Test memory and context management patterns."""
    
    def test_state_persistence_patterns(self):
        """Test state persistence follows best practices."""
        state1 = get_initial_state("small")
        state2 = get_initial_state("small")
        
        # States should be independent
        state1["current_phase"] = "ARCH"
        assert state2["current_phase"] == "REQ"
        
        # But structure should be consistent
        assert set(state1.keys()) == set(state2.keys())
    
    
    def test_context_isolation(self):
        """Test context isolation between operations."""
        from src.tools.custom_tools import update_orchestration_state
        
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create separate states
                state1 = update_orchestration_state.invoke({
                    "phase": "REQ",
                    "artifacts": {"requirements": True}
                })
                
                state2 = update_orchestration_state.invoke({
                    "phase": "ARCH", 
                    "artifacts": {"architecture": True}
                })
                
                # Second state should override first (same file)
                assert state2["phase"] == "ARCH"
                assert state2["artifacts"]["architecture"] is True
                # But should preserve previous data due to merge logic
                assert state2["artifacts"].get("requirements", False) is True
                
            finally:
                os.chdir(original_cwd)


class TestToolIntegrationPatterns:
    """Test tool integration best practices."""
    
    def test_tool_composition(self):
        """Test tools can be composed effectively."""
        from src.tools.custom_tools import validate_project_structure, update_orchestration_state
        
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Step 1: Validate (should fail)
                validation = validate_project_structure.invoke({"project_size": "small"})
                assert not validation["valid"]
                
                # Step 2: Update state with missing items
                state = update_orchestration_state.invoke({
                    "phase": "SETUP",
                    "issues": validation["missing"]
                })
                assert len(state["issues"]) > 0
                
                # Step 3: Create required files
                os.makedirs("docs", exist_ok=True)
                files_to_create = ["README.md", "TODO.md", "openapi.yaml", "Dockerfile"]
                for file_name in files_to_create:
                    with open(file_name, 'w') as f:
                        f.write("# Test content")
                with open("docs/architecture.md", 'w') as f:
                    f.write("# Architecture")
                
                # Step 4: Validate again (should pass)
                validation2 = validate_project_structure.invoke({"project_size": "small"})
                assert validation2["valid"] is True
                
            finally:
                os.chdir(original_cwd)
    
    
    def test_tool_parameter_validation(self):
        """Test tool parameter validation."""
        from src.tools.custom_tools import internet_search, validate_project_structure, update_orchestration_state
        
        # Test required parameters
        with pytest.raises(Exception):
            # Missing required query parameter
            internet_search.invoke({})
        
        with pytest.raises(Exception):
            # Missing required project_size parameter  
            validate_project_structure.invoke({})
        
        with pytest.raises(Exception):
            # Missing required phase parameter
            update_orchestration_state.invoke({})


class TestAgentCoordinationPatterns:
    """Test agent coordination best practices."""
    
    @patch('main.create_deep_agent')
    def test_subagent_configuration_consistency(self, mock_create_deep_agent):
        """Test subagent configurations are consistent."""
        mock_agent = Mock()
        mock_agent.with_config.return_value = mock_agent
        mock_create_deep_agent.return_value = mock_agent
        
        create_software_dev_agent()
        
        args, kwargs = mock_create_deep_agent.call_args
        subagents = kwargs["subagents"]
        
        # All subagents should have required fields
        required_fields = ["name", "description", "prompt", "tools"]
        for subagent in subagents:
            for field in required_fields:
                assert field in subagent
                assert isinstance(subagent[field], (str, list))
        
        # Names should be unique
        names = [agent["name"] for agent in subagents]
        assert len(names) == len(set(names))
    
    
    @patch('main.create_deep_agent')
    def test_tool_access_control(self, mock_create_deep_agent):
        """Test tool access control patterns."""
        mock_agent = Mock()
        mock_agent.with_config.return_value = mock_agent
        mock_create_deep_agent.return_value = mock_agent
        
        create_software_dev_agent()
        
        args, kwargs = mock_create_deep_agent.call_args
        subagents = kwargs["subagents"]
        
        # Find agents with internet access
        internet_agents = [
            agent for agent in subagents 
            if "internet_search" in agent.get("tools", [])
        ]
        
        # Only specific agents should have internet access
        expected_internet_agents = {"requirements-analyst", "architecture-agent"}
        actual_internet_agents = {agent["name"] for agent in internet_agents}
        
        assert actual_internet_agents == expected_internet_agents


@pytest.mark.slow
class TestPerformancePatterns:
    """Test performance-related patterns."""
    
    @patch('main.create_deep_agent')
    def test_configuration_caching(self, mock_create_deep_agent):
        """Test configuration caching patterns."""
        mock_agent = Mock()
        mock_agent.with_config.return_value = mock_agent
        mock_create_deep_agent.return_value = mock_agent
        
        # Create multiple agents
        agent1 = create_software_dev_agent()
        agent2 = create_software_dev_agent()
        
        # Should create separate instances
        assert mock_create_deep_agent.call_count == 2
    
    
    def test_state_efficiency(self):
        """Test state management efficiency."""
        import sys
        
        # Test memory efficiency of state creation
        state = get_initial_state("large")
        
        # State should not be excessively large
        state_size = sys.getsizeof(state)
        assert state_size < 10000  # Reasonable size limit
        
        # State should have efficient structure
        assert isinstance(state["artifacts"], dict)
        assert isinstance(state["issues"], list)
        assert isinstance(state["blocked_on"], list)
