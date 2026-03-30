# Domain: Example Domain

This file defines domain-specific guidelines and evaluation criteria for the
**Example Domain**. Domain content is injected into the Orchestrator's system
prompt at runtime to provide context-aware planning and evaluation.

---

## Overview

The Example Domain demonstrates how domain-specific knowledge is structured and
made available to the orchestrator. In a production system, each domain would
represent a distinct area of expertise (e.g., "web-frontend", "data-pipeline",
"infrastructure", "security-audit").

## Domain Guidelines

### Code Quality Standards

- All code must include type hints for function parameters and return values.
- Functions must have docstrings following Google-style format.
- Maximum function length: 50 lines (excluding docstring).
- Maximum cyclomatic complexity per function: 10.

### File Organization

- One primary class or concern per module.
- Related utilities grouped in a `utils/` sub-package.
- Test files mirror the source structure under `tests/`.

### Naming Conventions

- Snake case for functions and variables: `analyse_context`, `plan_pipeline`.
- Pascal case for classes: `OrchestratorAgent`, `TaskResult`.
- Upper snake case for constants: `MAX_RETRIES`, `DEFAULT_TIMEOUT`.
- Descriptive names that convey intent; avoid single-letter variables outside
  loop indices.

### Error Handling

- Tool functions must never raise exceptions; wrap all logic in try/except and
  return error strings.
- Use structured error responses with consistent fields:
  `{"error": true, "message": "...", "context": "..."}`.

## Evaluation Criteria

When the Evaluator reviews work in this domain, it must check:

### Functional Criteria

1. **Correctness**: Does the implementation satisfy all stated acceptance criteria?
2. **Completeness**: Are all required files, functions, and configurations present?
3. **Integration**: Does the code work correctly with existing project components?

### Structural Criteria

4. **Type Safety**: Are all function signatures fully typed?
5. **Documentation**: Do all public functions have docstrings?
6. **Test Coverage**: Is there at least one test for each public function?
7. **Error Handling**: Do all tool functions handle errors without raising exceptions?

### Style Criteria

8. **Naming**: Do all identifiers follow the naming conventions above?
9. **Organization**: Are files and modules organized according to the guidelines?
10. **Simplicity**: Is the implementation as simple as possible while meeting all
    criteria?

## Domain-Specific Context

This example domain is intentionally generic to serve as a template. When
creating a new domain, replace this section with:

- **Technology stack details**: frameworks, libraries, and versions in use.
- **Architecture patterns**: service boundaries, data flow diagrams, API contracts.
- **Business rules**: domain logic that must be preserved during implementation.
- **Compliance requirements**: regulatory or organizational standards that apply.
- **Known constraints**: performance budgets, compatibility requirements, or
  deployment limitations.
