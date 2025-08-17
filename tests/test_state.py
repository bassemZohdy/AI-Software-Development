"""
Tests for the enhanced state management system.
"""
import pytest
from src.state import SoftwareDevState, get_initial_state, ProjectArtifacts


class TestSoftwareDevState:
    """Test cases for SoftwareDevState."""
    
    def test_initial_state_creation(self):
        """Test creating initial state with default values."""
        state = get_initial_state()
        
        assert state["project_size"] == "small"
        assert state["current_phase"] == "REQ"
        assert state["artifacts"]["requirements"] is False
        assert state["artifacts"]["architecture"] is False
        assert state["issues"] == []
        assert state["blocked_on"] == []
        assert state["validation_passed"] is False
        assert state["ready_for_delivery"] is False
    
    def test_initial_state_with_custom_size(self):
        """Test creating initial state with custom project size."""
        state = get_initial_state("large")
        
        assert state["project_size"] == "large"
        assert state["current_phase"] == "REQ"
        assert isinstance(state["artifacts"], dict)
    
    def test_state_artifact_tracking(self):
        """Test artifact tracking functionality."""
        state = get_initial_state()
        
        # Initially all artifacts should be False
        artifacts = state["artifacts"]
        for artifact_name, completed in artifacts.items():
            assert completed is False
        
        # Expected artifact types
        expected_artifacts = {
            "requirements", "architecture", "adr", "openapi", 
            "ux", "run_instructions", "testing", "deployment"
        }
        assert set(artifacts.keys()) == expected_artifacts
    
    def test_state_phase_progression(self):
        """Test phase progression tracking."""
        state = get_initial_state()
        
        # Test phase progression
        phases = ["REQ", "ARCH", "UIUX", "FRONTEND", "BACKEND", "TEST", "OPS", "DONE"]
        
        for phase in phases:
            state["current_phase"] = phase
            assert state["current_phase"] == phase
    
    def test_issue_and_blocker_tracking(self):
        """Test issue and blocker tracking."""
        state = get_initial_state()
        
        # Add issues
        state["issues"].append("Missing API specification")
        state["blocked_on"].append("Waiting for requirements approval")
        
        assert len(state["issues"]) == 1
        assert len(state["blocked_on"]) == 1
        assert "Missing API specification" in state["issues"]
        assert "Waiting for requirements approval" in state["blocked_on"]
    
    def test_agent_assignment_tracking(self):
        """Test agent assignment tracking."""
        state = get_initial_state()
        
        # Assign tasks to agents
        state["agent_assignments"]["requirements-analyst"] = ["REQ-001", "REQ-002"]
        state["agent_assignments"]["architecture-agent"] = ["ADR-001"]
        
        assert len(state["agent_assignments"]) == 2
        assert "REQ-001" in state["agent_assignments"]["requirements-analyst"]
        assert "ADR-001" in state["agent_assignments"]["architecture-agent"]


class TestProjectArtifacts:
    """Test cases for ProjectArtifacts type."""
    
    def test_project_artifacts_structure(self):
        """Test ProjectArtifacts type structure."""
        artifacts = ProjectArtifacts()
        
        # All fields should be optional
        assert artifacts == {}
        
        # Can set individual fields
        artifacts["requirements"] = True
        artifacts["architecture"] = False
        
        assert artifacts["requirements"] is True
        assert artifacts["architecture"] is False
    
    def test_artifact_completion_tracking(self):
        """Test artifact completion tracking."""
        artifacts = ProjectArtifacts(
            requirements=True,
            architecture=True,
            adr=False,
            openapi=False
        )
        
        assert artifacts["requirements"] is True
        assert artifacts["architecture"] is True
        assert artifacts["adr"] is False
        assert artifacts["openapi"] is False


@pytest.mark.unit
class TestStateIntegration:
    """Integration tests for state management."""
    
    def test_state_workflow_progression(self):
        """Test complete workflow state progression."""
        state = get_initial_state("medium")
        
        # Phase 1: Requirements
        state["current_phase"] = "REQ"
        state["artifacts"]["requirements"] = True
        
        # Phase 2: Architecture 
        state["current_phase"] = "ARCH"
        state["artifacts"]["architecture"] = True
        state["artifacts"]["adr"] = True
        
        # Phase 3: Implementation
        state["current_phase"] = "FRONTEND"
        state["artifacts"]["ux"] = True
        
        # Validation checks
        assert state["project_size"] == "medium"
        assert state["current_phase"] == "FRONTEND"
        assert state["artifacts"]["requirements"] is True
        assert state["artifacts"]["architecture"] is True
        assert state["artifacts"]["adr"] is True
        assert state["artifacts"]["ux"] is True
    
    def test_quality_gate_validation(self):
        """Test quality gate validation."""
        state = get_initial_state()
        
        # Initially not ready
        assert state["validation_passed"] is False
        assert state["ready_for_delivery"] is False
        
        # Mark as validated
        state["validation_passed"] = True
        state["ready_for_delivery"] = True
        
        assert state["validation_passed"] is True
        assert state["ready_for_delivery"] is True