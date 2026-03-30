"""Tests for domains/example-domain/DOMAIN.md structure and content.

Validates acceptance criterion:
- AC-010: domains/example-domain/DOMAIN.md contains example domain-specific
  guidelines and evaluation criteria.
"""

import os

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN_MD_PATH = os.path.join(BASE_DIR, "domains", "example-domain", "DOMAIN.md")


@pytest.fixture
def domain_content():
    """Load and return the DOMAIN.md content."""
    assert os.path.isfile(DOMAIN_MD_PATH), (
        f"DOMAIN.md not found at {DOMAIN_MD_PATH}"
    )
    with open(DOMAIN_MD_PATH, "r") as f:
        return f.read()


class TestDomainMdExists:
    """AC-010: DOMAIN.md exists at the correct path."""

    def test_domain_directory_exists(self):
        domain_dir = os.path.join(BASE_DIR, "domains", "example-domain")
        assert os.path.isdir(domain_dir), (
            f"Expected domains/example-domain/ directory at {domain_dir}"
        )

    def test_domain_md_file_exists(self):
        assert os.path.isfile(DOMAIN_MD_PATH), (
            f"Expected DOMAIN.md at {DOMAIN_MD_PATH}"
        )

    def test_domain_md_not_empty(self, domain_content):
        assert len(domain_content.strip()) > 0, "DOMAIN.md must not be empty"


class TestDomainGuidelines:
    """AC-010: DOMAIN.md contains domain-specific guidelines."""

    def test_has_title(self, domain_content):
        assert domain_content.startswith("# Domain:"), (
            "DOMAIN.md must start with a '# Domain:' title"
        )

    def test_has_overview_section(self, domain_content):
        assert "## Overview" in domain_content, (
            "DOMAIN.md must have an Overview section"
        )

    def test_has_guidelines_section(self, domain_content):
        assert "## Domain Guidelines" in domain_content or "## Guidelines" in domain_content, (
            "DOMAIN.md must have a Guidelines section"
        )

    def test_has_code_quality_guidelines(self, domain_content):
        assert "Code Quality" in domain_content, (
            "DOMAIN.md must include code quality guidelines"
        )

    def test_has_naming_conventions(self, domain_content):
        assert "Naming Convention" in domain_content or "Naming" in domain_content, (
            "DOMAIN.md must include naming conventions"
        )

    def test_has_error_handling_guidelines(self, domain_content):
        assert "Error Handling" in domain_content, (
            "DOMAIN.md must include error handling guidelines"
        )


class TestDomainEvaluationCriteria:
    """AC-010: DOMAIN.md contains evaluation criteria."""

    def test_has_evaluation_criteria_section(self, domain_content):
        assert "## Evaluation Criteria" in domain_content, (
            "DOMAIN.md must have an Evaluation Criteria section"
        )

    def test_has_functional_criteria(self, domain_content):
        assert "Correctness" in domain_content, (
            "Evaluation criteria must include correctness checking"
        )

    def test_has_completeness_criteria(self, domain_content):
        assert "Completeness" in domain_content, (
            "Evaluation criteria must include completeness checking"
        )

    def test_has_structural_criteria(self, domain_content):
        assert "Test Coverage" in domain_content or "Testing" in domain_content, (
            "Evaluation criteria must include test coverage"
        )

    def test_has_documentation_criteria(self, domain_content):
        assert "Documentation" in domain_content, (
            "Evaluation criteria must include documentation requirements"
        )
