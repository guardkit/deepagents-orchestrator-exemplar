"""Validation checklist and smoke tests for TASK-OEX-007.

Verifies the entire DeepAgents orchestrator exemplar is complete and functional
by running the smoke test from the spec and checking every acceptance criterion:

- AC-001: All imports in smoke test succeed without errors
- AC-002: Config file loads and contains required model keys
- AC-003: Domain file loads successfully
- AC-004: All tools are importable and are BaseTool instances
- AC-005: All prompts are importable and are non-empty strings
- AC-006: agent.py module-level ``agent`` variable is a CompiledStateGraph
- AC-007: Evaluator subagent has ``tools: []`` (empty list)
- AC-008: Builder async subagent has ``graph_id`` field
- AC-009: File tree matches spec Section 7 (all expected files exist)
- AC-010: No import errors across the entire project
- AC-011: langgraph.json is valid JSON and references ``./agent.py:agent``
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
import yaml
from langchain_core.tools import BaseTool
from langgraph.graph.state import CompiledStateGraph

# Project root is the parent of the tests/ directory.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# AC-001: All imports in smoke test succeed without errors
# ---------------------------------------------------------------------------


class TestSmokeTestImports:
    """AC-001: Every import line in the spec smoke test must succeed."""

    def test_import_create_orchestrator(self) -> None:
        from agents.orchestrator import create_orchestrator

        assert callable(create_orchestrator)

    def test_import_implementer_subagent(self) -> None:
        from agents.implementer import implementer_subagent

        assert callable(implementer_subagent)

    def test_import_evaluator_subagent(self) -> None:
        from agents.evaluator import evaluator_subagent

        assert callable(evaluator_subagent)

    def test_import_builder_async_subagent(self) -> None:
        from agents.builder import builder_async_subagent

        assert callable(builder_async_subagent)

    def test_import_analyse_context(self) -> None:
        from tools.analyse_context import analyse_context

        assert analyse_context is not None

    def test_import_plan_pipeline(self) -> None:
        from tools.plan_pipeline import plan_pipeline

        assert plan_pipeline is not None

    def test_import_execute_command(self) -> None:
        from tools.execute_command import execute_command

        assert execute_command is not None

    def test_import_verify_output(self) -> None:
        from tools.verify_output import verify_output

        assert verify_output is not None

    def test_import_orchestrator_system_prompt(self) -> None:
        from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT

        assert isinstance(ORCHESTRATOR_SYSTEM_PROMPT, str)

    def test_import_implementer_system_prompt(self) -> None:
        from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT

        assert isinstance(IMPLEMENTER_SYSTEM_PROMPT, str)

    def test_import_evaluator_system_prompt(self) -> None:
        from prompts.evaluator_prompts import EVALUATOR_SYSTEM_PROMPT

        assert isinstance(EVALUATOR_SYSTEM_PROMPT, str)


# ---------------------------------------------------------------------------
# AC-002: Config file loads and contains required model keys
# ---------------------------------------------------------------------------


class TestConfigLoading:
    """AC-002: orchestrator-config.yaml loads and has required keys."""

    def test_config_file_exists(self) -> None:
        config_path = _PROJECT_ROOT / "orchestrator-config.yaml"
        assert config_path.exists(), f"orchestrator-config.yaml not found at {config_path}"

    def test_config_is_valid_yaml(self) -> None:
        config_path = _PROJECT_ROOT / "orchestrator-config.yaml"
        config = yaml.safe_load(config_path.read_text())
        assert isinstance(config, dict)

    def test_config_has_reasoning_model(self) -> None:
        config_path = _PROJECT_ROOT / "orchestrator-config.yaml"
        config = yaml.safe_load(config_path.read_text())
        assert config["orchestrator"]["reasoning_model"] is not None

    def test_config_has_implementation_model(self) -> None:
        config_path = _PROJECT_ROOT / "orchestrator-config.yaml"
        config = yaml.safe_load(config_path.read_text())
        assert config["orchestrator"]["implementation_model"] is not None

    def test_models_are_different(self) -> None:
        """Reasoning and implementation models should be different (two-model architecture)."""
        config_path = _PROJECT_ROOT / "orchestrator-config.yaml"
        config = yaml.safe_load(config_path.read_text())
        orch = config["orchestrator"]
        assert orch["reasoning_model"] != orch["implementation_model"], (
            "Reasoning and implementation models should differ for two-model separation"
        )


# ---------------------------------------------------------------------------
# AC-003: Domain file loads successfully
# ---------------------------------------------------------------------------


class TestDomainLoading:
    """AC-003: domains/example-domain/DOMAIN.md loads successfully."""

    def test_domain_file_exists(self) -> None:
        domain_path = _PROJECT_ROOT / "domains" / "example-domain" / "DOMAIN.md"
        assert domain_path.exists(), f"DOMAIN.md not found at {domain_path}"

    def test_domain_file_is_readable(self) -> None:
        domain_path = _PROJECT_ROOT / "domains" / "example-domain" / "DOMAIN.md"
        content = domain_path.read_text(encoding="utf-8")
        assert len(content) > 0, "DOMAIN.md should not be empty"

    def test_domain_file_contains_guidelines(self) -> None:
        domain_path = _PROJECT_ROOT / "domains" / "example-domain" / "DOMAIN.md"
        content = domain_path.read_text(encoding="utf-8")
        assert "domain" in content.lower() or "quality" in content.lower(), (
            "DOMAIN.md should contain domain guidelines"
        )


# ---------------------------------------------------------------------------
# AC-004: All tools are importable and are BaseTool instances
# ---------------------------------------------------------------------------


class TestToolsAreBaseTool:
    """AC-004: All four tools are importable and are BaseTool instances."""

    def test_analyse_context_is_base_tool(self) -> None:
        from tools.orchestrator_tools import analyse_context

        assert isinstance(analyse_context, BaseTool)

    def test_plan_pipeline_is_base_tool(self) -> None:
        from tools.orchestrator_tools import plan_pipeline

        assert isinstance(plan_pipeline, BaseTool)

    def test_execute_command_is_base_tool(self) -> None:
        from tools.orchestrator_tools import execute_command

        assert isinstance(execute_command, BaseTool)

    def test_verify_output_is_base_tool(self) -> None:
        from tools.orchestrator_tools import verify_output

        assert isinstance(verify_output, BaseTool)

    def test_tools_from_shim_modules_are_base_tool(self) -> None:
        """Tools imported via individual shim modules must also be BaseTool."""
        from tools.analyse_context import analyse_context
        from tools.execute_command import execute_command
        from tools.plan_pipeline import plan_pipeline
        from tools.verify_output import verify_output

        for tool_obj in (analyse_context, plan_pipeline, execute_command, verify_output):
            assert isinstance(tool_obj, BaseTool), f"{tool_obj} is not a BaseTool instance"


# ---------------------------------------------------------------------------
# AC-005: All prompts are importable and are non-empty strings
# ---------------------------------------------------------------------------


class TestPromptsAreNonEmpty:
    """AC-005: All three system prompts are importable and non-empty strings."""

    def test_orchestrator_prompt_non_empty(self) -> None:
        from prompts import ORCHESTRATOR_SYSTEM_PROMPT

        assert isinstance(ORCHESTRATOR_SYSTEM_PROMPT, str)
        assert len(ORCHESTRATOR_SYSTEM_PROMPT) > 100

    def test_implementer_prompt_non_empty(self) -> None:
        from prompts import IMPLEMENTER_SYSTEM_PROMPT

        assert isinstance(IMPLEMENTER_SYSTEM_PROMPT, str)
        assert len(IMPLEMENTER_SYSTEM_PROMPT) > 100

    def test_evaluator_prompt_non_empty(self) -> None:
        from prompts import EVALUATOR_SYSTEM_PROMPT

        assert isinstance(EVALUATOR_SYSTEM_PROMPT, str)
        assert len(EVALUATOR_SYSTEM_PROMPT) > 100


# ---------------------------------------------------------------------------
# AC-006: agent.py module-level agent variable is a CompiledStateGraph
# ---------------------------------------------------------------------------


class TestAgentEntrypoint:
    """AC-006: agent.py exports ``agent`` as a CompiledStateGraph."""

    def test_agent_module_has_agent_attr(self) -> None:
        import agent as agent_mod

        assert hasattr(agent_mod, "agent"), "agent.py must export 'agent'"

    def test_agent_is_compiled_state_graph(self) -> None:
        import agent as agent_mod

        assert isinstance(agent_mod.agent, CompiledStateGraph), (
            f"agent.agent must be CompiledStateGraph, got {type(agent_mod.agent)}"
        )


# ---------------------------------------------------------------------------
# AC-007: Evaluator subagent has tools: [] (empty list)
# ---------------------------------------------------------------------------


class TestEvaluatorNoTools:
    """AC-007: Evaluator subagent has an explicitly empty tools list."""

    def test_evaluator_tools_is_empty_list(self) -> None:
        from agents import evaluator_subagent

        ev = evaluator_subagent(model="anthropic:claude-sonnet-4-6")
        assert "tools" in ev, "Evaluator must have a 'tools' key"
        assert ev["tools"] == [], f"Evaluator tools must be [], got {ev['tools']}"
        assert isinstance(ev["tools"], list)


# ---------------------------------------------------------------------------
# AC-008: Builder async subagent has graph_id field
# ---------------------------------------------------------------------------


class TestBuilderGraphId:
    """AC-008: Builder AsyncSubAgent has a ``graph_id`` field."""

    def test_builder_has_graph_id(self) -> None:
        from agents import builder_async_subagent

        ba = builder_async_subagent()
        assert "graph_id" in ba, "Builder must have a 'graph_id' key"
        assert isinstance(ba["graph_id"], str)
        assert len(ba["graph_id"]) > 0


# ---------------------------------------------------------------------------
# AC-009: File tree matches spec Section 7 (all expected files exist)
# ---------------------------------------------------------------------------


class TestFileTree:
    """AC-009: All expected files from the spec file tree exist."""

    EXPECTED_FILES = [
        "agent.py",
        "orchestrator-config.yaml",
        "langgraph.json",
        "pyproject.toml",
        ".env.example",
        ".gitignore",
        "AGENTS.md",
        "README.md",
        "agents/__init__.py",
        "agents/agents.py",
        "agents/orchestrator.py",
        "agents/implementer.py",
        "agents/evaluator.py",
        "agents/builder.py",
        "tools/__init__.py",
        "tools/orchestrator_tools.py",
        "tools/analyse_context.py",
        "tools/plan_pipeline.py",
        "tools/execute_command.py",
        "tools/verify_output.py",
        "prompts/__init__.py",
        "prompts/orchestrator_prompts.py",
        "prompts/implementer_prompts.py",
        "prompts/evaluator_prompts.py",
        "domains/example-domain/DOMAIN.md",
        "skills/example-skill/SKILL.md",
    ]

    @pytest.mark.parametrize("rel_path", EXPECTED_FILES)
    def test_file_exists(self, rel_path: str) -> None:
        full_path = _PROJECT_ROOT / rel_path
        assert full_path.exists(), f"Expected file missing: {rel_path}"


# ---------------------------------------------------------------------------
# AC-010: No import errors across the entire project
# ---------------------------------------------------------------------------


class TestNoImportErrors:
    """AC-010: All project modules import without errors."""

    ALL_MODULES = [
        "agent",
        "agents",
        "agents.agents",
        "agents.orchestrator",
        "agents.implementer",
        "agents.evaluator",
        "agents.builder",
        "tools",
        "tools.orchestrator_tools",
        "tools.analyse_context",
        "tools.plan_pipeline",
        "tools.execute_command",
        "tools.verify_output",
        "prompts",
        "prompts.orchestrator_prompts",
        "prompts.implementer_prompts",
        "prompts.evaluator_prompts",
    ]

    @pytest.mark.parametrize("module_name", ALL_MODULES)
    def test_module_importable(self, module_name: str) -> None:
        mod = importlib.import_module(module_name)
        assert mod is not None


# ---------------------------------------------------------------------------
# AC-011: langgraph.json is valid JSON and references ./agent.py:agent
# ---------------------------------------------------------------------------


class TestLanggraphJson:
    """AC-011: langgraph.json is valid JSON referencing ./agent.py:agent."""

    def test_langgraph_json_exists(self) -> None:
        lg_path = _PROJECT_ROOT / "langgraph.json"
        assert lg_path.exists()

    def test_langgraph_json_is_valid_json(self) -> None:
        lg_path = _PROJECT_ROOT / "langgraph.json"
        data = json.loads(lg_path.read_text())
        assert isinstance(data, dict)

    def test_langgraph_references_agent(self) -> None:
        lg_path = _PROJECT_ROOT / "langgraph.json"
        data = json.loads(lg_path.read_text())
        assert data.get("graphs", {}).get("orchestrator") == "./agent.py:agent"


# ---------------------------------------------------------------------------
# Integration: full smoke test from spec Section 6
# ---------------------------------------------------------------------------


class TestFullSmokeTest:
    """Integration: runs the complete smoke test from the specification."""

    def test_full_smoke_test(self) -> None:
        """Execute all smoke test steps from spec Section 6 in sequence."""
        from agents.builder import builder_async_subagent
        from agents.evaluator import evaluator_subagent
        from agents.implementer import implementer_subagent
        from agents.orchestrator import create_orchestrator
        from prompts.evaluator_prompts import EVALUATOR_SYSTEM_PROMPT
        from prompts.implementer_prompts import IMPLEMENTER_SYSTEM_PROMPT
        from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT
        from tools.analyse_context import analyse_context
        from tools.execute_command import execute_command
        from tools.plan_pipeline import plan_pipeline
        from tools.verify_output import verify_output

        # All imports succeeded if we reach here.
        config = yaml.safe_load((_PROJECT_ROOT / "orchestrator-config.yaml").read_text())
        domain = (_PROJECT_ROOT / "domains" / "example-domain" / "DOMAIN.md").read_text()

        assert config["orchestrator"]["reasoning_model"] is not None
        assert config["orchestrator"]["implementation_model"] is not None
        assert len(domain) > 0

    def test_subagent_fields_complete(self) -> None:
        """SubAgent specs have all required fields (name, description, system_prompt, model, tools)."""
        from agents import evaluator_subagent, implementer_subagent

        required_fields = {"name", "description", "system_prompt", "model", "tools"}

        impl = implementer_subagent(model="anthropic:claude-haiku-4-5")
        for field in required_fields:
            assert field in impl, f"Implementer missing field: {field}"

        ev = evaluator_subagent(model="anthropic:claude-sonnet-4-6")
        for field in required_fields:
            assert field in ev, f"Evaluator missing field: {field}"

    def test_async_subagent_fields_complete(self) -> None:
        """AsyncSubAgent spec has required fields (name, description, graph_id)."""
        from agents import builder_async_subagent

        required_fields = {"name", "description", "graph_id"}
        ba = builder_async_subagent()
        for field in required_fields:
            assert field in ba, f"Builder missing field: {field}"
