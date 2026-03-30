---
id: TASK-OEX-001
title: Scaffold project structure and dependencies
task_type: scaffolding
parent_review: TASK-REV-8562
feature_id: FEAT-OEX
wave: 1
implementation_mode: direct
complexity: 3
dependencies: []
status: in_review
priority: high
tags:
- scaffold
- dependencies
- config
autobuild_state:
  current_turn: 1
  max_turns: 35
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/deepagents-orchestrator-exemplar/.guardkit/worktrees/FEAT-5009
  base_branch: main
  started_at: '2026-03-30T17:27:18.699633'
  last_updated: '2026-03-30T17:32:00.184139'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-30T17:27:18.699633'
    player_summary: 'Created all scaffold files for the project. pyproject.toml includes
      all 7 required dependencies with correct version specifiers and Python >=3.11,<4.0
      constraint. .env.example documents all required and optional env vars with clear
      comments. The existing .gitignore (from repo init) already covered all required
      patterns (__pycache__, .env, *.pyc via *.py[codz], .venv, dist/, *.egg-info/).
      langgraph.json references ./agent.py:agent as the graph entry point. Empty __init__.py
      files were created in '
    player_success: true
    coach_success: true
---

# Task: Scaffold project structure and dependencies

## Description
Create the foundational project files: `pyproject.toml` with `deepagents>=0.5.0a2` and all required dependencies, `.env.example` with documented environment variables, `.gitignore` for Python projects, and `langgraph.json` deployment configuration.

## Reference
- Spec: docs/research/project_template/FEAT-orchestrator-exemplar-build.md (Section 7, 8)
- SDK: ~/Projects/appmilla_github/deepagents (pyproject.toml for dependency versions)
- Pattern: nvidia_deep_agent langgraph.json format

## Acceptance Criteria
- [ ] `pyproject.toml` exists with: deepagents>=0.5.0a2, langchain>=1.2.11, langchain-core>=1.2.21, langgraph>=0.2, langsmith>=0.3, python-dotenv>=1.0, pyyaml>=6.0
- [ ] Python version requirement >=3.11,<4.0 (matches SDK requirement)
- [ ] `.env.example` documents: LANGSMITH_API_KEY, LANGSMITH_TRACING, LANGSMITH_PROJECT, ANTHROPIC_API_KEY, GOOGLE_API_KEY (optional), LOCAL_MODEL_ENDPOINT (optional)
- [ ] `.gitignore` covers: __pycache__, .env, *.pyc, .venv/, dist/, *.egg-info/
- [ ] `langgraph.json` references `"./agent.py:agent"` as graph entry point
- [ ] Empty `__init__.py` files created in: agents/, tools/, prompts/
- [ ] All modified files pass project-configured lint/format checks with zero errors

## Implementation Notes
- Use `uv` as package manager (consistent with existing exemplar)
- `langgraph.json` format: `{"dependencies": ["."], "graphs": {"orchestrator": "./agent.py:agent"}, "env": ".env"}`
- The `agent.py` file itself is created in TASK-OEX-006, but langgraph.json must reference it correctly now
