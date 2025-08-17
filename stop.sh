#!/usr/bin/env bash
set -euo pipefail

# Gracefully stop local services started by run-local-with-ui.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
RUN_DIR="$PROJECT_DIR/.run"

LG_PORT=8123
UI_PORT=5173

log() { echo "[stop] $*"; }

kill_pid() {
  local pid_file="${1:-}"; shift || true
  local name="${2:-unknown}"; shift || true
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file" 2>/dev/null || echo "")"
    if [[ -n "${pid}" ]] && kill -0 "$pid" 2>/dev/null; then
      log "Stopping $name (pid=$pid) ..."
      kill "$pid" 2>/dev/null || true
      # wait up to 5s
      for _ in {1..5}; do
        if kill -0 "$pid" 2>/dev/null; then sleep 1; else break; fi
      done
      if kill -0 "$pid" 2>/dev/null; then
        log "$name did not exit, force killing..."
        kill -9 "$pid" 2>/dev/null || true
      fi
    else
      log "$name: no running process for pid file (stale?)"
    fi
    rm -f "$pid_file"
  else
    log "$name: pid file not found ($pid_file)"
  fi
}

kill_port() {
  local port="${1:-}"; shift || true
  local label="${2:-unknown}"; shift || true
  local pids
  pids=$(lsof -ti tcp:"$port" -sTCP:LISTEN 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    log "Killing $label listeners on port $port: $pids"
    kill $pids 2>/dev/null || true
    sleep 1
    local pids2
    pids2=$(lsof -ti tcp:"$port" -sTCP:LISTEN 2>/dev/null || true)
    if [[ -n "$pids2" ]]; then
      log "Force killing remaining $label pids: $pids2"
      kill -9 $pids2 2>/dev/null || true
    fi
  else
    log "$label: no listeners on port $port"
  fi
}

fallback_pkill() {
  pkill -f "$1" 2>/dev/null || true
}

main() {
  mkdir -p "$RUN_DIR" "$LOG_DIR"

  # 1) Try PID files first (graceful)
  kill_pid "$RUN_DIR/langgraph.pid" "LangGraph"
  kill_pid "$RUN_DIR/ui.pid" "Deep Agents UI"
  # Note: We do not stop Ollama here on purpose

  # 2) Ensure ports are freed
  kill_port "$LG_PORT" "LangGraph"
  kill_port "$UI_PORT" "UI"
  # Do not stop Ollama port

  # 3) Fallback by process names (best-effort)
  fallback_pkill "langgraph dev"
  fallback_pkill "next dev"
  # Do not kill Ollama here

  # 4) Verify
  status=0
  for port in "$LG_PORT" "$UI_PORT"; do
    if lsof -i tcp:"$port" -sTCP:LISTEN 2>/dev/null | grep -q LISTEN; then
      log "Port $port still in use"; status=1
    else
      log "Port $port free"
    fi
  done
  exit $status
}

main "$@"
