---
id: TASK-EVF-002
title: Add local endpoint section to orchestrator-config.yaml
status: completed
priority: minor
complexity: 1
parent_review: TASK-REV-orchestrator-exemplar-validation
feature_id: FEAT-EVF
wave: 1
implementation_mode: direct
dependencies: []
tags: [config, exemplar-fix]
---

# TASK-EVF-002: Add local endpoint section to orchestrator-config.yaml

## Problem

The review checklist requires a `local` section with an `endpoint` field in
`orchestrator-config.yaml` for vLLM / local model support. This section is
currently missing.

## Acceptance Criteria

- [ ] `orchestrator-config.yaml` contains `local.endpoint` field under `orchestrator`
- [ ] Endpoint defaults to `http://localhost:8000/v1`
- [ ] Field is commented to explain its purpose
- [ ] YAML remains valid after edit

## Implementation

Add the following under the `orchestrator` key:

```yaml
  # Local model endpoint for vLLM or compatible OpenAI-API servers
  local:
    endpoint: "http://localhost:8000/v1"
```

## Files to Modify

- `orchestrator-config.yaml`
