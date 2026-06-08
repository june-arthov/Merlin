# Merlin-CLI Evolution Plan: Tier 3 Upgrade

Target: Transform Merlin-CLI from a simple script into a robust agentic framework similar to hermes-agent.

## Phase 1: Modularization
- [x] Move core logic to `merlin/` package.
- [x] Separate LLM logic (OpenRouter) from Execution logic.
- [x] Implement a proper Tool Registry.

## Phase 2: Tool Expansion (The Hermes Toolbelt)
Implement these core tools:
- [x] `read_file`: With line-range support.
- [x] `grep_search`: Regex search across codebase.
- [x] `list_dir`: Directory exploration.
- [x] `run_shell_command`: Command execution.
- [x] `write_file`: File creation.

## Phase 3: Skill System
- [x] Create `.merlin/skills` loader.
- [x] Support `SKILL.md` format for instruction injection.
- [x] Implementation of `activate_skill`.

## Phase 4: Memory & Context
- [x] Support `MERLIN.md` (Project Instructions).
- [x] Support `MEMORY.md` (Private Memory).
- [x] Hierarchy logic: Project > Global.

## Phase 5: Surgical Precision & Memory Persistance
- [x] `replace`: Surgical editing tool.
- [x] `glob`: Efficient file discovery.
- [x] `update_memory`: Persistent private memory management.
- [x] `update_project_instructions`: Repo-wide instruction management.

## Phase 6: Core Hardening & Self-Correction
- [x] `systematic_debugging`: 4-Phase Debugging Skill.
- [x] `plan`: Implementation planning tool.
- [x] Self-correction guidance in `MerlinEngine`.
- [x] Support for XML-like self-closing tags (`<tool />`).

## Phase 7: Security & Gray Hat Integration
- [x] `security_audit`: Skill for automated pentesting/code review.
- [x] `osint_toolkit`: Intelligence gathering skill.
- [x] `google_search` & `web_fetch`: Tools for information gathering.

## Phase 8: Deployment & CI/CD
- [x] `deploy`: Skill for automated deployment (Docker, VPS, SSH).
- [x] `docker_manager`: Tool for managing containers.
- [x] `ssh_exec`: Tool for remote VPS management.
- [x] Integration with `MERLIN_MANIFESTO.md` for ethical guardrails.

## Phase 9: Self-Evolution & Documentation
- [x] `self_evolution`: Skill for Merlin to improve its own source code.
- [x] `documentation`: Automated documentation skill.
- [x] Initial Core Test Suite in `tests/`.

## Phase 10-15: Visual & Package Hardening
- [x] Modular Package Structure (`main_entry.py`, `__init__.py`).
- [x] Global Installation Support (`setup.py` & `merlin` command).
- [x] Cyberpunk TUI Overhaul (Rich Layouts, Live Monitor).
- [x] Model Routing (`openrouter/free` failover logic).

## Phase 16: Immersive Dashboard (Singularity UI)
- [x] Full-screen interactive shell.
- [x] Real-time Execution Logs panel.
- [x] Persistent System Stats & Mandate tracking.

## Phase 17: Dynamic Tool Synthesis (Architect Mode)
- [ ] `create_tool`: Tool for Merlin to write and register new tools at runtime.
- [ ] `architect_mode`: Protocol for self-expanding capabilities.
- [ ] Tool sandbox verification before registration.
