---
id: TASK-OEX-002
title: Implement orchestrator tools
task_type: feature
parent_review: TASK-REV-8562
feature_id: FEAT-OEX
wave: 1
implementation_mode: task-work
complexity: 5
dependencies: []
status: in_review
priority: high
tags:
- tools
- langchain
- orchestrator
autobuild_state:
  current_turn: 1
  max_turns: 35
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/deepagents-orchestrator-exemplar/.guardkit/worktrees/FEAT-5009
  base_branch: main
  started_at: '2026-03-30T17:27:18.697875'
  last_updated: '2026-03-30T17:41:47.713169'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-30T17:27:18.697875'
    player_summary: Implementation via task-work delegation
    player_success: true
    coach_success: true
---

# Task: Implement orchestrator tools

## Description
Create four tools using the `@tool` decorator from `langchain_core.tools`: `analyse_context`, `plan_pipeline`, `execute_command`, and `verify_output`. All tools return strings and never raise exceptions (proven pattern from Player-Coach exemplar). These are simplified stubs for the exemplar — in production they would wrap GuardKit slash commands.

## Reference
- Spec: docs/research/project_template/FEAT-orchestrator-exemplar-build.md (Section 4 - Tool Contracts)
- SDK pattern: nvidia_deep_agent/src/tools.py (@tool with parse_docstring=True)
- Import: `from langchain_core.tools import tool`

## Acceptance Criteria
- [ ] `tools/analyse_context.py` — `analyse_context(query: str, domain: str) -> str` — reads and summarises project context
- [ ] `tools/plan_pipeline.py` — `plan_pipeline(task: str, context: str) -> str` — returns JSON pipeline plan string
- [ ] `tools/execute_command.py` — `execute_command(command: str, args: str) -> str` — returns execution result string
- [ ] `tools/verify_output.py` — `verify_output(output_path: str, criteria: str) -> str` — returns verification result string
- [ ] All tools use `@tool(parse_docstring=True)` decorator
- [ ] All tools return strings, never raise exceptions (wrap in try/except returning error strings)
- [ ] All tools have proper docstrings with Args section (required for parse_docstring)
- [ ] `tools/__init__.py` exports all four tools
- [ ] All modified files pass project-configured lint/format checks with zero errors

## Implementation Notes
- These are simplified stubs. `analyse_context` can read a file and return its content. `plan_pipeline` can return a JSON string with steps. `execute_command` can simulate command execution. `verify_output` can check if a path exists.
- Do NOT use `InjectedToolArg` for these tools — all parameters are user-facing
- Follow the nvidia_deep_agent pattern: simple functions, clear docstrings, string returns
