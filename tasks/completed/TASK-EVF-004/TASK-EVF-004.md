---
id: TASK-EVF-004
title: Add AsyncSubAgent instruction to orchestrator prompt
status: completed
completed: 2026-03-30T00:00:00Z
completed_location: tasks/completed/TASK-EVF-004/
priority: low
complexity: 1
parent_review: TASK-REV-orchestrator-exemplar-validation
feature_id: FEAT-EVF
wave: 1
implementation_mode: direct
dependencies: []
tags: [prompts, exemplar-fix]
---

# TASK-EVF-004: Add AsyncSubAgent instruction to orchestrator prompt

## Problem

The review checklist requires the orchestrator prompt to instruct use of
AsyncSubAgent for long-running operations. The current prompt mentions
"Delegate to Subagents" generically but doesn't distinguish sync vs async
subagents or mention the Builder subagent by name.

## Acceptance Criteria

- [x] Orchestrator prompt includes instruction to use the Builder (async)
  subagent for long-running build/deployment tasks
- [x] Instruction clarifies that async subagents run non-blocking
- [x] Prompt length still > 400 chars
- [x] No domain-specific content introduced

## Implementation

Add a bullet under the "Delegate to Subagents" section:

```
   - For long-running build or deployment operations, use the **Builder**
     (async) subagent.  Async subagents run non-blocking and return results
     when the operation completes.
```

## Files to Modify

- `prompts/orchestrator_prompts.py`
