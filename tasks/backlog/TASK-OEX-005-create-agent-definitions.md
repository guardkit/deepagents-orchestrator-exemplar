---
id: TASK-OEX-005
title: "Create agent definitions for all four roles"
task_type: feature
parent_review: TASK-REV-8562
feature_id: FEAT-OEX
wave: 2
implementation_mode: task-work
complexity: 7
dependencies:
  - TASK-OEX-001
  - TASK-OEX-002
  - TASK-OEX-003
  - TASK-OEX-004
status: pending
priority: high
tags: [agents, subagent, async-subagent, multi-model]
consumer_context:
  - task: TASK-OEX-002
    consumes: TOOLS
    framework: "create_deep_agent tools parameter"
    driver: "langchain_core.tools"
    format_note: "Tools must be @tool-decorated callables importable from tools/ package"
  - task: TASK-OEX-003
    consumes: PROMPTS
    framework: "SubAgent system_prompt field"
    driver: "deepagents SubAgent TypedDict"
    format_note: "Prompts must be string constants importable from prompts/ package"
  - task: TASK-OEX-004
    consumes: CONFIG
    framework: "yaml.safe_load + init_chat_model"
    driver: "pyyaml + langchain"
    format_note: "Model values must be 'provider:model' format strings compatible with init_chat_model()"
---

# Task: Create agent definitions for all four roles

## Description
Create the four agent definition modules:
1. `agents/orchestrator.py` — `create_orchestrator()` factory that builds the main agent with tools + subagents
2. `agents/implementer.py` — `implementer_subagent` SubAgent spec dict (sync, with tools)
3. `agents/evaluator.py` — `evaluator_subagent` SubAgent spec dict (sync, NO tools — `"tools": []`)
4. `agents/builder.py` — `builder_async_subagent` AsyncSubAgent spec dict (non-blocking)

## Reference
- Spec: docs/research/project_template/FEAT-orchestrator-exemplar-build.md (Section 3.1, 3.3)
- SDK SubAgent TypedDict: name, description, system_prompt (required), model (required), tools (required)
- SDK AsyncSubAgent TypedDict: name, description, graph_id (required), url (optional)
- SDK create_deep_agent: model, tools, system_prompt, subagents, memory, skills, context_schema

## SDK API Contracts (from review deep dive)

### SubAgent (sync) — Required fields:
```python
{
    "name": str,           # Required - unique identifier
    "description": str,    # Required - used by orchestrator to pick subagent
    "system_prompt": str,  # Required - instructions for the subagent
    "model": str,          # Required in new API - "provider:model" format
    "tools": list,         # Required in new API - explicit list (use [] for no tools)
}
```

### AsyncSubAgent — Required fields:
```python
{
    "name": str,           # Required - unique identifier
    "description": str,    # Required - what this subagent does
    "graph_id": str,       # Required - graph name on remote LangGraph server
    "url": str,            # Optional - omit for ASGI transport
}
```

## Acceptance Criteria
- [ ] `agents/orchestrator.py` exports `create_orchestrator(reasoning_model: str, implementation_model: str, domain_prompt: str) -> CompiledStateGraph`
- [ ] `create_orchestrator` uses `create_deep_agent()` with: model, tools, system_prompt, subagents (list of 3), memory, skills, context_schema
- [ ] `agents/implementer.py` exports `implementer_subagent` as a function that accepts `model: str` and returns SubAgent TypedDict
- [ ] Implementer SubAgent includes: name, description, system_prompt, model (required), tools (the 4 tools from TASK-OEX-002)
- [ ] `agents/evaluator.py` exports `evaluator_subagent` as a function that accepts `model: str` and returns SubAgent TypedDict
- [ ] Evaluator SubAgent includes: name, description, system_prompt, model (required), tools=[] (explicit empty list — NO tools)
- [ ] `agents/builder.py` exports `builder_async_subagent` as AsyncSubAgent TypedDict with: name, description, graph_id, url (configurable)
- [ ] `agents/__init__.py` exports all agent factories/specs
- [ ] All modified files pass project-configured lint/format checks with zero errors

## Seam Tests

The following seam tests validate the integration contracts with producer tasks.

```python
"""Seam test: verify TOOLS contract from TASK-OEX-002."""
import pytest


@pytest.mark.seam
@pytest.mark.integration_contract("TOOLS")
def test_tools_importable():
    """Verify tools are importable @tool-decorated callables.

    Contract: Tools must be @tool-decorated callables importable from tools/ package
    Producer: TASK-OEX-002
    """
    from tools import analyse_context, plan_pipeline, execute_command, verify_output
    from langchain_core.tools import BaseTool

    for tool in [analyse_context, plan_pipeline, execute_command, verify_output]:
        assert isinstance(tool, BaseTool), f"{tool} must be a BaseTool instance"


@pytest.mark.seam
@pytest.mark.integration_contract("PROMPTS")
def test_prompts_importable():
    """Verify prompts are importable string constants.

    Contract: Prompts must be string constants importable from prompts/ package
    Producer: TASK-OEX-003
    """
    from prompts import ORCHESTRATOR_SYSTEM_PROMPT, IMPLEMENTER_SYSTEM_PROMPT, EVALUATOR_SYSTEM_PROMPT

    for prompt in [ORCHESTRATOR_SYSTEM_PROMPT, IMPLEMENTER_SYSTEM_PROMPT, EVALUATOR_SYSTEM_PROMPT]:
        assert isinstance(prompt, str), f"Prompt must be a string"
        assert len(prompt) > 50, f"Prompt seems too short: {len(prompt)} chars"


@pytest.mark.seam
@pytest.mark.integration_contract("CONFIG")
def test_config_model_format():
    """Verify config model values use provider:model format.

    Contract: Model values must be 'provider:model' format strings compatible with init_chat_model()
    Producer: TASK-OEX-004
    """
    import yaml
    import pathlib

    config = yaml.safe_load(pathlib.Path("orchestrator-config.yaml").read_text())
    reasoning = config["orchestrator"]["reasoning_model"]
    implementation = config["orchestrator"]["implementation_model"]

    assert ":" in reasoning, f"reasoning_model must use provider:model format, got: {reasoning}"
    assert ":" in implementation, f"implementation_model must use provider:model format, got: {implementation}"
```

## Implementation Notes
- The orchestrator is NOT a peer of implementer/evaluator — it HAS subagents, they ARE subagents
- Evaluator MUST have `"tools": []` — SDK raises ValueError if `tools` key is missing in new API
- Builder async subagent targets a simple deployed agent for the exemplar (can be a stub endpoint)
- Each SubAgent factory function accepts a model string so the entrypoint can configure models from YAML
- Use `OrchestratorContext = TypedDict("OrchestratorContext", {...}, total=False)` for context_schema
