"""Tests for AGENTS.md structure and content.

Validates that the AGENTS.md file meets all acceptance criteria:
- AC-006: AGENTS.md defines ALWAYS/NEVER/ASK boundaries for Orchestrator, Implementer, Evaluator
- AC-007: Orchestrator boundaries
- AC-008: Implementer boundaries
- AC-009: Evaluator boundaries
"""

import os
import re

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_MD_PATH = os.path.join(BASE_DIR, "AGENTS.md")


@pytest.fixture
def agents_content():
    """Load and return the AGENTS.md content."""
    assert os.path.isfile(AGENTS_MD_PATH), (
        f"AGENTS.md not found at {AGENTS_MD_PATH}"
    )
    with open(AGENTS_MD_PATH, "r") as f:
        return f.read()


def extract_section(content: str, heading: str) -> str:
    """Extract the content under a given heading (## level) until the next ## heading."""
    pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def extract_subsection(content: str, heading: str) -> str:
    """Extract content under a ### heading until the next ### or ## heading."""
    pattern = rf"^### {re.escape(heading)}\s*\n(.*?)(?=^###? |\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


class TestAgentsMdExists:
    """AC-006: AGENTS.md exists and defines boundaries for all three roles."""

    def test_agents_md_exists(self):
        assert os.path.isfile(AGENTS_MD_PATH), (
            f"Expected AGENTS.md at {AGENTS_MD_PATH}"
        )

    def test_agents_md_not_empty(self, agents_content):
        assert len(agents_content.strip()) > 0, "AGENTS.md must not be empty"

    def test_defines_orchestrator_section(self, agents_content):
        assert "## Orchestrator" in agents_content, (
            "AGENTS.md must define an Orchestrator section"
        )

    def test_defines_implementer_section(self, agents_content):
        assert "## Implementer" in agents_content, (
            "AGENTS.md must define an Implementer section"
        )

    def test_defines_evaluator_section(self, agents_content):
        assert "## Evaluator" in agents_content, (
            "AGENTS.md must define an Evaluator section"
        )

    def test_all_roles_have_always_never_ask(self, agents_content):
        for role in ("Orchestrator", "Implementer", "Evaluator"):
            section = extract_section(agents_content, role)
            assert "### ALWAYS" in section, (
                f"{role} section must have ### ALWAYS subsection"
            )
            assert "### NEVER" in section, (
                f"{role} section must have ### NEVER subsection"
            )
            assert "### ASK" in section, (
                f"{role} section must have ### ASK subsection"
            )


class TestOrchestratorBoundaries:
    """AC-007: Orchestrator ALWAYS/NEVER/ASK rules."""

    def test_orchestrator_always_reason_before_acting(self, agents_content):
        section = extract_section(agents_content, "Orchestrator")
        always = extract_subsection(section, "ALWAYS")
        assert re.search(r"[Rr]eason\s+before\s+acting", always), (
            "Orchestrator ALWAYS must include 'reason before acting'"
        )

    def test_orchestrator_never_implement_directly(self, agents_content):
        section = extract_section(agents_content, "Orchestrator")
        never = extract_subsection(section, "NEVER")
        assert re.search(r"[Ii]mplement\s+directly", never), (
            "Orchestrator NEVER must include 'implement directly'"
        )

    def test_orchestrator_ask_when_plan_ambiguous(self, agents_content):
        section = extract_section(agents_content, "Orchestrator")
        ask = extract_subsection(section, "ASK")
        assert re.search(r"plan\s+is\s+ambiguous", ask), (
            "Orchestrator ASK must include 'when plan is ambiguous'"
        )


class TestImplementerBoundaries:
    """AC-008: Implementer ALWAYS/NEVER/ASK rules."""

    def test_implementer_always_follow_the_plan(self, agents_content):
        section = extract_section(agents_content, "Implementer")
        always = extract_subsection(section, "ALWAYS")
        assert re.search(r"[Ff]ollow\s+the\s+plan", always), (
            "Implementer ALWAYS must include 'follow the plan'"
        )

    def test_implementer_never_evaluate_own_work(self, agents_content):
        section = extract_section(agents_content, "Implementer")
        never = extract_subsection(section, "NEVER")
        assert re.search(r"[Ee]valuate\s+own\s+work", never), (
            "Implementer NEVER must include 'evaluate own work'"
        )

    def test_implementer_ask_when_instructions_unclear(self, agents_content):
        section = extract_section(agents_content, "Implementer")
        ask = extract_subsection(section, "ASK")
        assert re.search(r"instructions\s+are\s+unclear", ask), (
            "Implementer ASK must include 'when instructions unclear'"
        )


class TestEvaluatorBoundaries:
    """AC-009: Evaluator ALWAYS/NEVER/ASK rules."""

    def test_evaluator_always_structured_verdict(self, agents_content):
        section = extract_section(agents_content, "Evaluator")
        always = extract_subsection(section, "ALWAYS")
        assert re.search(r"structured\s+verdict\s+schema", always), (
            "Evaluator ALWAYS must include 'structured verdict schema'"
        )

    def test_evaluator_never_have_tools(self, agents_content):
        section = extract_section(agents_content, "Evaluator")
        never = extract_subsection(section, "NEVER")
        assert re.search(r"[Hh]ave\s+tools", never), (
            "Evaluator NEVER must include 'have tools'"
        )

    def test_evaluator_ask_when_criteria_ambiguous(self, agents_content):
        section = extract_section(agents_content, "Evaluator")
        ask = extract_subsection(section, "ASK")
        assert re.search(r"criteria\s+are\s+ambiguous", ask), (
            "Evaluator ASK must include 'when criteria ambiguous'"
        )

    def test_evaluator_verdict_schema_includes_required_fields(self, agents_content):
        """Verify the verdict schema JSON in the Evaluator section includes all required fields."""
        section = extract_section(agents_content, "Evaluator")
        for field in ("verdict", "criterion_id", "evidence", "suggestions"):
            assert f'"{field}"' in section, (
                f"Evaluator verdict schema must include '{field}' field"
            )
