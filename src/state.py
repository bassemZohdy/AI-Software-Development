"""
Minimal state definitions exposed at `src.state`.
"""
from __future__ import annotations

from typing import Dict

ProjectArtifacts = dict  # type: ignore


class SoftwareDevState:  # Only used as an identifier in tests
    pass


def get_initial_state(project_size: str = "small") -> Dict[str, object]:
    return {
        "messages": [],
        "files": {},
        "project_size": project_size,
        "current_phase": "REQ",
        "artifacts": {
            "requirements": False,
            "architecture": False,
            "adr": False,
            "openapi": False,
            "ux": False,
            "run_instructions": False,
            "testing": False,
            "deployment": False,
        },
        "issues": [],
        "blocked_on": [],
        "agent_assignments": {},
        "validation_passed": False,
        "ready_for_delivery": False,
    }

