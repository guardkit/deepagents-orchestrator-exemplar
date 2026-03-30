"""Tests for skills/example-skill/SKILL.md structure and content.

Validates acceptance criterion:
- AC-011: skills/example-skill/SKILL.md contains example skill documentation
  with YAML frontmatter.
"""

import os
import re

import pytest
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD_PATH = os.path.join(BASE_DIR, "skills", "example-skill", "SKILL.md")


@pytest.fixture
def skill_content():
    """Load and return the full SKILL.md content."""
    assert os.path.isfile(SKILL_MD_PATH), (
        f"SKILL.md not found at {SKILL_MD_PATH}"
    )
    with open(SKILL_MD_PATH, "r") as f:
        return f.read()


@pytest.fixture
def skill_frontmatter(skill_content):
    """Extract and parse the YAML frontmatter from SKILL.md."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", skill_content, re.DOTALL)
    assert match is not None, "SKILL.md must start with YAML frontmatter (---)"
    frontmatter_text = match.group(1)
    data = yaml.safe_load(frontmatter_text)
    assert isinstance(data, dict), "Frontmatter must parse to a YAML mapping"
    return data


@pytest.fixture
def skill_body(skill_content):
    """Extract the markdown body after the frontmatter."""
    match = re.match(r"^---\s*\n.*?\n---\s*\n(.*)", skill_content, re.DOTALL)
    assert match is not None, "SKILL.md must have content after frontmatter"
    return match.group(1)


class TestSkillMdExists:
    """AC-011: SKILL.md exists at the correct path."""

    def test_skill_directory_exists(self):
        skill_dir = os.path.join(BASE_DIR, "skills", "example-skill")
        assert os.path.isdir(skill_dir), (
            f"Expected skills/example-skill/ directory at {skill_dir}"
        )

    def test_skill_md_file_exists(self):
        assert os.path.isfile(SKILL_MD_PATH), (
            f"Expected SKILL.md at {SKILL_MD_PATH}"
        )

    def test_skill_md_not_empty(self, skill_content):
        assert len(skill_content.strip()) > 0, "SKILL.md must not be empty"


class TestSkillFrontmatter:
    """AC-011: SKILL.md has valid YAML frontmatter."""

    def test_has_yaml_frontmatter(self, skill_content):
        assert skill_content.startswith("---"), (
            "SKILL.md must start with YAML frontmatter delimiter '---'"
        )

    def test_frontmatter_has_closing_delimiter(self, skill_content):
        # Find the second occurrence of ---
        first_end = skill_content.index("---") + 3
        remaining = skill_content[first_end:]
        assert "---" in remaining, (
            "SKILL.md frontmatter must have a closing '---' delimiter"
        )

    def test_frontmatter_has_name(self, skill_frontmatter):
        assert "name" in skill_frontmatter, (
            "Frontmatter must include 'name' field"
        )
        assert isinstance(skill_frontmatter["name"], str), (
            "Frontmatter 'name' must be a string"
        )

    def test_frontmatter_has_version(self, skill_frontmatter):
        assert "version" in skill_frontmatter, (
            "Frontmatter must include 'version' field"
        )
        assert isinstance(skill_frontmatter["version"], str), (
            "Frontmatter 'version' must be a string"
        )

    def test_frontmatter_has_description(self, skill_frontmatter):
        assert "description" in skill_frontmatter, (
            "Frontmatter must include 'description' field"
        )
        assert isinstance(skill_frontmatter["description"], str), (
            "Frontmatter 'description' must be a string"
        )

    def test_frontmatter_has_tags(self, skill_frontmatter):
        assert "tags" in skill_frontmatter, (
            "Frontmatter must include 'tags' field"
        )
        assert isinstance(skill_frontmatter["tags"], list), (
            "Frontmatter 'tags' must be a list"
        )
        assert len(skill_frontmatter["tags"]) > 0, (
            "Frontmatter 'tags' must not be empty"
        )

    def test_frontmatter_has_inputs(self, skill_frontmatter):
        assert "inputs" in skill_frontmatter, (
            "Frontmatter must include 'inputs' field"
        )
        assert isinstance(skill_frontmatter["inputs"], list), (
            "Frontmatter 'inputs' must be a list"
        )

    def test_frontmatter_has_outputs(self, skill_frontmatter):
        assert "outputs" in skill_frontmatter, (
            "Frontmatter must include 'outputs' field"
        )
        assert isinstance(skill_frontmatter["outputs"], list), (
            "Frontmatter 'outputs' must be a list"
        )

    def test_input_fields_have_required_attributes(self, skill_frontmatter):
        """Each input should have name, type, and description."""
        for inp in skill_frontmatter["inputs"]:
            assert "name" in inp, f"Input must have 'name': {inp}"
            assert "type" in inp, f"Input must have 'type': {inp}"
            assert "description" in inp, f"Input must have 'description': {inp}"

    def test_output_fields_have_required_attributes(self, skill_frontmatter):
        """Each output should have name, type, and description."""
        for out in skill_frontmatter["outputs"]:
            assert "name" in out, f"Output must have 'name': {out}"
            assert "type" in out, f"Output must have 'type': {out}"
            assert "description" in out, f"Output must have 'description': {out}"


class TestSkillBody:
    """AC-011: SKILL.md has meaningful skill documentation."""

    def test_body_has_title(self, skill_body):
        assert "# Skill:" in skill_body, (
            "SKILL.md body must have a '# Skill:' title"
        )

    def test_body_has_purpose_section(self, skill_body):
        assert "## Purpose" in skill_body, (
            "SKILL.md body must have a Purpose section"
        )

    def test_body_has_description_section(self, skill_body):
        assert "## Description" in skill_body, (
            "SKILL.md body must have a Description section"
        )

    def test_body_has_usage_section(self, skill_body):
        assert "## Usage" in skill_body, (
            "SKILL.md body must have a Usage section"
        )

    def test_body_has_examples(self, skill_body):
        assert "## Examples" in skill_body or "### Example" in skill_body, (
            "SKILL.md body must include examples"
        )
