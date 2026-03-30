---
id: TASK-OEX-004
title: Create configuration files and domain structure
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
- config
- yaml
- domain
- skills
- agents-md
autobuild_state:
  current_turn: 1
  max_turns: 35
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/deepagents-orchestrator-exemplar/.guardkit/worktrees/FEAT-5009
  base_branch: main
  started_at: '2026-03-30T17:27:18.700672'
  last_updated: '2026-03-30T17:32:48.575360'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-30T17:27:18.700672'
    player_summary: 'Created four configuration and domain structure files: (1) orchestrator-config.yaml
      with orchestrator section (reasoning_model, implementation_model, checkpoint_level)
      and project section (name, description), using provider:model format compatible
      with init_chat_model(); (2) AGENTS.md defining ALWAYS/NEVER/ASK behavioral boundaries
      for Orchestrator, Implementer, and Evaluator roles; (3) domains/example-domain/DOMAIN.md
      with domain-specific guidelines and evaluation criteria; (4) skills/example-s'
    player_success: true
    coach_success: true
---

# Task: Create configuration files and domain structure

## Description
Create `orchestrator-config.yaml` for multi-model configuration, `AGENTS.md` with three-role boundaries (ALWAYS/NEVER/ASK per role), `domains/example-domain/DOMAIN.md` with example domain guidelines, and `skills/example-skill/SKILL.md` with example skill documentation.

## Reference
- Spec: docs/research/project_template/FEAT-orchestrator-exemplar-build.md (Section 3.1, Decision D2, D8)
- content-builder-agent pattern: AGENTS.md + config-driven model selection
- nvidia_deep_agent pattern: skills/ directory with SKILL.md format

## Acceptance Criteria
- [ ] `orchestrator-config.yaml` contains:
  - `orchestrator.reasoning_model`: string in `"provider:model"` format (e.g., `"anthropic:claude-sonnet-4-6"`)
  - `orchestrator.implementation_model`: string in `"provider:model"` format (e.g., `"anthropic:claude-haiku-4-5"`)
  - `orchestrator.checkpoint_level`: string (e.g., `"standard"`)
  - `project` section with name and description
- [ ] `AGENTS.md` defines ALWAYS/NEVER/ASK boundaries for: Orchestrator, Implementer, Evaluator
  - Orchestrator: ALWAYS reason before acting, NEVER implement directly, ASK when plan is ambiguous
  - Implementer: ALWAYS follow the plan, NEVER evaluate own work, ASK when instructions unclear
  - Evaluator: ALWAYS use structured verdict schema, NEVER have tools, ASK when criteria ambiguous
- [ ] `domains/example-domain/DOMAIN.md` contains example domain-specific guidelines and evaluation criteria
- [ ] `skills/example-skill/SKILL.md` contains example skill documentation with YAML frontmatter
- [ ] Model values in config use `"provider:model"` format compatible with `init_chat_model()`

## Implementation Notes
- `orchestrator-config.yaml` is read by `agent.py` at startup to configure model selection
- AGENTS.md is loaded via `memory=["./AGENTS.md"]` parameter in create_deep_agent
- DOMAIN.md content is injected into the orchestrator's system prompt at runtime
- SKILL.md follows nvidia_deep_agent pattern with YAML frontmatter metadata
