"""Comprehensive tests for system prompts (TASK-OEX-003).

Tests cover:
- AC-001: orchestrator_prompts.py exports ORCHESTRATOR_SYSTEM_PROMPT
- AC-002: implementer_prompts.py exports IMPLEMENTER_SYSTEM_PROMPT
- AC-003: evaluator_prompts.py exports EVALUATOR_SYSTEM_PROMPT with JSON verdict schema
- AC-004: Orchestrator prompt instructs: analyse context, plan pipeline, delegate, verify
- AC-005: Orchestrator prompt supports {domain_prompt} placeholder
- AC-006: Evaluator prompt includes full JSON verdict schema
- AC-007: prompts/__init__.py exports all three prompt constants
- AC-008: No hardcoded domain references in prompts (domain-agnostic)
"""

import json
import re
import sys
import os

import pytest

# Ensure the project root is on sys.path so we can import `prompts` as a package.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ---------------------------------------------------------------------------
# AC-001: orchestrator_prompts.py exports ORCHESTRATOR_SYSTEM_PROMPT
# ---------------------------------------------------------------------------

class TestOrchestratorPromptExport:
    """AC-001: prompts/orchestrator_prompts.py exports ORCHESTRATOR_SYSTEM_PROMPT."""

    def test_import_from_module(self):
        from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
        assert isinstance(ORCHESTRATOR_SYSTEM_PROMPT, str)
        assert len(ORCHESTRATOR_SYSTEM_PROMPT) > 100  # non-trivial content

    def test_is_string_constant(self):
        from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
        assert isinstance(ORCHESTRATOR_SYSTEM_PROMPT, str)


# ---------------------------------------------------------------------------
# AC-002: implementer_prompts.py exports IMPLEMENTER_SYSTEM_PROMPT
# ---------------------------------------------------------------------------

class TestImplementerPromptExport:
    """AC-002: prompts/implementer_prompts.py exports IMPLEMENTER_SYSTEM_PROMPT."""

    def test_import_from_module(self):
        from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT
        assert isinstance(IMPLEMENTER_SYSTEM_PROMPT, str)
        assert len(IMPLEMENTER_SYSTEM_PROMPT) > 100

    def test_is_string_constant(self):
        from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT
        assert isinstance(IMPLEMENTER_SYSTEM_PROMPT, str)


# ---------------------------------------------------------------------------
# AC-003: evaluator_prompts.py exports EVALUATOR_SYSTEM_PROMPT with JSON verdict
# ---------------------------------------------------------------------------

class TestEvaluatorPromptExport:
    """AC-003: prompts/evaluator_prompts.py exports EVALUATOR_SYSTEM_PROMPT."""

    def test_import_from_module(self):
        from prompts.evaluator_prompts import EVALUATOR_SYSTEM_PROMPT
        assert isinstance(EVALUATOR_SYSTEM_PROMPT, str)
        assert len(EVALUATOR_SYSTEM_PROMPT) > 100

    def test_verdict_schema_constant_exported(self):
        from prompts.evaluator_prompts import EVALUATOR_VERDICT_SCHEMA
        assert isinstance(EVALUATOR_VERDICT_SCHEMA, str)
        assert "decision" in EVALUATOR_VERDICT_SCHEMA
        assert "score" in EVALUATOR_VERDICT_SCHEMA


# ---------------------------------------------------------------------------
# AC-004: Orchestrator prompt instructs: analyse, plan, delegate, verify
# ---------------------------------------------------------------------------

class TestOrchestratorInstructions:
    """AC-004: Orchestrator prompt contains all four key instruction areas."""

    @pytest.fixture
    def prompt(self):
        from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
        return ORCHESTRATOR_SYSTEM_PROMPT

    def test_analyse_context_instruction(self, prompt):
        assert "analyse" in prompt.lower() or "analyze" in prompt.lower()
        assert "context" in prompt.lower()

    def test_plan_pipeline_instruction(self, prompt):
        assert "plan" in prompt.lower()
        assert "pipeline" in prompt.lower()

    def test_delegate_to_subagents_instruction(self, prompt):
        assert "delegate" in prompt.lower()
        assert "subagent" in prompt.lower()

    def test_verify_results_instruction(self, prompt):
        assert "verify" in prompt.lower()
        assert "result" in prompt.lower()

    def test_analyse_context_tool_mentioned(self, prompt):
        assert "analyse_context" in prompt

    def test_plan_pipeline_tool_mentioned(self, prompt):
        assert "plan_pipeline" in prompt

    def test_verify_output_tool_mentioned(self, prompt):
        assert "verify_output" in prompt

    def test_execute_command_tool_mentioned(self, prompt):
        assert "execute_command" in prompt


# ---------------------------------------------------------------------------
# AC-005: Orchestrator prompt supports {domain_prompt} placeholder
# ---------------------------------------------------------------------------

class TestDomainPromptPlaceholder:
    """AC-005: Orchestrator prompt supports {domain_prompt} placeholder."""

    @pytest.fixture
    def prompt(self):
        from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
        return ORCHESTRATOR_SYSTEM_PROMPT

    def test_domain_prompt_placeholder_present(self, prompt):
        assert "{domain_prompt}" in prompt

    def test_domain_prompt_placeholder_is_replaceable(self, prompt):
        test_domain = "You are operating in the financial services domain."
        rendered = prompt.format(domain_prompt=test_domain, date="2026-03-30")
        assert test_domain in rendered
        assert "{domain_prompt}" not in rendered

    def test_date_placeholder_present(self, prompt):
        assert "{date}" in prompt

    def test_date_placeholder_is_replaceable(self, prompt):
        rendered = prompt.format(domain_prompt="test", date="2026-03-30")
        assert "2026-03-30" in rendered
        assert "{date}" not in rendered


# ---------------------------------------------------------------------------
# AC-006: Evaluator prompt includes full JSON verdict schema
# ---------------------------------------------------------------------------

class TestEvaluatorVerdictSchema:
    """AC-006: Evaluator prompt includes JSON verdict schema with all fields."""

    @pytest.fixture
    def prompt(self):
        from prompts.evaluator_prompts import EVALUATOR_SYSTEM_PROMPT
        return EVALUATOR_SYSTEM_PROMPT

    @pytest.fixture
    def verdict_schema(self):
        from prompts.evaluator_prompts import EVALUATOR_VERDICT_SCHEMA
        return EVALUATOR_VERDICT_SCHEMA

    def test_decision_field_present(self, prompt):
        assert "decision" in prompt

    def test_decision_values_present(self, prompt):
        assert "accept" in prompt
        assert "revise" in prompt
        assert "reject" in prompt

    def test_score_field_present(self, prompt):
        assert "score" in prompt

    def test_score_range_described(self, prompt):
        # Score should be 1-5
        assert "1" in prompt and "5" in prompt

    def test_issues_field_present(self, prompt):
        assert "issues" in prompt

    def test_criteria_met_field_present(self, prompt):
        assert "criteria_met" in prompt

    def test_quality_assessment_field_present(self, prompt):
        assert "quality_assessment" in prompt

    def test_quality_assessment_values_present(self, prompt):
        assert "high" in prompt
        assert "adequate" in prompt
        assert "needs_revision" in prompt

    def test_verdict_schema_contains_all_fields(self, verdict_schema):
        """Verify the standalone schema constant has all required fields."""
        assert "decision" in verdict_schema
        assert "score" in verdict_schema
        assert "issues" in verdict_schema
        assert "criteria_met" in verdict_schema
        assert "quality_assessment" in verdict_schema

    def test_verdict_schema_decision_values(self, verdict_schema):
        assert "accept" in verdict_schema
        assert "revise" in verdict_schema
        assert "reject" in verdict_schema

    def test_verdict_schema_quality_values(self, verdict_schema):
        assert "high" in verdict_schema
        assert "adequate" in verdict_schema
        assert "needs_revision" in verdict_schema

    def test_evaluator_prompt_has_date_placeholder(self, prompt):
        """Evaluator prompt should also support {date} placeholder."""
        assert "{date}" in prompt

    def test_evaluator_prompt_date_is_replaceable(self, prompt):
        rendered = prompt.format(date="2026-03-30")
        assert "2026-03-30" in rendered


# ---------------------------------------------------------------------------
# AC-007: prompts/__init__.py exports all three prompt constants
# ---------------------------------------------------------------------------

class TestInitExports:
    """AC-007: prompts/__init__.py exports all three prompt constants."""

    def test_import_orchestrator_from_init(self):
        from prompts import ORCHESTRATOR_SYSTEM_PROMPT
        assert isinstance(ORCHESTRATOR_SYSTEM_PROMPT, str)
        assert len(ORCHESTRATOR_SYSTEM_PROMPT) > 0

    def test_import_implementer_from_init(self):
        from prompts import IMPLEMENTER_SYSTEM_PROMPT
        assert isinstance(IMPLEMENTER_SYSTEM_PROMPT, str)
        assert len(IMPLEMENTER_SYSTEM_PROMPT) > 0

    def test_import_evaluator_from_init(self):
        from prompts import EVALUATOR_SYSTEM_PROMPT
        assert isinstance(EVALUATOR_SYSTEM_PROMPT, str)
        assert len(EVALUATOR_SYSTEM_PROMPT) > 0

    def test_import_verdict_schema_from_init(self):
        from prompts import EVALUATOR_VERDICT_SCHEMA
        assert isinstance(EVALUATOR_VERDICT_SCHEMA, str)
        assert len(EVALUATOR_VERDICT_SCHEMA) > 0

    def test_all_exports_in_dunder_all(self):
        import prompts
        assert hasattr(prompts, "__all__")
        assert "ORCHESTRATOR_SYSTEM_PROMPT" in prompts.__all__
        assert "IMPLEMENTER_SYSTEM_PROMPT" in prompts.__all__
        assert "EVALUATOR_SYSTEM_PROMPT" in prompts.__all__
        assert "EVALUATOR_VERDICT_SCHEMA" in prompts.__all__

    def test_direct_module_imports_match_init_imports(self):
        """Verify that importing from submodules gives the same objects."""
        from prompts import ORCHESTRATOR_SYSTEM_PROMPT as from_init
        from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT as from_module
        assert from_init is from_module

        from prompts import IMPLEMENTER_SYSTEM_PROMPT as imp_init
        from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT as imp_module
        assert imp_init is imp_module

        from prompts import EVALUATOR_SYSTEM_PROMPT as eval_init
        from prompts.evaluator_prompts import EVALUATOR_SYSTEM_PROMPT as eval_module
        assert eval_init is eval_module


# ---------------------------------------------------------------------------
# AC-008: No hardcoded domain references in prompts (domain-agnostic)
# ---------------------------------------------------------------------------

# Common domain-specific terms that should NOT appear hardcoded in prompts.
DOMAIN_SPECIFIC_TERMS = [
    "python",
    "javascript",
    "typescript",
    "react",
    "django",
    "flask",
    "fastapi",
    "kubernetes",
    "docker",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "java",
    "rust",
    "golang",
    "ruby",
    "rails",
    "spring",
    "angular",
    "vue",
    "svelte",
    "nextjs",
    "next.js",
    "node.js",
    "nodejs",
    "tensorflow",
    "pytorch",
]


class TestDomainAgnostic:
    """AC-008: No hardcoded domain references in prompts."""

    @pytest.fixture
    def all_prompts(self):
        from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
        from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT
        from prompts.evaluator_prompts import EVALUATOR_SYSTEM_PROMPT
        return {
            "orchestrator": ORCHESTRATOR_SYSTEM_PROMPT,
            "implementer": IMPLEMENTER_SYSTEM_PROMPT,
            "evaluator": EVALUATOR_SYSTEM_PROMPT,
        }

    @pytest.mark.parametrize("term", DOMAIN_SPECIFIC_TERMS)
    def test_no_hardcoded_domain_term(self, all_prompts, term):
        """Ensure no domain-specific technology is hardcoded in any prompt."""
        for name, prompt in all_prompts.items():
            # Use word-boundary matching to avoid false positives
            # (e.g. "rust" inside "trust")
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            assert len(matches) == 0, (
                f"Found hardcoded domain term '{term}' in {name} prompt"
            )

    def test_no_specific_language_references(self, all_prompts):
        """High-level check that prompts do not prescribe a specific language."""
        for name, prompt in all_prompts.items():
            lower = prompt.lower()
            # Should not prescribe writing in a specific language
            assert "write in python" not in lower, f"{name} prescribes Python"
            assert "write in java" not in lower, f"{name} prescribes Java"
            assert "write in javascript" not in lower, f"{name} prescribes JavaScript"

    def test_orchestrator_mentions_domain_agnostic(self, all_prompts):
        """Orchestrator prompt should explicitly mention being domain-agnostic."""
        prompt = all_prompts["orchestrator"].lower()
        assert "domain-agnostic" in prompt or "domain agnostic" in prompt


# ---------------------------------------------------------------------------
# Additional quality checks
# ---------------------------------------------------------------------------

class TestPromptQuality:
    """Additional quality checks on all prompts."""

    def test_orchestrator_prompt_not_empty(self):
        from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
        assert len(ORCHESTRATOR_SYSTEM_PROMPT.strip()) > 200

    def test_implementer_prompt_not_empty(self):
        from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT
        assert len(IMPLEMENTER_SYSTEM_PROMPT.strip()) > 200

    def test_evaluator_prompt_not_empty(self):
        from prompts.evaluator_prompts import EVALUATOR_SYSTEM_PROMPT
        assert len(EVALUATOR_SYSTEM_PROMPT.strip()) > 200

    def test_implementer_has_date_placeholder(self):
        from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT
        assert "{date}" in IMPLEMENTER_SYSTEM_PROMPT

    def test_implementer_date_replaceable(self):
        from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT
        rendered = IMPLEMENTER_SYSTEM_PROMPT.format(date="2026-03-30")
        assert "2026-03-30" in rendered

    def test_orchestrator_mentions_implementer(self):
        from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
        assert "Implementer" in ORCHESTRATOR_SYSTEM_PROMPT

    def test_orchestrator_mentions_evaluator(self):
        from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
        assert "Evaluator" in ORCHESTRATOR_SYSTEM_PROMPT

    def test_evaluator_emphasizes_objectivity(self):
        from prompts.evaluator_prompts import EVALUATOR_SYSTEM_PROMPT
        lower = EVALUATOR_SYSTEM_PROMPT.lower()
        assert "objective" in lower

    def test_evaluator_warns_against_self_confirmation_bias(self):
        from prompts.evaluator_prompts import EVALUATOR_SYSTEM_PROMPT
        lower = EVALUATOR_SYSTEM_PROMPT.lower()
        assert "self-confirmation" in lower or "confirmation bias" in lower

    def test_implementer_focuses_on_execution(self):
        from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT
        lower = IMPLEMENTER_SYSTEM_PROMPT.lower()
        assert "execut" in lower  # execute, execution

    def test_implementer_mentions_not_self_evaluate(self):
        from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT
        lower = IMPLEMENTER_SYSTEM_PROMPT.lower()
        assert "not" in lower and "evaluat" in lower
