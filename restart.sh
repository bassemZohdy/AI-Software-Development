#!/usr/bin/env bash
set -euo pipefail

# Restart a specific local service: langgraph | ui

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
RUN_DIR="$PROJECT_DIR/.run"
LANGGRAPH_PORT="8123"
UI_PORT="5173"
UI_DIR="$PROJECT_DIR/deep-agents-ui"

usage() {
  echo "Usage: $0 {langgraph|ui}" >&2
  exit 1
}

ensure_dirs() { mkdir -p "$LOG_DIR" "$RUN_DIR"; }

stop_langgraph() {
  local pid_file="$RUN_DIR/langgraph.pid"
  if [[ -f "$pid_file" ]]; then
    local pid; pid="$(cat "$pid_file" 2>/dev/null || echo "")"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      echo "[restart] Stopping LangGraph (pid=$pid)"
      kill "$pid" 2>/dev/null || true; sleep 1
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
  fi
  # Free the port if still in use
  local pids; pids=$(lsof -ti tcp:"$LANGGRAPH_PORT" -sTCP:LISTEN 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    echo "[restart] Killing listeners on :$LANGGRAPH_PORT ($pids)"
    kill $pids 2>/dev/null || true; sleep 1
    local p2; p2=$(lsof -ti tcp:"$LANGGRAPH_PORT" -sTCP:LISTEN 2>/dev/null || true)
    [[ -n "$p2" ]] && kill -9 $p2 2>/dev/null || true
  fi
}

start_langgraph() {
  if ! command -v langgraph >/dev/null 2>&1; then
    echo "langgraph CLI not found. Install with: pip install langgraph-cli[inmem]" >&2
    exit 1
  fi
  echo "[restart] Starting LangGraph on :$LANGGRAPH_PORT (logs: $LOG_DIR/langgraph.log)"
  (cd "$PROJECT_DIR" && nohup langgraph dev --port "$LANGGRAPH_PORT" > "$LOG_DIR/langgraph.log" 2>&1 & echo $! > "$RUN_DIR/langgraph.pid")
}

stop_ui() {
  local pid_file="$RUN_DIR/ui.pid"
  if [[ -f "$pid_file" ]]; then
    local pid; pid="$(cat "$pid_file" 2>/dev/null || echo "")"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      echo "[restart] Stopping UI (pid=$pid)"
      kill "$pid" 2>/dev/null || true; sleep 1
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
  fi
  local pids; pids=$(lsof -ti tcp:"$UI_PORT" -sTCP:LISTEN 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    echo "[restart] Killing listeners on :$UI_PORT ($pids)"
    kill $pids 2>/dev/null || true; sleep 1
    local p2; p2=$(lsof -ti tcp:"$UI_PORT" -sTCP:LISTEN 2>/dev/null || true)
    [[ -n "$p2" ]] && kill -9 $p2 2>/dev/null || true
  fi
}

start_ui() {
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm not found. Install Node.js/npm to run the UI." >&2
    exit 1
  fi
  mkdir -p "$UI_DIR"
  # Ensure env for UI is set
  (
    cd "$UI_DIR"
    touch .env.local
    # Next.js public env
    if ! grep -q '^NEXT_PUBLIC_DEPLOYMENT_URL=' .env.local; then
      echo "NEXT_PUBLIC_DEPLOYMENT_URL=http://127.0.0.1:${LANGGRAPH_PORT}" >> .env.local
    fi
    if ! grep -q '^NEXT_PUBLIC_AGENT_ID=' .env.local; then
      echo "NEXT_PUBLIC_AGENT_ID=ai-software-development" >> .env.local
    fi
  )
  echo "[restart] Starting UI on :$UI_PORT (logs: $LOG_DIR/ui.log)"
  (
    cd "$UI_DIR"
    nohup bash -lc "npm install && npm run dev -- --port '${UI_PORT}'" > "$LOG_DIR/ui.log" 2>&1 & echo $! > "$RUN_DIR/ui.pid"
  )
}

main() {
  ensure_dirs
  local target="${1:-}"
  [[ -z "$target" ]] && usage

  case "$target" in
    langgraph)
      stop_langgraph
      start_langgraph
      ;;
    ui)
      stop_ui
      start_ui
      ;;
    *)
      usage
      ;;
  esac

  echo "[restart] Done. Check logs in $LOG_DIR for details."
}

main "$@"

