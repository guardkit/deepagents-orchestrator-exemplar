# Feature: DeepAgents Orchestrator Exemplar

## Problem
GuardKit's template philosophy requires templates created FROM proven working code. Before building the Factory Pipeline Orchestrator, a working exemplar must exist demonstrating the Orchestrator + Implementer + Evaluator pattern with multi-model architecture and non-blocking subagent execution.

## Solution
Build a three-role agent exemplar using the DeepAgents SDK 0.5.0a2:
- **Orchestrator**: Reasoning model with tools + subagents — decides what to do
- **Implementer**: SubAgent (sync) — executes plans
- **Evaluator**: SubAgent (sync, no tools) — reviews output with structured JSON verdict
- **Builder**: AsyncSubAgent — non-blocking long-running operations

## Tasks (7 across 3 waves)

### Wave 1: Foundation (parallel)
| Task | Title | Complexity | Mode |
|------|-------|-----------|------|
| TASK-OEX-001 | Scaffold project structure | 3 | direct |
| TASK-OEX-002 | Implement 4 orchestrator tools | 5 | task-work |
| TASK-OEX-003 | Create system prompts (3 roles) | 4 | direct |
| TASK-OEX-004 | Config files + domain structure | 3 | direct |

### Wave 2: Agents (sequential)
| Task | Title | Complexity | Mode |
|------|-------|-----------|------|
| TASK-OEX-005 | Agent definitions (4 roles) | 7 | task-work |
| TASK-OEX-006 | Entrypoint wiring (agent.py) | 5 | task-work |

### Wave 3: Validation
| Task | Title | Complexity | Mode |
|------|-------|-----------|------|
| TASK-OEX-007 | Validation + smoke test | 4 | task-work |

## Quick Start
```bash
/task-work TASK-OEX-001   # Start with scaffold (or run Wave 1 in parallel)
```

## References
- [Feature spec](../../../docs/research/project_template/FEAT-orchestrator-exemplar-build.md)
- [Implementation guide](./IMPLEMENTATION-GUIDE.md)
- Review: TASK-REV-8562
