"""
Main entry point for the AI-Software-Development system.

This version keeps all source under `src/` and avoids hard dependencies
at import time so tests can run without network/package installs.
"""
from __future__ import annotations

import os
import logging
from typing import Optional, Literal, Dict, Any, List

from deepagents import create_deep_agent, SubAgent  # type: ignore

# Local modules with minimal deps
from src.tools.custom_tools import internet_search, validate_project_structure, update_orchestration_state
from src.state import SoftwareDevState, get_initial_state

# YAML config loader for prompts
from src.utils.config_loader import load_prompt_config, get_system_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _load_agent_config(config_name: str) -> Dict[str, Any]:
    cfg = load_prompt_config(config_name)
    # Derive canonical machine name from config key to satisfy tests
    norm = config_name.replace("_", "-")
    return {
        "name": norm,
        "description": cfg["description"],
        "prompt": get_system_prompt(cfg),
        "tools": cfg.get("tools", []),
    }


def _subagent_with_model(base: Dict[str, Any], model: Optional[str]) -> Dict[str, Any]:
    if model:
        return {**base, "model": model}
    return base


def get_requirements_analyst_subagent(model: Optional[str] = None) -> SubAgent:
    base = _load_agent_config("requirements_analyst")
    return _subagent_with_model(base, model)


def get_architecture_agent_subagent(model: Optional[str] = None) -> SubAgent:
    base = _load_agent_config("architecture_agent")
    return _subagent_with_model(base, model)


def get_frontend_developer_subagent(model: Optional[str] = None) -> SubAgent:
    base = _load_agent_config("frontend_developer")
    return _subagent_with_model(base, model)


def get_backend_developer_subagent(model: Optional[str] = None) -> SubAgent:
    base = _load_agent_config("backend_developer")
    return _subagent_with_model(base, model)


def get_tester_agent_subagent(model: Optional[str] = None) -> SubAgent:
    base = _load_agent_config("tester_agent")
    return _subagent_with_model(base, model)


def get_devops_agent_subagent(model: Optional[str] = None) -> SubAgent:
    base = _load_agent_config("devops_agent")
    return _subagent_with_model(base, model)


def get_supervisor_instructions() -> str:
    cfg = load_prompt_config("supervisor")
    return get_system_prompt(cfg)


SUPERVISOR_INSTRUCTIONS = get_supervisor_instructions()


def create_software_dev_agent(
    model: Optional[str] = None,
    project_size: Literal["small", "medium", "large"] = "small",
    recursion_limit: int = 1000,
    enable_callbacks: bool = True,
    enable_memory: bool = True,
    project_id: Optional[str] = None,
    agent_models: Optional[Dict[str, str]] = None,
) -> Any:
    if recursion_limit <= 0:
        raise ValueError("Recursion limit must be positive")

    try:
        logger.info("Creating AI-Software-Development agent with improved Deep Agents patterns...")

        custom_tools = [internet_search, validate_project_structure, update_orchestration_state]

        selected_model = model or os.environ.get("DEFAULT_MODEL") or os.environ.get("OLLAMA_MODEL")
        if not selected_model and os.environ.get("OLLAMA_BASE_URL"):
            selected_model = "llama3.1"

        agent_models = agent_models or {}
        subagents: List[SubAgent] = [
            get_requirements_analyst_subagent(model=agent_models.get("requirements", selected_model)),
            get_architecture_agent_subagent(model=agent_models.get("architecture", selected_model)),
            get_frontend_developer_subagent(model=agent_models.get("frontend", selected_model)),
            get_backend_developer_subagent(model=agent_models.get("backend", selected_model)),
            get_tester_agent_subagent(model=agent_models.get("tester", selected_model)),
            get_devops_agent_subagent(model=agent_models.get("devops", selected_model)),
        ]

        agent_config: Dict[str, Any] = {
            "tools": custom_tools,
            "instructions": SUPERVISOR_INSTRUCTIONS,
            "subagents": subagents,
            "state_schema": SoftwareDevState,
        }
        if model:
            agent_config["model"] = model

        # Optional integrations (callbacks, memory) can be wired where needed

        agent = create_deep_agent(**agent_config)
        logger.info(f"Agent created successfully with {len(subagents)} sub-agents")

        return agent.with_config(
            {
                "recursion_limit": recursion_limit,
                "configurable": {
                    "project_size": project_size,
                    "project_id": project_id or f"default_{project_size}",
                    "enable_callbacks": enable_callbacks,
                    "enable_memory": enable_memory,
                },
            }
        )
    except Exception as e:
        logger.error(f"Failed to create software development agent: {e}")
        raise


# Optional: create a default instance on import, guarded for errors
try:  # pragma: no cover - side effect not essential for tests
    software_dev_agent = create_software_dev_agent(
        project_id="default_project", enable_callbacks=True, enable_memory=True
    )
    logger.info("Default software development agent created successfully")
except Exception as e:  # pragma: no cover
    logger.error(f"Failed to create default agent: {e}")
    software_dev_agent = None
