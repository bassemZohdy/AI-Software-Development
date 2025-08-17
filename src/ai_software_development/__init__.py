"""
AI-Software-Development system - A modular, multi-agent system for end-to-end software development.

This package provides specialized agents that collaborate across requirements, architecture,
frontend, backend, testing, and DevOps using shared state and tools.
"""
from .state import SoftwareDevState, get_initial_state
from .callbacks import get_default_callbacks
from .memory import get_memory_manager

__all__ = [
    "SoftwareDevState",
    "get_initial_state",
    "get_default_callbacks", 
    "get_memory_manager"
]
