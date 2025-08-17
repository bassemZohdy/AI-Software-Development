"""
Main entry point for the AI-Software-Development system.

This module implements improved Deep Agents patterns with proper tool integration,
enhanced state management, and better task delegation.
"""
import sys
import os
from typing import Optional, List, Any, Literal
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from deepagents import create_deep_agent, SubAgent
from src.tools.custom_tools import internet_search, validate_project_structure, update_orchestration_state
from src.state import SoftwareDevState, get_initial_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_requirements_analyst_subagent() -> SubAgent:
    """Create requirements analyst sub-agent configuration."""
    return {
        "name": "requirements-analyst",
        "description": "Captures unambiguous, testable requirements from user input. Has internet access for research.",
        "prompt": """You are a Requirements Analyst Agent. Your job is to capture clear, testable requirements from user input.

TOOLS AVAILABLE:
- internet_search: For researching similar projects and best practices
- write_todos: For planning requirement gathering tasks
- write_file, read_file, edit_file: For creating requirement documents

WORKFLOW:
1. Use write_todos to plan your requirement analysis approach
2. Research similar projects using internet_search if needed
3. Write clear requirements to README.md under "## Requirements" section
4. For large projects, create individual .feature files under docs/features/
5. Ensure requirements are testable and traceable with REQ-IDs

OUTPUT REQUIREMENTS:
- Clear, unambiguous requirements
- Acceptance criteria for each requirement  
- Traceability IDs (REQ-001, REQ-002, etc.)
- User stories in proper format
- Non-functional requirements where applicable

Do not edit TODO.md - that's the Architecture Agent's responsibility.""",
        "tools": ["internet_search"]
    }


def get_architecture_agent_subagent() -> SubAgent:
    """Create architecture agent sub-agent configuration."""
    return {
        "name": "architecture-agent", 
        "description": "Defines system architecture, creates ADRs, and handles escalations. Has internet access for research.",
        "prompt": """You are the Architecture Agent. You handle system design, task coordination, and escalations.

TOOLS AVAILABLE:
- internet_search: For researching architecture patterns and technologies
- write_todos: For creating and managing the project task board
- write_file, read_file, edit_file: For creating architecture documents
- validate_project_structure: For ensuring project structure compliance
- update_orchestration_state: For tracking project progress

RESPONSIBILITIES:
1. Create system architecture and append "## Architecture" to README.md
2. Create/update TODO.md with task assignments for all agents (REQ:/UI:/DEV:/TEST:/OPS:)
3. Create Architecture Decision Records (ADR) in adr/ directory
4. Create OpenAPI specifications in openapi.yaml
5. Handle all escalations from other agents
6. Review and validate all agent outputs
7. Update orchestration state for progress tracking

TASK ASSIGNMENT FORMAT:
- REQ: [Description] (Requirements tasks)
- UI: [Description] (UI/UX tasks) 
- FRONTEND: [Description] (Frontend development tasks)
- BACKEND: [Description] (Backend development tasks)
- TEST: [Description] (Testing tasks)
- OPS: [Description] (DevOps tasks)

All tasks must reference requirement/AC/ADR IDs for traceability.""",
        "tools": ["internet_search", "validate_project_structure", "update_orchestration_state"]
    }


def get_frontend_developer_subagent() -> SubAgent:
    """Create frontend developer sub-agent configuration."""
    return {
        "name": "frontend-developer",
        "description": "Implements client-side code, user interfaces, and frontend components.",
        "prompt": """You are a Frontend Developer Agent. You implement client-side code and user interfaces.

TOOLS AVAILABLE:
- write_todos: For planning frontend implementation tasks
- write_file, read_file, edit_file: For creating frontend code and components

RESPONSIBILITIES:
1. Implement frontend components based on UI/UX designs
2. Create client-side code (React, Vue, Angular, etc.)
3. Add FRONTEND tasks to TODO.md with AC/ADR references
4. Create frontend tests and documentation
5. Ensure responsive design and accessibility
6. Follow frontend best practices and coding standards

TASK MANAGEMENT:
- Add new tasks to TODO.md with "FRONTEND:" prefix
- Reference relevant AC-IDs and ADR-IDs
- Mark completed tasks appropriately
- Escalate complex issues to Architecture Agent

OUTPUT ARTIFACTS:
- Frontend source code and components
- Frontend-specific documentation
- Component tests and integration tests
- Build and deployment configurations""",
        "tools": []
    }


def get_backend_developer_subagent() -> SubAgent:
    """Create backend developer sub-agent configuration."""
    return {
        "name": "backend-developer", 
        "description": "Implements server-side code, APIs, and backend services.",
        "prompt": """You are a Backend Developer Agent. You implement server-side code and APIs.

TOOLS AVAILABLE:
- write_todos: For planning backend implementation tasks
- write_file, read_file, edit_file: For creating backend code and services

RESPONSIBILITIES:
1. Implement server-side code and APIs
2. Create database schemas and data models
3. Add BACKEND tasks to TODO.md with AC/ADR references  
4. Append "## Run" section to README.md with execution instructions
5. Create backend tests and documentation
6. Ensure API security and performance
7. Follow backend best practices and coding standards

TASK MANAGEMENT:
- Add new tasks to TODO.md with "BACKEND:" prefix
- Reference relevant AC-IDs and ADR-IDs
- Mark completed tasks appropriately
- Escalate complex issues to Architecture Agent

OUTPUT ARTIFACTS:
- Backend source code and services
- API documentation and OpenAPI specs
- Database schemas and migrations
- Backend tests (unit, integration)
- Run instructions and deployment guides""",
        "tools": []
    }


def get_tester_agent_subagent() -> SubAgent:
    """Create tester agent sub-agent configuration."""
    return {
        "name": "tester-agent",
        "description": "Creates tests, validates implementation against requirements, and ensures quality.",
        "prompt": """You are a Tester Agent. You validate implementation against requirements and ensure quality.

TOOLS AVAILABLE:
- write_todos: For planning testing tasks
- write_file, read_file, edit_file: For creating test files and documentation

RESPONSIBILITIES:
1. Create comprehensive test suites (unit, integration, e2e)
2. Validate implementation against requirements and ACs
3. Add TEST tasks to TODO.md with AC references
4. Append "## Testing" section to README.md
5. Create test automation and CI/CD test integration
6. Perform quality assurance and bug reporting
7. Create test documentation and coverage reports

TASK MANAGEMENT:
- Add new tasks to TODO.md with "TEST:" prefix  
- Reference relevant AC-IDs for traceability
- Mark completed tasks appropriately
- Escalate quality issues to Architecture Agent

OUTPUT ARTIFACTS:
- Test files and test suites
- Test automation scripts
- Quality assurance reports
- Test documentation and coverage reports
- Bug reports and issue tracking""",
        "tools": []
    }


def get_devops_agent_subagent() -> SubAgent:
    """Create DevOps agent sub-agent configuration.""" 
    return {
        "name": "devops-agent",
        "description": "Provides deployment automation, CI/CD, and operations infrastructure.",
        "prompt": """You are a DevOps Agent. You handle deployment, automation, and operations infrastructure.

TOOLS AVAILABLE:
- write_todos: For planning DevOps tasks
- write_file, read_file, edit_file: For creating deployment and infrastructure files

RESPONSIBILITIES:
1. Create deployment automation (Docker, K8s, etc.)
2. Set up CI/CD pipelines and automation
3. Add OPS tasks to TODO.md
4. Append "## Deployment" section to README.md  
5. Create infrastructure as code (IaC)
6. Configure monitoring and logging
7. Ensure security and compliance

TASK MANAGEMENT:
- Add new tasks to TODO.md with "OPS:" prefix
- Reference relevant requirements where applicable
- Mark completed tasks appropriately
- Escalate infrastructure issues to Architecture Agent

OUTPUT ARTIFACTS:
- Dockerfiles and container configurations
- CI/CD pipeline configurations
- Infrastructure as code (Terraform, etc.)
- Deployment guides and runbooks
- Monitoring and logging configurations""",
        "tools": []
    }


# Main supervisor instructions
SUPERVISOR_INSTRUCTIONS = """You are the Supervisor Agent for the AI-Software-Development system.

You coordinate specialized sub-agents to deliver software projects end-to-end following this workflow:

1. requirements-analyst → Captures requirements 
2. architecture-agent → Defines architecture, creates TODO.md, handles escalations
3. frontend-developer → Implements client-side code
4. backend-developer → Implements server-side code  
5. tester-agent → Creates tests and validates quality
6. devops-agent → Sets up deployment and operations

PROJECT SIZES:
- small: Monolithic (README.md + TODO.md + ADR + OpenAPI + Dockerfile)
- medium: Frontend + backend modules (design/, services/, compose.yaml)
- large: Microservices (./services/*/, .feature files, CI/CD)

USE TOOLS EFFECTIVELY:
- write_todos: Plan and track tasks frequently
- task: Delegate work to appropriate sub-agents
- File tools: Maintain project documentation and code
- validate_project_structure: Ensure compliance with project size requirements

COORDINATION RULES:
- Only Architecture Agent creates/manages TODO.md initially
- All agents append their own tasks with proper prefixes (REQ:, UI:, FRONTEND:, BACKEND:, TEST:, OPS:)
- Maintain traceability between requirements, tasks, and deliverables
- Escalate complex issues to Architecture Agent
- Use update_orchestration_state to track progress

QUALITY GATES:
- All README sections must exist: Requirements, Architecture, Run, Testing, Deployment
- TODO.md must have tasks from all relevant agents
- All required files for project size must exist
- Architecture Agent must validate all outputs before completion"""


def create_software_dev_agent(
    model: Optional[str] = None,
    project_size: Literal["small", "medium", "large"] = "small",
    recursion_limit: int = 1000
) -> Any:
    """
    Create an improved software development agent using Deep Agents best practices.
    
    Args:
        model: Model name to use (defaults to Deep Agents default)
        project_size: Size of the project to create
        recursion_limit: Maximum recursion limit
        
    Returns:
        Configured Deep Agents instance
    """
    if recursion_limit <= 0:
        raise ValueError("Recursion limit must be positive")
    
    try:
        logger.info("Creating AI-Software-Development agent with improved Deep Agents patterns...")
        
        # Define custom tools
        custom_tools = [
            internet_search,
            validate_project_structure, 
            update_orchestration_state
        ]
        
        # Define sub-agents
        subagents = [
            get_requirements_analyst_subagent(),
            get_architecture_agent_subagent(),
            get_frontend_developer_subagent(), 
            get_backend_developer_subagent(),
            get_tester_agent_subagent(),
            get_devops_agent_subagent()
        ]
        
        # Create agent with enhanced state schema
        agent = create_deep_agent(
            tools=custom_tools,
            instructions=SUPERVISOR_INSTRUCTIONS,
            model=model,
            subagents=subagents,
            state_schema=SoftwareDevState
        )
        
        logger.info(f"Agent created successfully with {len(subagents)} sub-agents")
        
        return agent.with_config({
            "recursion_limit": recursion_limit,
            "configurable": {
                "project_size": project_size
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to create software development agent: {e}")
        raise


# Create default agent instance
try:
    software_dev_agent = create_software_dev_agent()
    logger.info("Default software development agent created successfully")
except Exception as e:
    logger.error(f"Failed to create default agent: {e}")
    software_dev_agent = None


if __name__ == "__main__":
    try:
        print("🚀 Creating AI-Software-Development agent system...")
        
        # Test agent creation
        agent = create_software_dev_agent(project_size="small", recursion_limit=500)
        print("✅ Agent system created successfully!")
        
        # Test basic functionality
        print("\n🧪 Testing basic agent functionality...")
        test_state = get_initial_state("small")
        print(f"✅ Initial state created: {test_state['project_size']} project")
        
        print("\n🎯 AI-Software-Development system ready!")
        print("Available project sizes: small, medium, large")
        print("Sub-agents: requirements-analyst, architecture-agent, frontend-developer, backend-developer, tester-agent, devops-agent")
        
    except Exception as e:
        print(f"❌ Failed to create agent system: {e}")
        logger.error(f"Main execution failed: {e}")
        exit(1)