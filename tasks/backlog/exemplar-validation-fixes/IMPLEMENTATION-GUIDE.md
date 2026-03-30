# Implementation Guide: Exemplar Validation Fixes (FEAT-EVF)

## Overview

4 tasks fixing deviations found during TASK-REV orchestrator exemplar validation.
All tasks are independent and can execute in parallel.

## Wave 1 (all tasks — no dependencies)

### Parallel Execution Group

All 4 tasks touch different files and can run simultaneously.

| Task | Method | Files | Est. Complexity |
|------|--------|-------|-----------------|
| TASK-EVF-001 | `/task-work` | `agent.py`, `tests/test_agent_entrypoint.py` | 3/10 |
| TASK-EVF-002 | Direct edit | `orchestrator-config.yaml` | 1/10 |
| TASK-EVF-003 | Direct edit | `agents/agents.py`, tests | 2/10 |
| TASK-EVF-004 | Direct edit | `prompts/orchestrator_prompts.py` | 1/10 |

### Execution Order

No ordering constraints. All can start immediately.

## Verification

After all tasks complete, re-run the full validation:

```bash
# Full test suite
uv run pytest tests/ -v

# Smoke test from review checklist
uv run python -c "
from agents.orchestrator import create_orchestrator
from agents.implementer import implementer_subagent
from agents.evaluator import evaluator_subagent
from agents.builder import builder_async_subagent
from tools.analyse_context import analyse_context
from tools.plan_pipeline import plan_pipeline
from tools.execute_command import execute_command
from tools.verify_output import verify_output
from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT
from prompts.evaluator_prompts import EVALUATOR_SYSTEM_PROMPT
print('All imports OK')
"

# CLI help test (new)
uv run python agent.py --help
```

## Acceptance

All 5 non-blocking findings from the review are resolved. Re-run
`/task-review TASK-REV-orchestrator-exemplar-validation` to confirm
all checklist items pass.
