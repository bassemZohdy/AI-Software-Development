"""
Enhanced state schema for the AI-Software-Development system.
"""
from typing import Dict, List, Optional, Literal
from deepagents.state import DeepAgentState
from typing_extensions import TypedDict


class ProjectArtifacts(TypedDict, total=False):
    """Tracking of project artifacts completion."""
    requirements: bool
    architecture: bool
    adr: bool
    openapi: bool
    ux: bool
    run_instructions: bool
    testing: bool
    deployment: bool


class SoftwareDevState(DeepAgentState):
    """
    Enhanced state schema for software development projects.
    
    Extends DeepAgentState with project-specific tracking.
    """
    # Project metadata
    project_size: Optional[Literal["small", "medium", "large"]] = None
    current_phase: Optional[Literal["REQ", "ARCH", "UIUX", "FRONTEND", "BACKEND", "TEST", "OPS", "DONE"]] = None
    
    # Artifact tracking
    artifacts: Optional[ProjectArtifacts] = None
    
    # Issue and blocker tracking
    issues: List[str] = []
    blocked_on: List[str] = []
    
    # Agent assignment tracking
    agent_assignments: Dict[str, List[str]] = {}
    
    # Quality gates
    validation_passed: bool = False
    ready_for_delivery: bool = False


def get_initial_state(project_size: str = "small") -> SoftwareDevState:
    """Initialize the state for a new software development project."""
    return SoftwareDevState(
        messages=[],
        files={},
        project_size=project_size,
        current_phase="REQ",
        artifacts={
            "requirements": False,
            "architecture": False,
            "adr": False,
            "openapi": False,
            "ux": False,
            "run_instructions": False,
            "testing": False,
            "deployment": False
        },
        issues=[],
        blocked_on=[],
        agent_assignments={},
        validation_passed=False,
        ready_for_delivery=False
    )