"""
Test configuration and fixtures for AI-Software-Development tests.
"""
import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_tavily_client():
    """Mock Tavily client for testing internet search."""
    with patch('src.tools.custom_tools.get_tavily_client') as mock_get_client:
        mock_client = Mock()
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Test Result",
                    "url": "https://example.com",
                    "content": "Test content"
                }
            ]
        }
        mock_get_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    with patch.dict(os.environ, {
        'TAVILY_API_KEY': 'test-api-key',
        'LOG_LEVEL': 'INFO'
    }):
        yield


@pytest.fixture
def sample_state_data():
    """Sample state data for testing."""
    return {
        "project_size": "small",
        "current_phase": "REQ",
        "artifacts": {
            "requirements": False,
            "architecture": False,
            "adr": False,
            "openapi": False,
            "ux": False,
            "run_instructions": False,
            "testing": False,
            "deployment": False
        },
        "issues": [],
        "blocked_on": [],
        "agent_assignments": {},
        "validation_passed": False,
        "ready_for_delivery": False
    }


@pytest.fixture
def sample_project_files(temp_dir):
    """Create sample project files for testing."""
    files = {
        "README.md": """# Test Project
## Requirements
REQ-001: User authentication
## Architecture  
Microservices architecture
""",
        "TODO.md": """# Project Tasks
REQ: Analyze user authentication requirements - REQ-001
ARCH: Design authentication service - ADR-001
""",
        "requirements.txt": "fastapi>=0.68.0\npytest>=6.0.0",
        "Dockerfile": "FROM python:3.9\nCOPY . /app"
    }
    
    for filename, content in files.items():
        with open(filename, 'w') as f:
            f.write(content)
    
    # Create directories
    os.makedirs("adr", exist_ok=True)
    with open("adr/0001-architecture.md", 'w') as f:
        f.write("# ADR-001: Authentication Architecture\n\nDecision to use OAuth2")
    
    return files