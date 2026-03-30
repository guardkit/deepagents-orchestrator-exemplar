---
complexity: 4
dependencies:
- TASK-OEX-006
feature_id: FEAT-OEX
id: TASK-OEX-007
implementation_mode: task-work
parent_review: TASK-REV-8562
priority: high
status: design_approved
tags:
- validation
- smoke-test
- quality
task_type: testing
title: Run validation checklist and smoke test
wave: 3
---

# Task: Run validation checklist and smoke test

## Description
Run the TASK-REV validation checklist and smoke test from the spec to verify the exemplar is complete and functional. Fix any failures found.

## Reference
- Spec: docs/research/project_template/FEAT-orchestrator-exemplar-build.md (Section 6 - Test Strategy)
- Validation checklist: docs/research/project_template/TASK-REV-orchestrator-exemplar-validation.md (if exists)

## Smoke Test (from spec Section 6)
```python
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
import yaml, pathlib
config = yaml.safe_load(pathlib.Path('orchestrator-config.yaml').read_text())
domain = pathlib.Path('domains/example-domain/DOMAIN.md').read_text()
assert config['orchestrator']['reasoning_model'] is not None
assert config['orchestrator']['implementation_model'] is not None
print('Full smoke test OK - ready for validation')
```

## Acceptance Criteria
- [ ] All imports in smoke test succeed without errors
- [ ] Config file loads and contains required model keys
- [ ] Domain file loads successfully
- [ ] All tools are importable and are BaseTool instances
- [ ] All prompts are importable and are non-empty strings
- [ ] `agent.py` module-level `agent` variable is a CompiledStateGraph
- [ ] Evaluator subagent has `tools: []` (empty list)
- [ ] Builder async subagent has `graph_id` field
- [ ] File tree matches spec Section 7 (all expected files exist)
- [ ] No import errors across the entire project
- [ ] `langgraph.json` is valid JSON and references `./agent.py:agent`

## Implementation Notes
- Run smoke test via: `uv run python -c "..."`
- If any import fails, trace back to the producing task and fix
- Verify file tree completeness against spec Section 7
- Check that SubAgent specs have all required fields (name, description, system_prompt, model, tools)
- Check that AsyncSubAgent spec has required fields (name, description, graph_id)