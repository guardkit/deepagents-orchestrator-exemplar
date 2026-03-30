---
id: TASK-OEX-006
title: "Create agent.py entrypoint wiring"
task_type: feature
parent_review: TASK-REV-8562
feature_id: FEAT-OEX
wave: 2
implementation_mode: task-work
complexity: 5
dependencies:
  - TASK-OEX-005
status: pending
priority: high
tags: [entrypoint, wiring, langgraph]
consumer_context:
  - task: TASK-OEX-005
    consumes: AGENT_FACTORIES
    framework: "create_orchestrator() + SubAgent factories"
    driver: "deepagents create_deep_agent"
    format_note: "create_orchestrator must accept reasoning_model, implementation_model, domain_prompt and return CompiledStateGraph"
  - task: TASK-OEX-004
    consumes: CONFIG
    framework: "yaml.safe_load"
    driver: "pyyaml"
    format_note: "orchestrator-config.yaml must have orchestrator.reasoning_model and orchestrator.implementation_model keys"
---

# Task: Create agent.py entrypoint wiring

## Description
Create `agent.py` that wires everything together: reads `orchestrator-config.yaml` for model selection, reads `domains/{domain}/DOMAIN.md` for domain context, and creates the orchestrator agent. Must export a module-level `agent` variable for `langgraph.json` compatibility.

## Reference
- Spec: docs/research/project_template/FEAT-orchestrator-exemplar-build.md (Section 3.2, 3.3)
- nvidia_deep_agent pattern: src/agent.py module-level `agent` variable
- langgraph.json: `{"graphs": {"orchestrator": "./agent.py:agent"}}`

## Data Flow
```
1. agent.py reads orchestrator-config.yaml -> selects reasoning_model + implementation_model
2. agent.py reads domains/{domain}/DOMAIN.md -> loads domain context
3. agent.py calls create_orchestrator(reasoning_model, implementation_model, domain_prompt)
4. Module-level: agent = create_orchestrator(...)
```

## Acceptance Criteria
- [ ] `agent.py` reads `orchestrator-config.yaml` using `yaml.safe_load()`
- [ ] `agent.py` reads domain prompt from `domains/example-domain/DOMAIN.md`
- [ ] `agent.py` calls `create_orchestrator()` with config values and domain prompt
- [ ] Module-level `agent` variable exported (required for langgraph.json)
- [ ] `python-dotenv` loads `.env` file for API keys
- [ ] Graceful handling if `.env` or domain file is missing (with defaults)
- [ ] All modified files pass project-configured lint/format checks with zero errors

## Seam Tests

```python
"""Seam test: verify AGENT_FACTORIES contract from TASK-OEX-005."""
import pytest


@pytest.mark.seam
@pytest.mark.integration_contract("AGENT_FACTORIES")
def test_create_orchestrator_signature():
    """Verify create_orchestrator accepts expected parameters.

    Contract: create_orchestrator must accept reasoning_model, implementation_model, domain_prompt and return CompiledStateGraph
    Producer: TASK-OEX-005
    """
    import inspect
    from agents.orchestrator import create_orchestrator

    sig = inspect.signature(create_orchestrator)
    params = list(sig.parameters.keys())
    assert "reasoning_model" in params, f"Missing reasoning_model param, got: {params}"
    assert "implementation_model" in params, f"Missing implementation_model param, got: {params}"
    assert "domain_prompt" in params, f"Missing domain_prompt param, got: {params}"
```

## Implementation Notes
- Pattern from nvidia_deep_agent: module-level assignment `agent = create_deep_agent(...)`
- Use `pathlib.Path` for file reading (consistent, cross-platform)
- Domain defaults to "example-domain" if not specified
- Config defaults to reasonable values if YAML file is missing
- `load_dotenv()` from python-dotenv for environment variable loading
