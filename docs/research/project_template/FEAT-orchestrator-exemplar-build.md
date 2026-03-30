# Feature Specification: DeepAgents Orchestrator Exemplar

**Date:** March 2026
**Author:** Rich
**Status:** Ready for Implementation
**Research Method:** Claude Desktop ideation → this spec
**Target Repo:** `guardkit/deepagents-orchestrator-exemplar`
**Target Branch:** `main`

---

## 1. Problem Statement

Before building the GuardKit Factory Pipeline Orchestrator (`guardkit/guardkitfactory`), a working exemplar repo must exist. GuardKit's template philosophy is explicit: templates are created FROM proven working code, not authored by hand. This feature builds that exemplar by combining patterns from multiple official LangChain DeepAgents examples and the existing Player-Coach exemplar into a single repo that demonstrates an Orchestrator + Implementer + Evaluator pattern with multi-model architecture and non-blocking subagent execution.

The exemplar must run end-to-end, pass the TASK-REV validation checklist, and represent genuine best-practice patterns — not noise that would corrupt the downstream orchestrator build.

**Key difference from Player-Coach exemplar:** The original exemplar combined `deep_research` + `content-builder-agent` into a **two-agent data generation** pattern (Player generates, Coach evaluates). This exemplar adds a **reasoning orchestration layer** — an LLM that decides which tools to invoke, in what order, using `AsyncSubAgent` for non-blocking long-running operations. The pattern is Orchestrator → Implementer → Evaluator, where the Orchestrator is an LLM making tool-selection decisions.

---

## 2. Decision Log

| # | Decision | Rationale | Alternatives Rejected | ADR Status |
|---|----------|-----------|----------------------|------------|
| D1 | Use `nvidia_deep_agent` as structural backbone | Has multi-model architecture (frontier + Nemotron), subagent delegation via `task` tool, `init_chat_model()` for provider-agnostic model resolution, `context_schema` for runtime config, skills integration | Building from scratch (slower, no proven multi-model baseline) | Accepted |
| D2 | Borrow config-driven pattern from `content-builder-agent` and existing Player-Coach exemplar | `AGENTS.md` + `coach-config.yaml` + `domains/` externalisation is proven. Provider switching (local/API) is proven. | Hardcoding config in Python | Accepted |
| D3 | Borrow Player-Coach adversarial pattern from `deepagents-player-coach-exemplar` | Factory function pattern (`create_player()`, `create_coach()`), tool separation (Player has tools, Coach has none), structured JSON verdict schema are all proven | Re-inventing the adversarial pattern | Accepted |
| D4 | Use `AsyncSubAgent` (SDK 0.5.0a2) for long-running operations | AutoBuild feature builds take 15+ turns over hours. Non-blocking execution enables orchestrator to continue working while builds run. `start_async_task` / `check_async_task` / `update_async_task` pattern. | Synchronous-only (blocks orchestrator during long builds) | Accepted |
| D5 | Orchestrator uses different model from Implementer | Block paper + Anthropic validation: self-evaluation fails. Two-model separation prevents self-confirmation bias. `init_chat_model()` for each role. | Single model for all roles | Accepted |
| D6 | Three-role architecture: Orchestrator + Implementer + Evaluator | Orchestrator (reasoning model) decides what to do. Implementer (`SubAgent` or `AsyncSubAgent`) executes. Evaluator (`SubAgent`) reviews. Mirrors Anthropic's Planner → Generator → Evaluator. | Two-role only (loses the planning/reasoning layer) | Accepted |
| D7 | Orchestrator tools are external command wrappers | The orchestrator's tools wrap external operations (file analysis, context queries, command execution). In the exemplar, these are simplified stubs. In production (`guardkitfactory`), they wrap GuardKit slash commands. | Inline implementation (breaks the tool-wrapper pattern we need to validate) | Accepted |
| D8 | `orchestrator-config.yaml` for multi-model configuration | Configures: reasoning model, implementation model, checkpoint level, project settings. | Env vars only (less explicit), single config file (mixes concerns) | Accepted |
| D9 | `uv` for dependency management, pin `deepagents>=0.5.0a2` | Consistent with existing exemplar. SDK 0.5 required for `AsyncSubAgent`. | pip (less reproducible), older SDK (no async subagents) | Accepted |

**Warnings & Constraints:**
- `AsyncSubAgent` requires a LangGraph server endpoint (via `url` + `graph_id`) or ASGI transport for local servers
- The orchestrator's `create_deep_agent()` call must include `subagents=` with a mix of `SubAgent` (sync) and `AsyncSubAgent` (async) specs
- `AsyncSubAgent` state is tracked in `async_tasks` state key — survives context compaction
- For the exemplar, the `AsyncSubAgent` can target a simple deployed agent (e.g. a research subagent via `langgraph dev`) rather than a full AutoBuild deployment
- Orchestrator and Implementer are NOT peer agents like Player/Coach — the Orchestrator has subagents, the Implementer IS a subagent

---

## 3. Architecture

### 3.1 Component Design

| Component | File Path | Purpose | Source |
|-----------|-----------|---------|--------|
| Entrypoint | `agent.py` | Wires everything, reads config, creates orchestrator agent | nvidia_deep_agent pattern |
| Orchestrator agent | `agents/orchestrator.py` | `create_orchestrator()` — reasoning model with tools + subagents | NEW (nvidia_deep_agent + AsyncSubAgent) |
| Implementer subagent | `agents/implementer.py` | `SubAgent` spec dict — synchronous execution subagent | Player-Coach exemplar pattern |
| Evaluator subagent | `agents/evaluator.py` | `SubAgent` spec dict — synchronous evaluation subagent (no tools) | Player-Coach exemplar pattern (Coach) |
| Builder async subagent | `agents/builder.py` | `AsyncSubAgent` spec dict — non-blocking long-running operations | NEW (SDK 0.5 AsyncSubAgent) |
| Analyse tool | `tools/analyse_context.py` | Reads and summarises project context | NEW (wraps file reading) |
| Plan tool | `tools/plan_pipeline.py` | Proposes a pipeline execution plan | NEW (orchestrator reasoning) |
| Execute tool | `tools/execute_command.py` | Executes an external command and returns result | NEW (command wrapper pattern) |
| Verify tool | `tools/verify_output.py` | Runs verification checks on completed work | NEW |
| Orchestrator prompts | `prompts/orchestrator_prompts.py` | `ORCHESTRATOR_SYSTEM_PROMPT` — reasoning and tool selection | NEW (nvidia_deep_agent style) |
| Implementer prompts | `prompts/implementer_prompts.py` | `IMPLEMENTER_SYSTEM_PROMPT` — execution instructions | Player-Coach exemplar (Player) |
| Evaluator prompts | `prompts/evaluator_prompts.py` | `EVALUATOR_SYSTEM_PROMPT` — evaluation criteria + JSON schema | Player-Coach exemplar (Coach) |
| Agent boundaries | `AGENTS.md` | ALWAYS/NEVER/ASK per role | content-builder pattern |
| Orchestrator config | `orchestrator-config.yaml` | Multi-model config, checkpoint levels, project settings | NEW |
| Domain config | `domains/example-domain/DOMAIN.md` | Domain-specific guidelines and criteria | Player-Coach exemplar |
| Skills | `skills/example-skill/SKILL.md` | Skill documentation for implementer | nvidia_deep_agent pattern |
| LangGraph config | `langgraph.json` | Deployment configuration | deep_research pattern |
| Dependencies | `pyproject.toml` | uv-managed, pins deepagents>=0.5.0a2 | standard |

### 3.2 Data Flow

```
1. agent.py reads orchestrator-config.yaml → selects reasoning model + implementation model
2. agent.py reads domains/{domain}/DOMAIN.md → loads domain context
3. Orchestrator agent receives task: "build feature X for project Y"
4. Orchestrator calls analyse_context tool → gets project/domain context
5. Orchestrator calls plan_pipeline tool → proposes execution steps
6. Orchestrator evaluates plan using Evaluator SubAgent (sync) → gets structured verdict
7a. For quick operations: Orchestrator delegates to Implementer SubAgent (sync)
7b. For long-running operations: Orchestrator launches Builder AsyncSubAgent (non-blocking)
8. Orchestrator calls verify_output tool → checks results
9. Orchestrator calls check_async_task periodically for async operations
10. Loop continues until all planned steps complete or orchestrator decides to stop
```

### 3.3 Agent Wiring (in agent.py)

```python
from deepagents import create_deep_agent, AsyncSubAgent

orchestrator = create_deep_agent(
    model=reasoning_model,                    # e.g. "google:gemini-3.1-pro"
    tools=[analyse_context, plan_pipeline, execute_command, verify_output],
    system_prompt=ORCHESTRATOR_SYSTEM_PROMPT + "\n\n" + domain_prompt,
    subagents=[
        implementer_subagent,                 # SubAgent (sync) — quick execution
        evaluator_subagent,                   # SubAgent (sync) — quality evaluation
        builder_async_subagent,               # AsyncSubAgent — long-running builds
    ],
    memory=["./AGENTS.md"],
    skills=["./skills/"],
    context_schema=OrchestratorContext,        # Runtime config (from nvidia_deep_agent)
)
```

---

## 4. API Contracts

### Evaluator Verdict Schema

Same proven schema from Player-Coach exemplar:

```json
{
  "decision": "accept | revise | reject",
  "score": 1-5,
  "issues": ["specific problem descriptions"],
  "criteria_met": true | false,
  "quality_assessment": "high | adequate | needs_revision"
}
```

### Tool Contracts

All tools return strings, never raise exceptions (proven pattern from Player-Coach).

| Tool | Input | Output |
|------|-------|--------|
| `analyse_context` | `query: str, domain: str` | Context summary string |
| `plan_pipeline` | `task: str, context: str` | JSON pipeline plan string |
| `execute_command` | `command: str, args: str` | Execution result string |
| `verify_output` | `output_path: str, criteria: str` | Verification result string |

---

## 5. Implementation Tasks

### Wave 1: Foundation (parallel)

- **TASK-OEX-001** — Scaffold: `pyproject.toml` (deepagents>=0.5.0a2), `.env.example`, `.gitignore`, `langgraph.json`
- **TASK-OEX-002** — Tools: `analyse_context`, `plan_pipeline`, `execute_command`, `verify_output` (all @tool decorated, return strings)
- **TASK-OEX-003** — Prompts: orchestrator, implementer, evaluator system prompts (domain-agnostic, criteria from DOMAIN.md)
- **TASK-OEX-004** — Config: `orchestrator-config.yaml` (multi-model), `AGENTS.md` (three-role boundaries), `domains/example-domain/DOMAIN.md`, `skills/example-skill/SKILL.md`

### Wave 2: Agents (sequential, depends on Wave 1)

- **TASK-OEX-005** — Agent definitions: `orchestrator.py` (creates main agent with subagents), `implementer.py` (SubAgent spec), `evaluator.py` (SubAgent spec, no tools), `builder.py` (AsyncSubAgent spec)
- **TASK-OEX-006** — Entrypoint: `agent.py` wires config → models → agents → module-level `agent` variable

### Wave 3: Validation

- **TASK-OEX-007** — Run TASK-REV validation checklist, fix any failures

---

## 6. Test Strategy

### Smoke test (after Wave 2)

```bash
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
import yaml, pathlib
config = yaml.safe_load(pathlib.Path('orchestrator-config.yaml').read_text())
domain = pathlib.Path('domains/example-domain/DOMAIN.md').read_text()
assert config['orchestrator']['reasoning_model'] is not None
assert config['orchestrator']['implementation_model'] is not None
print('Full smoke test OK — ready for validation')
"
```

---

## 7. Target File Tree

```
deepagents-orchestrator-exemplar/
├── pyproject.toml
├── .env.example
├── .gitignore
├── README.md
├── AGENTS.md
├── orchestrator-config.yaml
├── langgraph.json
├── agent.py
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── implementer.py
│   ├── evaluator.py
│   └── builder.py
├── tools/
│   ├── __init__.py
│   ├── analyse_context.py
│   ├── plan_pipeline.py
│   ├── execute_command.py
│   └── verify_output.py
├── prompts/
│   ├── __init__.py
│   ├── orchestrator_prompts.py
│   ├── implementer_prompts.py
│   └── evaluator_prompts.py
├── domains/
│   └── example-domain/
│       └── DOMAIN.md
├── skills/
│   └── example-skill/
│       └── SKILL.md
└── docs/
    └── research/
        └── project_template/
            ├── FEAT-orchestrator-exemplar-build.md
            └── TASK-REV-orchestrator-exemplar-validation.md
```

---

## 8. Dependencies

### Python dependencies (in `pyproject.toml`)
```
deepagents>=0.5.0a2
langchain>=1.2.11
langchain-core>=1.2.21
langgraph>=0.2
langsmith>=0.3
python-dotenv>=1.0
pyyaml>=6.0
```

### Environment variables (from `.env`)
```
LANGSMITH_API_KEY=<from smith.langchain.com>
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=deepagents-orchestrator-exemplar
ANTHROPIC_API_KEY=<for Claude reasoning model>
GOOGLE_API_KEY=<optional — for Gemini reasoning model>
LOCAL_MODEL_ENDPOINT=http://localhost:8000/v1
```

---

## 9. Out of Scope

- Real GuardKit slash command integration (exemplar uses simplified tool stubs)
- NATS JetStream integration (downstream `guardkitfactory` concern)
- Multi-project management (downstream concern)
- Full end-to-end run with AutoBuild (exemplar proves the three-role wiring pattern)
- Production AsyncSubAgent deployment (exemplar validates the spec pattern)

---

## 10. Revision Log

| Date | Reviewer | Finding | Change |
|------|----------|---------|--------|
| 2026-03-30 | Initial | N/A | Created from original FEAT-deepagents-exemplar-build.md methodology |

---

*FEAT prepared March 2026 | Consumed by `/task-review` or manual implementation*
