---
id: TASK-OEX-003
title: "Create system prompts for all three roles"
task_type: declarative
parent_review: TASK-REV-8562
feature_id: FEAT-OEX
wave: 1
implementation_mode: direct
complexity: 4
dependencies: []
status: pending
priority: high
tags: [prompts, orchestrator, implementer, evaluator]
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
