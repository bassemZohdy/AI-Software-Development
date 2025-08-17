"""
Tests for custom tools implementation.
"""
import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from src.tools.custom_tools import (
    internet_search, 
    validate_project_structure, 
    update_orchestration_state,
    get_tavily_client
)


class TestInternetSearch:
    """Test cases for internet search tool."""
    
    def test_internet_search_success(self, mock_tavily_client, mock_env_vars):
        """Test successful internet search."""
        result = internet_search.invoke({"query": "test query"})
        
        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test Result"
        mock_tavily_client.search.assert_called_once()
    
    def test_internet_search_with_params(self, mock_tavily_client, mock_env_vars):
        """Test internet search with custom parameters."""
        result = internet_search.invoke({
            "query": "test query", 
            "max_results": 10,
            "topic": "news",
            "include_raw_content": True
        })
        
        mock_tavily_client.search.assert_called_with(
            "test query",
            max_results=10,
            include_raw_content=True,
            topic="news"
        )
        assert "results" in result
    
    def test_internet_search_api_key_missing(self):
        """Test internet search without API key."""
        with patch.dict(os.environ, {}, clear=True):
            result = internet_search.invoke({"query": "test query"})
            
            assert "error" in result
            assert "TAVILY_API_KEY" in result["error"]
            assert result["results"] == []
    
    def test_internet_search_client_error(self, mock_env_vars):
        """Test internet search with client error."""
        with patch('src.tools.custom_tools.get_tavily_client') as mock_get_client:
            mock_get_client.side_effect = Exception("Connection error")
            
            result = internet_search.invoke({"query": "test query"})
            
            assert "error" in result
            assert "Connection error" in result["error"]
            assert result["results"] == []
    
    def test_get_tavily_client_success(self, mock_env_vars):
        """Test successful Tavily client creation."""
        with patch('src.tools.custom_tools.TavilyClient') as mock_client:
            client = get_tavily_client()
            mock_client.assert_called_once_with(api_key="test-api-key")
    
    def test_get_tavily_client_no_key(self):
        """Test Tavily client creation without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="TAVILY_API_KEY"):
                get_tavily_client()


class TestValidateProjectStructure:
    """Test cases for project structure validation."""
    
    def test_validate_small_project_success(self, temp_dir, sample_project_files):
        """Test validation of small project structure."""
        # Create openapi.yaml file
        with open("openapi.yaml", 'w') as f:
            f.write("openapi: 3.0.0\ninfo:\n  title: Test API")
        
        result = validate_project_structure.invoke({"project_size": "small"})
        
        assert result["valid"] is True
        assert result["project_size"] == "small"
        assert len(result["missing"]) == 0
        assert "README.md" in result["expected"]
        assert "TODO.md" in result["expected"]
    
    def test_validate_small_project_missing_files(self, temp_dir):
        """Test validation with missing files."""
        result = validate_project_structure.invoke({"project_size": "small"})
        
        assert result["valid"] is False
        assert len(result["missing"]) > 0
        assert "README.md" in result["missing"]
        assert "TODO.md" in result["missing"]
    
    def test_validate_medium_project_structure(self, temp_dir):
        """Test validation of medium project structure."""
        # Create required files and directories
        with open("README.md", 'w') as f:
            f.write("# Test Project")
        with open("TODO.md", 'w') as f:
            f.write("# Tasks")
        with open("docker-compose.yaml", 'w') as f:
            f.write("version: '3'")
        with open("Dockerfile", 'w') as f:
            f.write("FROM python:3.9")
        
        os.makedirs("design", exist_ok=True)
        os.makedirs("services", exist_ok=True)
        
        result = validate_project_structure.invoke({"project_size": "medium"})
        
        assert result["valid"] is True
        assert result["project_size"] == "medium"
        assert "design/" in result["expected"]
        assert "services/" in result["expected"]
    
    def test_validate_large_project_structure(self, temp_dir):
        """Test validation of large project structure."""
        # Create required files and directories
        files = ["README.md", "TODO.md", "docker-compose.yaml"]
        for file in files:
            with open(file, 'w') as f:
                f.write("test content")
        
        directories = ["docs/features", "services", "ci", "k8s"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        result = validate_project_structure.invoke({"project_size": "large"})
        
        assert result["valid"] is True
        assert result["project_size"] == "large"
        assert "docs/features/" in result["expected"]
        assert "services/" in result["expected"]
    
    def test_validate_unknown_project_size(self, temp_dir):
        """Test validation with unknown project size."""
        result = validate_project_structure.invoke({"project_size": "unknown"})
        
        assert result["valid"] is False
        assert "error" in result
        assert "Unknown project size" in result["error"]


class TestUpdateOrchestrationState:
    """Test cases for orchestration state management."""
    
    def test_update_orchestration_state_new_file(self, temp_dir):
        """Test creating new orchestration state file."""
        result = update_orchestration_state.invoke({
            "phase": "REQ",
            "artifacts": {"requirements": True},
            "issues": ["Test issue"],
            "blocked_on": ["Test blocker"]
        })
        
        assert result["phase"] == "REQ"
        assert result["artifacts"]["requirements"] is True
        assert "Test issue" in result["issues"]
        assert "Test blocker" in result["blocked_on"]
        
        # Check file was created
        assert os.path.exists(".orchestration/state.json")
        
        # Verify file contents
        with open(".orchestration/state.json", 'r') as f:
            saved_state = json.load(f)
        
        assert saved_state["phase"] == "REQ"
        assert saved_state["artifacts"]["requirements"] is True
    
    def test_update_orchestration_state_existing_file(self, temp_dir):
        """Test updating existing orchestration state file."""
        # Create initial state
        os.makedirs(".orchestration", exist_ok=True)
        initial_state = {
            "phase": "REQ", 
            "artifacts": {"requirements": True},
            "issues": [],
            "blocked_on": []
        }
        
        with open(".orchestration/state.json", 'w') as f:
            json.dump(initial_state, f)
        
        # Update state
        result = update_orchestration_state.invoke({
            "phase": "ARCH",
            "artifacts": {"requirements": True, "architecture": True},
            "issues": ["New issue"]
        })
        
        assert result["phase"] == "ARCH"
        assert result["artifacts"]["requirements"] is True
        assert result["artifacts"]["architecture"] is True
        assert "New issue" in result["issues"]
    
    def test_update_orchestration_state_partial_update(self, temp_dir):
        """Test partial state update."""
        # Create initial state
        os.makedirs(".orchestration", exist_ok=True)
        initial_state = {
            "phase": "REQ",
            "artifacts": {"requirements": True},
            "issues": ["Old issue"],
            "blocked_on": ["Old blocker"]
        }
        
        with open(".orchestration/state.json", 'w') as f:
            json.dump(initial_state, f)
        
        # Update only phase
        result = update_orchestration_state.invoke({"phase": "ARCH"})
        
        assert result["phase"] == "ARCH"
        assert result["artifacts"]["requirements"] is True  # Preserved
        assert "Old issue" in result["issues"]  # Preserved
        assert "Old blocker" in result["blocked_on"]  # Preserved
    
    def test_update_orchestration_state_invalid_json(self, temp_dir):
        """Test handling of corrupted JSON file."""
        # Create directory and invalid JSON file
        os.makedirs(".orchestration", exist_ok=True)
        with open(".orchestration/state.json", 'w') as f:
            f.write("invalid json content")
        
        # Should handle gracefully and create new state
        result = update_orchestration_state.invoke({
            "phase": "REQ",
            "artifacts": {"requirements": True}
        })
        
        assert result["phase"] == "REQ"
        assert result["artifacts"]["requirements"] is True


@pytest.mark.integration
class TestToolsIntegration:
    """Integration tests for tools working together."""
    
    def test_tools_workflow_integration(self, temp_dir, mock_tavily_client, mock_env_vars):
        """Test tools working together in a workflow."""
        # Step 1: Search for requirements
        search_result = internet_search.invoke({"query": "web development best practices"})
        assert "results" in search_result
        
        # Step 2: Validate project structure (should fail initially)
        validation_result = validate_project_structure.invoke({"project_size": "small"})
        assert validation_result["valid"] is False
        
        # Step 3: Update orchestration state
        state_result = update_orchestration_state.invoke({
            "phase": "REQ",
            "artifacts": {"requirements": False},
            "issues": validation_result["missing"]
        })
        assert state_result["phase"] == "REQ"
        assert len(state_result["issues"]) > 0
        
        # Step 4: Create required files
        for missing_file in validation_result["missing"]:
            if not missing_file.endswith('/'):
                os.makedirs(os.path.dirname(missing_file) or '.', exist_ok=True)
                with open(missing_file, 'w') as f:
                    f.write("test content")
            else:
                os.makedirs(missing_file, exist_ok=True)
        
        # Step 5: Validate again (should pass now)
        final_validation = validate_project_structure.invoke({"project_size": "small"})
        assert final_validation["valid"] is True
        
        # Step 6: Update final state
        final_state = update_orchestration_state.invoke({
            "phase": "ARCH",
            "artifacts": {"requirements": True}
        })
        assert final_state["phase"] == "ARCH"
        assert final_state["artifacts"]["requirements"] is True