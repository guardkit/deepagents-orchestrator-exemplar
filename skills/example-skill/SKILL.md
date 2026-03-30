---
name: example-skill
version: "1.0.0"
description: "An example skill demonstrating the SKILL.md format for the DeepAgents orchestrator."
author: "deepagents-team"
tags:
  - example
  - template
  - documentation
dependencies: []
inputs:
  - name: query
    type: string
    required: true
    description: "The input query or task description to process."
  - name: context
    type: string
    required: false
    description: "Optional additional context for the skill execution."
outputs:
  - name: result
    type: string
    description: "The processed output from the skill."
  - name: status
    type: string
    description: "Execution status: 'success', 'error', or 'partial'."
---

# Skill: Example Skill

## Purpose

This skill serves as a template demonstrating the standard SKILL.md format used
by the DeepAgents orchestrator. Skills are self-contained units of capability
that the orchestrator can discover and invoke during task execution.

## Description

The Example Skill processes an input query and optional context, returning a
structured result. In a production system, skills would encapsulate specific
capabilities such as code analysis, test generation, documentation writing, or
deployment automation.

## Usage

The orchestrator discovers skills by scanning the `skills/` directory for
`SKILL.md` files. The YAML frontmatter provides machine-readable metadata for
skill selection, while the markdown body provides human-readable documentation.

### Invocation

```python
# Skills are typically invoked by the orchestrator during plan execution.
# The orchestrator selects skills based on their metadata and the current task.

skill_input = {
    "query": "Analyse the project structure",
    "context": "Focus on the tools/ directory"
}
```

### Expected Behavior

1. The skill receives the input parameters defined in the frontmatter.
2. It processes the query using its internal logic.
3. It returns the output fields defined in the frontmatter.

## Examples

### Basic Invocation

**Input:**
```json
{
  "query": "What files are in the project?",
  "context": ""
}
```

**Output:**
```json
{
  "result": "The project contains: orchestrator-config.yaml, AGENTS.md, agent.py, tools/, prompts/, domains/, skills/",
  "status": "success"
}
```

### Invocation with Context

**Input:**
```json
{
  "query": "Summarise the tool implementations",
  "context": "Focus on error handling patterns"
}
```

**Output:**
```json
{
  "result": "All tools use try/except blocks and return error strings instead of raising exceptions.",
  "status": "success"
}
```

## Limitations

- This is a template skill and does not perform actual processing.
- Production skills should implement concrete logic behind the documented interface.
- Skills should be stateless; any required state must be passed via inputs.

## Related

- `AGENTS.md` — Defines the agent roles that invoke skills.
- `orchestrator-config.yaml` — Configures the models used during skill execution.
- `domains/` — Provides domain context that may influence skill behavior.
