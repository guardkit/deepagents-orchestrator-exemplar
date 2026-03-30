---
id: TASK-OEX-003
title: Create system prompts for all three roles
task_type: declarative
parent_review: TASK-REV-8562
feature_id: FEAT-OEX
wave: 1
implementation_mode: direct
complexity: 4
dependencies: []
status: in_review
priority: high
tags:
- prompts
- orchestrator
- implementer
- evaluator
autobuild_state:
  current_turn: 1
  max_turns: 35
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/deepagents-orchestrator-exemplar/.guardkit/worktrees/FEAT-5009
  base_branch: main
  started_at: '2026-03-30T17:27:18.710636'
  last_updated: '2026-03-30T17:33:44.196285'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-30T17:27:18.710636'
    player_summary: 'Created system prompts for Orchestrator, Implementer, and Evaluator
      roles. All prompts are domain-agnostic with {date} placeholder for runtime injection.
      Orchestrator also supports {domain_prompt} placeholder. Evaluator includes full
      JSON verdict schema with decision/score/issues/criteria_met/quality_assessment
      fields. The evaluator prompt uses a two-phase build approach: %s-formatting
      for schema injection, then brace-escaping to preserve {date} as a runtime placeholder.
      The __init__.py re-expor'
    player_success: true
    coach_success: true
---

# Task: Create system prompts for all three roles

## Description
Create system prompts for the Orchestrator, Implementer, and Evaluator roles. Prompts must be domain-agnostic (domain-specific criteria come from DOMAIN.md at runtime). The Evaluator prompt must include the structured JSON verdict schema.

## Reference
- Spec: docs/research/project_template/FEAT-orchestrator-exemplar-build.md (Section 3.1, 4)
- Evaluator verdict schema: Section 4 - API Contracts
- Pattern: nvidia_deep_agent ORCHESTRATOR_INSTRUCTIONS / RESEARCHER_INSTRUCTIONS

## Acceptance Criteria
- [ ] `prompts/orchestrator_prompts.py` exports `ORCHESTRATOR_SYSTEM_PROMPT` — reasoning and tool selection instructions
- [ ] `prompts/implementer_prompts.py` exports `IMPLEMENTER_SYSTEM_PROMPT` — execution instructions for the implementer subagent
- [ ] `prompts/evaluator_prompts.py` exports `EVALUATOR_SYSTEM_PROMPT` — evaluation criteria + JSON verdict schema
- [ ] Orchestrator prompt instructs: analyse context, plan pipeline, delegate to subagents, verify results
- [ ] Orchestrator prompt supports `{domain_prompt}` placeholder for runtime domain injection
- [ ] Evaluator prompt includes JSON verdict schema: `{"decision": "accept|revise|reject", "score": 1-5, "issues": [...], "criteria_met": bool, "quality_assessment": "high|adequate|needs_revision"}`
- [ ] `prompts/__init__.py` exports all three prompt constants
- [ ] No hardcoded domain references in prompts (domain-agnostic)

## Implementation Notes
- Orchestrator prompt should describe available tools and when to use each
- Implementer prompt should focus on execution quality and following plans
- Evaluator prompt should emphasize objective evaluation, no self-confirmation bias
- Use `{date}` placeholder for runtime date injection (nvidia_deep_agent pattern)
