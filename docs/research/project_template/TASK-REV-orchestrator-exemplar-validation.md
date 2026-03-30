# TASK-REV: DeepAgents Orchestrator Exemplar Validation
## Before using exemplar to build guardkit/guardkitfactory

**Task Type:** review
**Complexity:** medium
**Domain tags:** `deepagents, langchain, template, python, orchestrator, async-subagent`
**Prerequisite for:** Building `guardkit/guardkitfactory` from validated exemplar
**Date:** March 2026

---

## Context

Before using this exemplar to build the Pipeline Orchestrator (`guardkit/guardkitfactory`),
this review verifies the exemplar is structurally sound, runs correctly, and
represents genuine best-practice patterns.

The exemplar implements a three-role Orchestrator + Implementer + Evaluator pattern
combining patterns from:
- `nvidia_deep_agent` — multi-model architecture, subagent delegation, context_schema
- `deepagents-player-coach-exemplar` — Player-Coach adversarial, provider switching
- `AsyncSubAgent` middleware (SDK 0.5.0a2) — non-blocking long-running operations

---

## Target Structure

```
deepagents-orchestrator-exemplar/
├── pyproject.toml
├── .env.example
├── AGENTS.md
├── orchestrator-config.yaml
├── langgraph.json
├── README.md
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
└── skills/
    └── example-skill/
        └── SKILL.md
```

---

## Review Checklist

### Section 1: Environment and Dependencies

- [ ] `pyproject.toml` exists and is valid TOML
- [ ] `deepagents>=0.5.0a2` is listed (required for AsyncSubAgent)
- [ ] `langchain`, `langgraph`, `langsmith` are present
- [ ] `python-dotenv` and `pyyaml` are present
- [ ] `uv sync` completes without errors from clean environment
- [ ] `uv run python -c "from deepagents import create_deep_agent, AsyncSubAgent; print('OK')"` passes
- [ ] `.env.example` documents: `LANGSMITH_API_KEY`, `LANGSMITH_TRACING`, `LANGSMITH_PROJECT`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` (optional), `LOCAL_MODEL_ENDPOINT`
- [ ] No API keys or secrets in tracked files

---

### Section 2: Entrypoint (`agent.py`)

- [ ] Imports `create_orchestrator` from `agents.orchestrator`
- [ ] Imports `init_chat_model` from `langchain.chat_models`
- [ ] Reads `orchestrator-config.yaml` for model configuration
- [ ] Creates separate model instances for reasoning and implementation roles
- [ ] Reads domain config from `domains/{domain}/DOMAIN.md`
- [ ] Supports `--domain` CLI argument (defaults to `example-domain`)
- [ ] Defines module-level `agent` variable (required for `langgraph.json`)
- [ ] No model strings hardcoded

**Anti-patterns to reject:**
- [ ] Reasoning model == implementation model (must be different)
- [ ] API keys hardcoded
- [ ] All three roles sharing the same system prompt

---

### Section 3: Orchestrator config (`orchestrator-config.yaml`)

- [ ] File parses as valid YAML
- [ ] Contains `orchestrator.reasoning_model` field (e.g. `anthropic:claude-sonnet-4-6`)
- [ ] Contains `orchestrator.implementation_model` field (e.g. `openai:local-model` or `anthropic:claude-sonnet-4-6`)
- [ ] Reasoning model and implementation model are DIFFERENT
- [ ] Contains `local` section with `endpoint` field for local vLLM
- [ ] Switching providers changes model without code changes

**Expected structure:**
```yaml
orchestrator:
  reasoning_model: anthropic:claude-sonnet-4-6
  implementation_model: openai:local-model
  local:
    endpoint: http://localhost:8000/v1
  checkpoint_level: standard  # minimal | standard | full
```

---

### Section 4: Agent definitions

**orchestrator.py:**
- [ ] Imports `create_deep_agent` from `deepagents`
- [ ] Defines `create_orchestrator(reasoning_model, implementation_model, domain_prompt)` factory
- [ ] Returns `create_deep_agent()` with `tools=`, `subagents=`, `memory=`, `skills=`
- [ ] Subagents list includes both `SubAgent` (sync) and `AsyncSubAgent` (async) specs
- [ ] Uses `context_schema` parameter (from nvidia_deep_agent pattern)
- [ ] Function is callable without side effects (no top-level instantiation)

**implementer.py:**
- [ ] Defines `implementer_subagent` as a `SubAgent` TypedDict
- [ ] Has `name`, `description`, `system_prompt` fields
- [ ] Has `tools` field with implementation tools
- [ ] Has `model` field set to implementation_model (NOT reasoning_model)

**evaluator.py:**
- [ ] Defines `evaluator_subagent` as a `SubAgent` TypedDict
- [ ] Has `name`, `description`, `system_prompt` fields
- [ ] Has `tools: []` — explicitly empty (evaluator has NO custom tools)
- [ ] Does NOT specify `model` (inherits from orchestrator, or specify reasoning_model)

**builder.py:**
- [ ] Defines `builder_async_subagent` as an `AsyncSubAgent` TypedDict
- [ ] Has `name`, `description`, `graph_id` fields
- [ ] Has `url` field (for remote LangGraph server endpoint)
- [ ] Does NOT have `tools` or `model` fields (AsyncSubAgent doesn't use these)

**Anti-patterns to reject:**
- [ ] Agent instantiated at module level
- [ ] Evaluator given any custom tools
- [ ] Implementer and Evaluator using the same model as Orchestrator without justification
- [ ] AsyncSubAgent missing `graph_id`

---

### Section 5: Tools

All tools must be `@tool` decorated, return strings, never raise exceptions.

**analyse_context.py:**
- [ ] `@tool` decorated with clear docstring
- [ ] Returns context summary string
- [ ] Handles missing files/data gracefully (returns error string, not exception)

**plan_pipeline.py:**
- [ ] `@tool` decorated with clear docstring
- [ ] Returns JSON pipeline plan as string
- [ ] Validates inputs, returns error string on failure

**execute_command.py:**
- [ ] `@tool` decorated with clear docstring
- [ ] Returns command result as string
- [ ] Handles command failure gracefully (returns error string)
- [ ] Does NOT execute arbitrary shell commands (safety constraint)

**verify_output.py:**
- [ ] `@tool` decorated with clear docstring
- [ ] Returns verification result string
- [ ] Handles missing output gracefully

---

### Section 6: Prompts

**orchestrator_prompts.py:**
- [ ] Defines `ORCHESTRATOR_SYSTEM_PROMPT` as module-level string constant
- [ ] Instructs orchestrator to analyse context BEFORE planning
- [ ] Instructs orchestrator to evaluate plans using Evaluator subagent
- [ ] Instructs orchestrator to use AsyncSubAgent for long-running operations
- [ ] Does NOT contain domain-specific content (injected from DOMAIN.md)
- [ ] Length > 400 chars

**implementer_prompts.py:**
- [ ] Defines `IMPLEMENTER_SYSTEM_PROMPT` as module-level string constant
- [ ] Instructs implementer to execute tasks and report results
- [ ] Length > 200 chars

**evaluator_prompts.py:**
- [ ] Defines `EVALUATOR_SYSTEM_PROMPT` as module-level string constant
- [ ] Instructs evaluator to return ONLY valid JSON verdict
- [ ] Defines verdict schema: `{decision, score, issues, criteria_met, quality_assessment}`
- [ ] Instructs evaluator it does NOT have write tools
- [ ] Length > 400 chars

---

### Section 7: AGENTS.md

- [ ] Describes three agent roles: Orchestrator, Implementer, Evaluator
- [ ] Each role has ALWAYS/NEVER/ASK sections:

  ```
  ## Orchestrator
  ALWAYS: analyse context before planning, evaluate plans before execution,
          use AsyncSubAgent for long-running operations
  NEVER: execute implementation directly (delegate to Implementer),
         skip evaluation step, hardcode model choices
  ASK: when checkpoint_level requires human approval

  ## Implementer
  ALWAYS: execute assigned tasks, report results with evidence,
          follow domain guidelines from DOMAIN.md
  NEVER: evaluate own work (that's Evaluator's job),
         modify orchestrator plans, skip verification
  ASK: (none currently defined)

  ## Evaluator
  ALWAYS: return structured JSON verdict, evaluate against domain criteria,
          be sceptical (Block paper principle)
  NEVER: write files, modify content, execute commands,
         return prose instead of JSON
  ASK: when score is 3 (borderline) — flag for human review
  ```

- [ ] Referenced in agent factory via `memory=["./AGENTS.md"]`
- [ ] No domain-specific terms

---

### Section 8: Domain and Skills config

- [ ] `domains/example-domain/DOMAIN.md` exists and is valid Markdown
- [ ] Contains sections: Domain Description, Guidelines, Evaluation Criteria, Output Format
- [ ] Content is clearly a GENERIC EXAMPLE with "replace this" notes
- [ ] `skills/example-skill/SKILL.md` exists
- [ ] Skill is a simple example demonstrating the skills/ pattern

---

### Section 9: LangSmith integration

- [ ] `LANGSMITH_TRACING=true` documented in `.env.example`
- [ ] `LANGSMITH_PROJECT=deepagents-orchestrator-exemplar` in `.env.example`
- [ ] No explicit callback setup (DeepAgents traces automatically)

---

### Section 10: Smoke test

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
print('All imports OK')
"
```

- [ ] All imports resolve without error
- [ ] `uv run python agent.py --help` runs without error

---

## Review Decision

### PASS criteria (all must be true)
- All Section 1 dependency checks pass
- Sections 2-8 have zero FAIL on anti-pattern items
- Section 10 smoke test passes (all imports OK)
- No API keys in tracked files
- Reasoning model ≠ implementation model in config
- AsyncSubAgent spec has `graph_id` field
- Evaluator has NO custom tools

### FAIL criteria (any one blocks the build)
- `uv sync` fails
- Any import in Section 10 fails
- Reasoning model == implementation model
- Evaluator has custom tools
- `AsyncSubAgent` spec missing `graph_id`
- API keys present in tracked files

---

## After this review passes

The validated exemplar is used to build `guardkit/guardkitfactory`:

```bash
# Copy conversation starter to guardkitfactory
cp docs/research/pipeline-orchestrator-conversation-starter.md \
   /path/to/guardkitfactory/docs/research/

# Run /system-arch in guardkitfactory using this exemplar as context
cd /path/to/guardkitfactory
# /system-arch --context docs/research/pipeline-orchestrator-conversation-starter.md
```

---

*TASK-REV prepared March 2026 | Orchestrator exemplar validation | Modelled on TASK-REV-deepagents-exemplar-validation.md*
