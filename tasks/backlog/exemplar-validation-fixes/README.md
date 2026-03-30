# Exemplar Validation Fixes (FEAT-EVF)

## Problem Statement

The TASK-REV orchestrator exemplar validation review identified 5 findings
(4 actionable). While no blockers were found (the exemplar passes all FAIL
criteria), these deviations from the spec should be fixed before using the
exemplar as a template for `guardkit/guardkitfactory`.

## Solution Approach

Four targeted fixes, each isolated to 1-2 files:

| Task | Finding | Severity | Files |
|------|---------|----------|-------|
| EVF-001 | Add `--domain` CLI argument | Minor | `agent.py`, tests |
| EVF-002 | Add `local` config section | Minor | `orchestrator-config.yaml` |
| EVF-003 | Load AGENTS.md into memory | Medium | `agents/agents.py`, tests |
| EVF-004 | AsyncSubAgent in prompt | Low | `prompts/orchestrator_prompts.py` |

## Subtask Summary

- **4 tasks**, all in **Wave 1** (no dependencies between them)
- **1 task-work** (EVF-001 — needs CLI + test changes)
- **3 direct** (EVF-002, EVF-003, EVF-004 — single-file edits)
- Parent review: `TASK-REV-orchestrator-exemplar-validation`
