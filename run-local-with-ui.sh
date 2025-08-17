#!/usr/bin/env bash
set -euo pipefail

# A convenience script to run everything locally:
# 1) Ensure .env exists and has sensible defaults
# 2) Start Ollama (for local LLMs)
# 3) Start the LangGraph server for this project
# 4) Launch the Deep Agents UI and connect to the server

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
LANGGRAPH_PORT="8123"
UI_DIR="$PROJECT_DIR/deep-agents-ui"
UI_PORT="5173"

mkdir -p "$LOG_DIR"

ensure_env() {
  cd "$PROJECT_DIR"
  if [[ ! -f .env ]]; then
    if [[ -f .env.example ]]; then
      cp .env.example .env
      echo "Created .env from .env.example. Review and set your secrets (e.g., TAVILY_API_KEY)."
    else
      touch .env
      echo "Created empty .env. Add required variables (e.g., TAVILY_API_KEY)."
    fi
  fi

  # Ensure defaults exist without overwriting user values
  ensure_line() {
    local key="$1"; shift
    local value="$1"; shift
    if ! grep -q "^${key}=" .env; then
      echo "${key}=${value}" >> .env
    fi
  }

  ensure_line LOG_LEVEL "INFO"
  ensure_line OLLAMA_BASE_URL "http://localhost:11434"
  ensure_line OLLAMA_TIMEOUT "60"

  if ! grep -q '^TAVILY_API_KEY=' .env; then
    echo "NOTE: TAVILY_API_KEY is not set in .env. Internet search tool will be disabled until you add it."
  fi
}

start_ollama() {
  if ! command -v ollama >/dev/null 2>&1; then
    echo "Ollama not found. Install from https://ollama.com/download before continuing."
    return 0
  fi

  # Try to detect running server
  local base_url="$(grep '^OLLAMA_BASE_URL=' .env | cut -d'=' -f2 || echo 'http://localhost:11434')"
  if curl -sS "${base_url}/api/tags" >/dev/null 2>&1; then
    echo "Ollama appears to be running at ${base_url}."
  else
    echo "Starting Ollama..."
    nohup ollama serve > "$LOG_DIR/ollama.log" 2>&1 &
    # Wait briefly for server to start
    for i in {1..20}; do
      if curl -sS "${base_url}/api/tags" >/dev/null 2>&1; then
        echo "Ollama is up at ${base_url}."
        break
      fi
      sleep 1
    done
  fi

  # Optionally pull a model (can be time-consuming). Set OLLAMA_MODEL to skip/change.
  local model="${OLLAMA_MODEL:-llama3.1}"
  if [[ -n "${model}" ]]; then
    echo "Ensuring Ollama model '${model}' is available (this may take a while on first run)..."
    ollama pull "${model}" || true
  fi
}

start_langgraph() {
  if ! command -v langgraph >/dev/null 2>&1; then
    echo "langgraph CLI not found. Install with: pip install langgraph-cli[inmem]"
    exit 1
  fi
  echo "Starting LangGraph dev server on port ${LANGGRAPH_PORT}..."
  cd "$PROJECT_DIR"
  nohup langgraph dev --port "${LANGGRAPH_PORT}" > "$LOG_DIR/langgraph.log" 2>&1 &
  # Wait briefly for server to start
  for i in {1..20}; do
    if curl -sS "http://localhost:${LANGGRAPH_PORT}/" >/dev/null 2>&1; then
      echo "LangGraph server is up at http://localhost:${LANGGRAPH_PORT}"
      break
    fi
    sleep 1
  done
}

start_ui() {
  if ! command -v git >/dev/null 2>&1; then
    echo "git is required to clone the UI repo. Install git and re-run."
    exit 1
  fi
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm is required to run the UI. Install Node.js/npm and re-run."
    exit 1
  fi

  if [[ ! -d "$UI_DIR" ]]; then
    echo "Cloning Deep Agents UI into $UI_DIR ..."
    git clone https://github.com/langchain-ai/deep-agents-ui "$UI_DIR"
  else
    echo "Updating Deep Agents UI..."
    (cd "$UI_DIR" && git pull --ff-only || true)
  fi

  echo "Installing UI dependencies..."
  (cd "$UI_DIR" && npm install)

  echo "Starting Deep Agents UI on port ${UI_PORT}..."
  (cd "$UI_DIR" && nohup npm run dev -- --port "${UI_PORT}" > "$LOG_DIR/ui.log" 2>&1 &)

  echo "UI should be available at http://localhost:${UI_PORT}"
  echo "In the UI, add a server: http://localhost:${LANGGRAPH_PORT} and open graph 'ai-software-development' (alias: 'software-development')."
}

main() {
  ensure_env
  start_ollama
  start_langgraph
  start_ui

  echo "\nAll set!"
  echo "- LangGraph server: http://localhost:${LANGGRAPH_PORT}"
  echo "- Deep Agents UI:  http://localhost:${UI_PORT}"
}

main "$@"
