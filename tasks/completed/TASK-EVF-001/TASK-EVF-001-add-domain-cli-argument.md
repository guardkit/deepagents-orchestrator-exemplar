---
id: TASK-EVF-001
title: Add --domain CLI argument to agent.py
status: completed
completed: 2026-03-30T00:00:00Z
completed_location: tasks/completed/TASK-EVF-001/
priority: minor
complexity: 3
parent_review: TASK-REV-orchestrator-exemplar-validation
feature_id: FEAT-EVF
wave: 1
implementation_mode: task-work
dependencies: []
tags: [cli, entrypoint, exemplar-fix]
---

# TASK-EVF-001: Add --domain CLI argument to agent.py

## Problem

The review checklist requires `agent.py` to support a `--domain` CLI argument
(defaulting to `example-domain`). Currently `DEFAULT_DOMAIN` is hardcoded with
no argument parsing.

## Acceptance Criteria

- [x] `agent.py` uses `argparse` to accept `--domain` with default `"example-domain"`
- [x] `uv run python agent.py --help` runs without error and shows the `--domain` flag
- [x] `uv run python agent.py --domain example-domain` works (module-level `agent` still exported)
- [x] Existing `langgraph.json` import path (`./agent.py:agent`) still works
- [x] Tests updated to cover CLI argument parsing

## Implementation Notes

- Add `argparse.ArgumentParser` with `--domain` flag
- Parse args at module level (guard with `if __name__` or parse unconditionally
  with `parse_known_args` to avoid breaking langgraph.json import)
- Use `parse_known_args()` so that LangGraph server imports don't fail on
  unexpected arguments
- Update `_load_domain_prompt` call to use the parsed domain value

## Files to Modify

- `agent.py` — add argparse
- `tests/test_agent_entrypoint.py` — add CLI test cases
