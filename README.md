# AI-Software-Development

A modular, multi-agent system for end-to-end software development. Specialized agents collaborate across requirements, architecture, frontend, backend, testing, and DevOps using shared state and tools.

## Features
- Modular sub-agents with clear responsibilities
- LangGraph-compatible graph exposed via `langgraph dev`
- Custom tools: internet search, project validation, orchestration state
- Strong tests with coverage and realistic workflows
- Works with local or hosted models (Deep Agents ecosystem)

## Requirements
- Python 3.11+
- Dependencies: installed via `pip install -e .[dev,test]` (or `pip install -r requirements.txt` for runtime)
- Environment: copy `.env.example` to `.env` and set:
  - `TAVILY_API_KEY` (required for internet search tool)
  - `LOG_LEVEL` (e.g., INFO, DEBUG)
  - Optional model-specific variables as needed by your Deep Agents backend

## Installation
```
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,test]
# or: pip install -r requirements.txt
```

## Running
- Local CLI: `python main.py` (creates the multi-agent system and prints status)
- LangGraph server: `langgraph dev` (uses `langgraph.json` mapping `ai-software-development` → `./main.py:software_dev_agent`)
- One-command local setup: `./run-local-with-ui.sh` to start Ollama (if installed), the LangGraph server, and the Deep Agents UI. The script also ensures `.env` exists and sets safe defaults.

## Deep Agents UI (Optional)
Use the web UI to interact with the graph visually.
1) Start the local server with `langgraph dev` and note the URL.
2) Clone https://github.com/langchain-ai/deep-agents-ui and start it (`npm install && npm run dev`).
3) In the UI, add the server URL and open the `ai-software-development` graph.

## Architecture Overview
- High-level design and decisions live in `docs/architecture.md`.
- The Supervisor coordinates sub-agents in this order: Requirements → Architecture → Frontend → Backend → Testing → DevOps.
- Project sizes supported: small, medium, large (see validation below).

## Project Structure
```
.
├─ main.py                 # Creates and configures the agent
├─ langgraph.json          # Graph config for `langgraph dev`
├─ src/
│  ├─ state.py             # State schema and helpers
│  ├─ callbacks.py         # Callback utilities
│  ├─ memory.py            # Memory utilities
│  └─ tools/
│     └─ custom_tools.py   # internet_search, validate_project_structure, etc.
└─ tests/                  # Pytest suite (unit + integration)
```

## Agents & Tools
- Agents: requirements-analyst, architecture-agent, frontend-developer, backend-developer, tester-agent, devops-agent (defined in `main.py`).
- Tools (`src/tools/custom_tools.py`):
  - `internet_search(query, ...)` — Tavily-backed search (requires `TAVILY_API_KEY`).
  - `validate_project_structure(project_size)` — Checks required files exist:
    - small: `README.md`, `TODO.md`, `docs/architecture.md`, `openapi.yaml`, `Dockerfile`
    - medium: `README.md`, `TODO.md`, `design/`, `services/`, `docker-compose.yaml`, `Dockerfile`
    - large: `README.md`, `TODO.md`, `docs/features/`, `services/`, `docker-compose.yaml`, `ci/`, `k8s/`
  - `update_orchestration_state(phase, artifacts, ...)` — Writes `.orchestration/state.json`.

## Testing
```
pytest -q                      # Run all tests
pytest -m "unit"               # Only unit tests
pytest -m "integration"       # Only integration tests
pytest --cov . --cov-report=html  # Coverage; open htmlcov/index.html
```

## Linting & Formatting
```
black src tests main.py
isort src tests
flake8 src tests
mypy src
```

## Troubleshooting
- Missing API key: set `TAVILY_API_KEY` in `.env` for internet search.
- Validation fails: ensure the required files for your `project_size` exist.
- UI cannot connect: confirm `langgraph dev` is running and reachable from Deep Agents UI.

## License
MIT (see `pyproject.toml`).
