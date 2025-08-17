#!/usr/bin/env bash
set -euo pipefail

# A convenience script to run everything locally:
# 1) Ensure .env exists and has sensible defaults
# 2) Start Ollama (for local LLMs)
# 3) Start the LangGraph server for this project
# 4) Launch the Deep Agents UI and connect to the server

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
RUN_DIR="$PROJECT_DIR/.run"
LANGGRAPH_PORT="8123"
UI_DIR="$PROJECT_DIR/deep-agents-ui"
UI_PORT="5173"

mkdir -p "$LOG_DIR" "$RUN_DIR"

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

  # Start Ollama in background without waiting for readiness
  echo "Starting Ollama in background... (logs: $LOG_DIR/ollama.log)"
  nohup ollama serve > "$LOG_DIR/ollama.log" 2>&1 &
  echo $! > "$RUN_DIR/ollama.pid"

  # Optional background model pull if explicitly enabled
  if [[ "${OLLAMA_PULL:-}" == "1" ]]; then
    local model="${OLLAMA_MODEL:-llama3.1}"
    if [[ -n "${model}" ]]; then
      echo "Background pulling Ollama model '${model}'... (logs: $LOG_DIR/ollama-pull.log)"
      nohup ollama pull "${model}" > "$LOG_DIR/ollama-pull.log" 2>&1 &
      echo $! > "$RUN_DIR/ollama-pull.pid"
    fi
  else
    echo "Skipping model pull. Set OLLAMA_PULL=1 (and optional OLLAMA_MODEL) to pull in background."
  fi
}

start_langgraph() {
  if ! command -v langgraph >/dev/null 2>&1; then
    echo "langgraph CLI not found. Install with: pip install langgraph-cli[inmem]"
    exit 1
  fi
  echo "Starting LangGraph dev server in background on port ${LANGGRAPH_PORT}... (logs: $LOG_DIR/langgraph.log)"
  cd "$PROJECT_DIR"
  nohup langgraph dev --port "${LANGGRAPH_PORT}" > "$LOG_DIR/langgraph.log" 2>&1 &
  echo $! > "$RUN_DIR/langgraph.pid"
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

  # Ensure UI env matches API config (graph name and server URL)
  echo "Configuring UI environment (.env.local) ..."
  (
    cd "$UI_DIR"
    touch .env.local
    set_kv() {
      local key="$1"; shift
      local val="$1"; shift
      if grep -q "^${key}=" .env.local; then
        # Replace existing line
        sed -i.bak "s#^${key}=.*#${key}=${val}#" .env.local && rm -f .env.local.bak
      else
        echo "${key}=${val}" >> .env.local
      fi
    }
    set_kv VITE_SERVER_URL "http://localhost:${LANGGRAPH_PORT}"
    set_kv VITE_GRAPH_NAME "ai-software-development"
  )

  echo "Starting Deep Agents UI in background on port ${UI_PORT}... (logs: $LOG_DIR/ui.log)"
  (
    cd "$UI_DIR"
    nohup bash -lc "npm install && npm run dev -- --port '${UI_PORT}'" > "$LOG_DIR/ui.log" 2>&1 & echo $! > "$RUN_DIR/ui.pid"
  )

  echo "UI should be available at http://localhost:${UI_PORT}"
  echo "In the UI, the default server and graph are set via .env.local (VITE_SERVER_URL, VITE_GRAPH_NAME=ai-software-development)."
}

main() {
  ensure_env
  start_ollama
  start_langgraph
  start_ui

  echo "\nAll services started in background."
  echo "- LangGraph server: http://localhost:${LANGGRAPH_PORT} (logs: $LOG_DIR/langgraph.log)"
  echo "- Deep Agents UI:  http://localhost:${UI_PORT} (logs: $LOG_DIR/ui.log)"
  echo "- Ollama logs:     $LOG_DIR/ollama.log (and $LOG_DIR/ollama-pull.log if OLLAMA_PULL=1)"
  echo "Check logs to validate readiness."
}

main "$@"
