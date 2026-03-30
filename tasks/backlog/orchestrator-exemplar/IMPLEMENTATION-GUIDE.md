# Implementation Guide: DeepAgents Orchestrator Exemplar

## Overview

Build a three-role agent exemplar (Orchestrator + Implementer + Evaluator) with multi-model architecture and non-blocking AsyncSubAgent execution using the DeepAgents SDK 0.5.0a2.

**Source spec**: [FEAT-orchestrator-exemplar-build.md](../../../docs/research/project_template/FEAT-orchestrator-exemplar-build.md)
**Review task**: TASK-REV-8562
**Feature ID**: FEAT-OEX

---

## Data Flow: Read/Write Paths

```mermaid
flowchart LR
    subgraph Writes["Write Paths"]
        W1["agent.py\nreads config + domain"]
        W2["create_orchestrator()\nbuilds agent graph"]
        W3["Orchestrator LLM\ncalls tools + subagents"]
    end

    subgraph Storage["Storage / Config"]
        S1[("orchestrator-config.yaml\n(model selection)")]
        S2[("domains/DOMAIN.md\n(domain context)")]
        S3[("AGENTS.md\n(role boundaries)")]
        S4[("tools/\n(4 tool modules)")]
        S5[("prompts/\n(3 prompt modules)")]
    end

    subgraph Reads["Read Paths"]
        R1["agent.py\nstartup wiring"]
        R2["SubAgentMiddleware\ntask tool delegation"]
        R3["AsyncSubAgentMiddleware\nstart/check/update tools"]
        R4["langgraph.json\n./agent.py:agent"]
    end

    W1 -->|"yaml.safe_load"| S1
    W1 -->|"pathlib.read_text"| S2
    W2 -->|"memory= param"| S3
    W2 -->|"tools= param"| S4
    W2 -->|"system_prompt"| S5

    S1 -->|"model strings"| R1
    S2 -->|"domain_prompt"| R1
    S3 -->|"MemoryMiddleware"| R2
    S4 -->|"@tool callables"| R2
    S5 -->|"system_prompt str"| R2
    S1 -.->|"builder url/graph_id"| R3

    R1 -->|"module-level agent"| R4

    style R3 fill:#ffc,stroke:#cc0
```

**Note**: The AsyncSubAgent (Builder) path is marked yellow because it requires a running LangGraph server endpoint. For the exemplar, use `langgraph dev` locally or document as a deployment prerequisite.

---

## Integration Contracts

```mermaid
sequenceDiagram
    participant Config as orchestrator-config.yaml
    participant Agent as agent.py
    participant Orch as create_orchestrator()
    participant Tools as tools/*.py
    participant Prompts as prompts/*.py
    participant Impl as implementer_subagent
    participant Eval as evaluator_subagent
    participant Builder as builder_async_subagent
    participant LG as LangGraph Server

    Agent->>Config: yaml.safe_load()
    Config-->>Agent: reasoning_model, implementation_model

    Agent->>Prompts: import ORCHESTRATOR_SYSTEM_PROMPT
    Prompts-->>Agent: prompt string

    Agent->>Orch: create_orchestrator(reasoning_model, impl_model, domain_prompt)

    Orch->>Tools: import all 4 tools
    Tools-->>Orch: BaseTool instances

    Orch->>Impl: implementer_subagent(impl_model)
    Impl-->>Orch: SubAgent TypedDict (with tools)

    Orch->>Eval: evaluator_subagent(reasoning_model)
    Eval-->>Orch: SubAgent TypedDict (tools=[])

    Orch->>Builder: builder_async_subagent dict
    Builder-->>Orch: AsyncSubAgent TypedDict (graph_id + url)

    Note over Orch: create_deep_agent(model, tools, subagents=[impl, eval, builder])

    Note over Orch,LG: At runtime: Builder connects to LangGraph server via url
    Orch->>LG: start_async_task(description, subagent_type="builder")
    LG-->>Orch: task_id (non-blocking)
```

---

## Task Dependencies

```mermaid
graph TD
    T1[TASK-OEX-001<br/>Scaffold project] --> T5[TASK-OEX-005<br/>Agent definitions]
    T2[TASK-OEX-002<br/>Implement tools] --> T5
    T3[TASK-OEX-003<br/>Create prompts] --> T5
    T4[TASK-OEX-004<br/>Config + domain] --> T5
    T5 --> T6[TASK-OEX-006<br/>Entrypoint wiring]
    T6 --> T7[TASK-OEX-007<br/>Validation]

    style T1 fill:#cfc,stroke:#090
    style T2 fill:#cfc,stroke:#090
    style T3 fill:#cfc,stroke:#090
    style T4 fill:#cfc,stroke:#090
```

_Tasks with green background can run in parallel (Wave 1)._

---

## Execution Strategy

### Wave 1: Foundation (4 tasks, parallel)

| Task | Title | Complexity | Mode | Workspace |
|------|-------|-----------|------|-----------|
| TASK-OEX-001 | Scaffold project | 3/10 | direct | oex-wave1-1 |
| TASK-OEX-002 | Implement tools | 5/10 | task-work | oex-wave1-2 |
| TASK-OEX-003 | Create prompts | 4/10 | direct | oex-wave1-3 |
| TASK-OEX-004 | Config + domain | 3/10 | direct | oex-wave1-4 |

All four tasks are independent — no shared files, no data dependencies. Safe to run in parallel.

### Wave 2: Agents (2 tasks, sequential)

| Task | Title | Complexity | Mode | Dependencies |
|------|-------|-----------|------|--------------|
| TASK-OEX-005 | Agent definitions | 7/10 | task-work | All Wave 1 tasks |
| TASK-OEX-006 | Entrypoint wiring | 5/10 | task-work | TASK-OEX-005 |

TASK-OEX-005 depends on all Wave 1 outputs (tools, prompts, config). TASK-OEX-006 depends on TASK-OEX-005 (needs agent factories).

### Wave 3: Validation (1 task)

| Task | Title | Complexity | Mode | Dependencies |
|------|-------|-----------|------|--------------|
| TASK-OEX-007 | Validation | 4/10 | task-work | TASK-OEX-006 |

Runs the smoke test from spec Section 6 and verifies file tree completeness.

---

## SDK Corrections Applied

These corrections were identified during the review deep dive and are reflected in the task acceptance criteria:

1. **Evaluator `tools: []`** — SDK requires explicit `tools` field in new API. Evaluator must have `"tools": []`, not omit the field.
2. **Builder `graph_id`** — AsyncSubAgent TypedDict requires `graph_id` field (the graph name on the remote server).
3. **Module-level `agent`** — `agent.py` must export `agent = create_deep_agent(...)` at module level for `langgraph.json` compatibility.
4. **`provider:model` format** — Config values must use `"anthropic:claude-sonnet-4-6"` format for `init_chat_model()`.
5. **SubAgent `model` required** — Each SubAgent must include explicit `model` field (no inheritance in new API).

---

## §4: Integration Contracts

### Contract: TOOLS
- **Producer task:** TASK-OEX-002
- **Consumer task(s):** TASK-OEX-005
- **Artifact type:** Python module exports
- **Format constraint:** All four tools must be `@tool`-decorated callables importable from `tools/` package, each returning `str`
- **Validation method:** Import all tools and verify they are `BaseTool` instances

### Contract: PROMPTS
- **Producer task:** TASK-OEX-003
- **Consumer task(s):** TASK-OEX-005
- **Artifact type:** Python string constants
- **Format constraint:** `ORCHESTRATOR_SYSTEM_PROMPT`, `IMPLEMENTER_SYSTEM_PROMPT`, `EVALUATOR_SYSTEM_PROMPT` must be non-empty strings importable from `prompts/` package
- **Validation method:** Import all prompts and verify they are `str` with length > 50

### Contract: CONFIG
- **Producer task:** TASK-OEX-004
- **Consumer task(s):** TASK-OEX-005, TASK-OEX-006
- **Artifact type:** YAML configuration file
- **Format constraint:** `orchestrator-config.yaml` must have `orchestrator.reasoning_model` and `orchestrator.implementation_model` keys with `"provider:model"` format strings compatible with `init_chat_model()`
- **Validation method:** Load YAML and verify both model keys contain `:` separator

### Contract: AGENT_FACTORIES
- **Producer task:** TASK-OEX-005
- **Consumer task(s):** TASK-OEX-006
- **Artifact type:** Python factory functions
- **Format constraint:** `create_orchestrator(reasoning_model, implementation_model, domain_prompt)` must return `CompiledStateGraph`
- **Validation method:** Inspect function signature for required parameters

---

## Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| D1 | nvidia_deep_agent as backbone | Multi-model, subagent delegation, context_schema proven |
| D5 | Different models per role | Block paper: self-evaluation fails with single model |
| D6 | Three roles (O+I+E) | Orchestrator reasons, Implementer executes, Evaluator reviews |
| D7 | Tools as external wrappers | Exemplar uses stubs; production wraps GuardKit commands |
| D9 | uv + deepagents>=0.5.0a2 | SDK 0.5 required for AsyncSubAgent |

## Next Steps

1. Review task files in [tasks/backlog/orchestrator-exemplar/](.)
2. Start with Wave 1 tasks (4 parallel)
3. Use `/task-work TASK-OEX-001` to begin implementation
