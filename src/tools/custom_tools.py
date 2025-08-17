"""
Custom tools with minimal runtime deps so tests can import safely.

If LangChain's `tool` decorator is unavailable, we provide a lightweight
fallback that mimics the `.invoke()` interface and basic metadata.
"""
from __future__ import annotations

import os
import json
from typing import Literal, Optional, Any, Callable, Dict

# Try to import langchain's tool decorator; fall back to a shim if missing.
try:  # pragma: no cover - import guard behavior
    from langchain_core.tools import tool as lc_tool  # type: ignore
except Exception:  # pragma: no cover
    lc_tool = None

# Expose a placeholder so tests can patch TavilyClient at module path
TavilyClient = None  # type: ignore


def _tool_fallback(func: Callable[..., Any]) -> Any:
    """Wrap a function to provide a `.invoke()` method and metadata.

    - `.name`: function name
    - `.description`: function docstring or empty string
    - `.args_schema`: placeholder object to satisfy tests
    - `.invoke(input_dict)`: calls function with kwargs from dict
    """
    class ToolWrapper:
        def __init__(self, f: Callable[..., Any]):
            self._f = f
            self.name = f.__name__
            self.description = (f.__doc__ or "").strip()
            self.args_schema = object()  # placeholder for tests

        def invoke(self, input_dict: Dict[str, Any]) -> Any:
            return self._f(**input_dict)

        def __call__(self, *args: Any, **kwargs: Any) -> Any:  # direct call support
            return self._f(*args, **kwargs)

    return ToolWrapper(func)


def tool(func: Callable[..., Any]) -> Any:
    """Decorator resolving to LangChain's `tool` or a local fallback."""
    if lc_tool is not None:
        return lc_tool(func)
    return _tool_fallback(func)


def get_tavily_client():
    """Get a Tavily client instance using TAVILY_API_KEY.

    Import happens at call time to avoid hard dependency during import.
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is required")
    global TavilyClient  # use/initialize module-level symbol for patchability
    if TavilyClient is None:  # type: ignore
        try:  # Late import to avoid hard dependency for tests that mock this
            from tavily import TavilyClient as _TavilyClient  # type: ignore
            TavilyClient = _TavilyClient  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"Failed to import tavily client: {e}")
    return TavilyClient(api_key=api_key)  # type: ignore


@tool
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> dict:
    """Run a web search using Tavily (web search helper)."""
    try:
        client = get_tavily_client()
        return client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )
    except Exception as e:
        return {"error": f"Search failed: {str(e)}", "results": []}


@tool
def validate_project_structure(project_size: str) -> dict:
    """Validate expected files/folders by project size (small|medium|large)."""
    required_files = {
        "small": [
            "README.md",
            "TODO.md",
            "docs/architecture.md",
            "openapi.yaml",
            "Dockerfile",
        ],
        "medium": [
            "README.md", "TODO.md", "design/", "services/",
            "docker-compose.yaml", "Dockerfile",
        ],
        "large": [
            "README.md", "TODO.md", "docs/features/", "services/",
            "docker-compose.yaml", "ci/", "k8s/",
        ],
    }
    if project_size not in required_files:
        return {"valid": False, "error": f"Unknown project size: {project_size}"}

    expected = required_files[project_size]
    missing = [p for p in expected if not os.path.exists(p)]
    return {
        "valid": len(missing) == 0,
        "expected": expected,
        "missing": missing,
        "project_size": project_size,
    }


@tool
def update_orchestration_state(
    phase: str,
    artifacts: Optional[dict] = None,
    issues: Optional[list] = None,
    blocked_on: Optional[list] = None,
) -> dict:
    """Update orchestration state in .orchestration/state.json with merge semantics."""
    state_file = ".orchestration/state.json"
    os.makedirs(".orchestration", exist_ok=True)

    state: Dict[str, Any] = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            state = {}

    existing_artifacts = dict(state.get("artifacts", {}))
    if artifacts:
        existing_artifacts.update(artifacts)

    state.update({
        "phase": phase,
        "artifacts": existing_artifacts,
        "issues": issues or state.get("issues", []),
        "blocked_on": blocked_on or state.get("blocked_on", []),
    })

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    return state

