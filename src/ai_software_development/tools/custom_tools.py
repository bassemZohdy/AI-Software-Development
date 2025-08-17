"""
Custom tools for the AI-Software-Development system.
"""
import os
from typing import Literal, Optional
from langchain_core.tools import tool
from tavily import TavilyClient


# Initialize Tavily client for internet search
def get_tavily_client():
    """Get Tavily client with error handling."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is required")
    return TavilyClient(api_key=api_key)


@tool
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> dict:
    """
    Run a web search to gather information.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        topic: The topic category for the search
        include_raw_content: Whether to include raw content
        
    Returns:
        Dictionary containing search results
    """
    try:
        client = get_tavily_client()
        search_docs = client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )
        return search_docs
    except Exception as e:
        return {"error": f"Search failed: {str(e)}", "results": []}


@tool
def validate_project_structure(project_size: str) -> dict:
    """
    Validate that the project structure matches the expected size requirements.
    
    Args:
        project_size: The size of the project (small, medium, large)
        
    Returns:
        Dictionary with validation results
    """
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
            "docker-compose.yaml", "Dockerfile"
        ],
        "large": [
            "README.md", "TODO.md", "docs/features/", "services/", 
            "docker-compose.yaml", "ci/", "k8s/"
        ]
    }
    
    if project_size not in required_files:
        return {"valid": False, "error": f"Unknown project size: {project_size}"}
    
    expected = required_files[project_size]
    missing = []

    for entry in expected:
        if not os.path.exists(entry):
            missing.append(entry)
    
    return {
        "valid": len(missing) == 0,
        "expected": expected,
        "missing": missing,
        "project_size": project_size
    }


@tool 
def update_orchestration_state(
    phase: str,
    artifacts: Optional[dict] = None,
    issues: Optional[list] = None,
    blocked_on: Optional[list] = None
) -> dict:
    """
    Update the orchestration state file.
    
    Args:
        phase: Current project phase
        artifacts: Dictionary of artifact completion status
        issues: List of current issues
        blocked_on: List of blockers
        
    Returns:
        Updated state dictionary
    """
    state_file = ".orchestration/state.json"
    
    # Ensure directory exists
    os.makedirs(".orchestration", exist_ok=True)
    
    # Load existing state or create new
    import json
    state = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except json.JSONDecodeError:
            state = {}
    
    # Update state with proper merging
    existing_artifacts = state.get("artifacts", {})
    if artifacts:
        existing_artifacts.update(artifacts)
    
    state.update({
        "phase": phase,
        "artifacts": existing_artifacts,
        "issues": issues or state.get("issues", []),
        "blocked_on": blocked_on or state.get("blocked_on", [])
    })
    
    # Save state
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    return state
