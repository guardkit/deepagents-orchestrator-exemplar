---
id: TASK-EVF-003
title: Load AGENTS.md into agent memory
status: completed
completed: 2026-03-30
completed_location: tasks/completed/TASK-EVF-003/
priority: medium
complexity: 2
parent_review: TASK-REV-orchestrator-exemplar-validation
feature_id: FEAT-EVF
wave: 1
implementation_mode: direct
dependencies: []
tags: [agents, memory, exemplar-fix]
---

# TASK-EVF-003: Load AGENTS.md into agent memory

## Problem

AGENTS.md states it is "loaded into agent memory via the `memory=["./AGENTS.md"]`
parameter", but `create_orchestrator()` passes `memory=None`. The agent
behavioral boundaries defined in AGENTS.md are therefore not enforced at runtime.

## Acceptance Criteria

- [x] `create_deep_agent()` call in `agents/agents.py` uses `memory=["./AGENTS.md"]`
  instead of `memory=None`
- [x] Existing tests still pass (373/373)
- [x] No tests mock `create_deep_agent` with memory assertions — no changes needed

## Files to Modify

- `agents/agents.py` — change `memory=None` to `memory=["./AGENTS.md"]`
- Tests that assert on `create_deep_agent` kwargs (if any)
