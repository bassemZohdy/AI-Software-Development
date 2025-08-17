# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2025-08-17
- docs: Comprehensive README with installation, running (CLI + LangGraph), Deep Agents UI, testing, linting, troubleshooting, and project structure.
- feat(tools): Enforce `docs/architecture.md` for small project validation (removed ADR fallback).
- refactor(tests): Update fixtures and integration tests to use `docs/architecture.md`.
- feat(main): Update Architecture Agent prompt and supervisor guidance to reference `docs/architecture.md`.
- chore(gitignore): Ignore `AGENTS.md` and `CLAUDE.md` (AI-agent-only docs).
- chore: Add previously untracked helper modules `src/callbacks.py` and `src/memory.py` to VCS.

## [0.1.0] - 2025-08-16
- Initial project setup with multi-agent architecture, tools, tests, and LangGraph integration.
