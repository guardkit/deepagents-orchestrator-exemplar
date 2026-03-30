"""Tests for agent definitions (TASK-OEX-005).

Verifies all four agent roles: orchestrator, implementer, evaluator, and builder.
Tests cover factory functions, TypedDict structure, field correctness, and exports.
"""

from __future__ import annotations

from langchain_core.tools import BaseTool

# ---------------------------------------------------------------------------
# AC-001: agents/orchestrator.py exports create_orchestrator
# ---------------------------------------------------------------------------


class TestCreateOrchestratorExport:
    """AC-001: create_orchestrator is importable and has correct signature."""

    def test_create_orchestrator_importable(self) -> None:
        from agents import create_orchestrator

        assert callable(create_orchestrator)

    def test_create_orchestrator_signature(self) -> None:
        """create_orchestrator accepts reasoning_model, implementation_model, domain_prompt."""
        import inspect

        from agents import create_orchestrator

        sig = inspect.signature(create_orchestrator)
        params = list(sig.parameters.keys())
        assert "reasoning_model" in params
        assert "implementation_model" in params
        assert "domain_prompt" in params

    def test_create_orchestrator_params_are_str(self) -> None:
        """All three parameters should be annotated as str."""
        import inspect

        from agents import create_orchestrator

        sig = inspect.signature(create_orchestrator)
        for name in ("reasoning_model", "implementation_model", "domain_prompt"):
            assert sig.parameters[name].annotation is str or sig.parameters[name].annotation == "str"


# ---------------------------------------------------------------------------
# AC-002: create_orchestrator uses create_deep_agent with correct arguments
# ---------------------------------------------------------------------------


class TestCreateOrchestratorCallsDeepAgent:
    """AC-002: create_orchestrator uses create_deep_agent() with the right kwargs."""

    def test_returns_compiled_state_graph(self) -> None:
        """create_orchestrator returns a CompiledStateGraph from create_deep_agent."""
        from unittest.mock import MagicMock, patch

        from agents import create_orchestrator

        mock_graph = MagicMock()
        with patch("agents.agents.create_deep_agent", return_value=mock_graph) as mock_cda:
            result = create_orchestrator(
                reasoning_model="anthropic:claude-sonnet-4-6",
                implementation_model="anthropic:claude-haiku-4-5",
                domain_prompt="Test domain",
            )
            mock_cda.assert_called_once()
            assert result is mock_graph

    def test_passes_model_as_reasoning_model(self) -> None:
        """The model param passed to create_deep_agent should be the reasoning_model."""
        from unittest.mock import MagicMock, patch

        from agents import create_orchestrator

        with patch("agents.agents.create_deep_agent", return_value=MagicMock()) as mock_cda:
            create_orchestrator(
                reasoning_model="anthropic:claude-sonnet-4-6",
                implementation_model="anthropic:claude-haiku-4-5",
                domain_prompt="Test domain",
            )
            call_kwargs = mock_cda.call_args
            assert (
                call_kwargs.kwargs.get("model") == "anthropic:claude-sonnet-4-6"
                or call_kwargs[1].get("model") == "anthropic:claude-sonnet-4-6"
            )

    def test_passes_tools(self) -> None:
        """create_orchestrator passes tools to create_deep_agent."""
        from unittest.mock import MagicMock, patch

        from agents import create_orchestrator

        with patch("agents.agents.create_deep_agent", return_value=MagicMock()) as mock_cda:
            create_orchestrator(
                reasoning_model="anthropic:claude-sonnet-4-6",
                implementation_model="anthropic:claude-haiku-4-5",
                domain_prompt="Test domain",
            )
            call_kwargs = mock_cda.call_args[1] if mock_cda.call_args[1] else {}
            # Should have tools
            assert "tools" in call_kwargs
            tools = call_kwargs["tools"]
            assert isinstance(tools, (list, tuple))
            assert len(tools) == 4
            for t in tools:
                assert isinstance(t, BaseTool)

    def test_passes_system_prompt(self) -> None:
        """create_orchestrator passes system_prompt to create_deep_agent."""
        from unittest.mock import MagicMock, patch

        from agents import create_orchestrator

        with patch("agents.agents.create_deep_agent", return_value=MagicMock()) as mock_cda:
            create_orchestrator(
                reasoning_model="anthropic:claude-sonnet-4-6",
                implementation_model="anthropic:claude-haiku-4-5",
                domain_prompt="My custom domain",
            )
            call_kwargs = mock_cda.call_args[1]
            assert "system_prompt" in call_kwargs
            prompt = call_kwargs["system_prompt"]
            assert isinstance(prompt, str)
            assert len(prompt) > 50

    def test_passes_subagents_list_of_3(self) -> None:
        """create_orchestrator passes 3 subagents: implementer, evaluator, builder."""
        from unittest.mock import MagicMock, patch

        from agents import create_orchestrator

        with patch("agents.agents.create_deep_agent", return_value=MagicMock()) as mock_cda:
            create_orchestrator(
                reasoning_model="anthropic:claude-sonnet-4-6",
                implementation_model="anthropic:claude-haiku-4-5",
                domain_prompt="Test domain",
            )
            call_kwargs = mock_cda.call_args[1]
            assert "subagents" in call_kwargs
            subagents = call_kwargs["subagents"]
            assert isinstance(subagents, (list, tuple))
            assert len(subagents) == 3

    def test_passes_domain_prompt_into_system_prompt(self) -> None:
        """domain_prompt should be injected into the orchestrator system prompt."""
        from unittest.mock import MagicMock, patch

        from agents import create_orchestrator

        with patch("agents.agents.create_deep_agent", return_value=MagicMock()) as mock_cda:
            create_orchestrator(
                reasoning_model="anthropic:claude-sonnet-4-6",
                implementation_model="anthropic:claude-haiku-4-5",
                domain_prompt="UNIQUE_DOMAIN_MARKER_XYZ",
            )
            call_kwargs = mock_cda.call_args[1]
            prompt = call_kwargs["system_prompt"]
            assert "UNIQUE_DOMAIN_MARKER_XYZ" in prompt


# ---------------------------------------------------------------------------
# AC-003: agents/implementer.py exports implementer_subagent function
# ---------------------------------------------------------------------------


class TestImplementerSubagent:
    """AC-003 & AC-004: implementer_subagent factory returns correct SubAgent dict."""

    def test_implementer_subagent_importable(self) -> None:
        from agents import implementer_subagent

        assert callable(implementer_subagent)

    def test_accepts_model_param(self) -> None:
        """implementer_subagent accepts a model: str parameter."""
        import inspect

        from agents import implementer_subagent

        sig = inspect.signature(implementer_subagent)
        assert "model" in sig.parameters

    def test_returns_dict(self) -> None:
        from agents import implementer_subagent

        result = implementer_subagent(model="anthropic:claude-haiku-4-5")
        assert isinstance(result, dict)

    def test_has_name_field(self) -> None:
        from agents import implementer_subagent

        result = implementer_subagent(model="anthropic:claude-haiku-4-5")
        assert "name" in result
        assert isinstance(result["name"], str)
        assert len(result["name"]) > 0

    def test_has_description_field(self) -> None:
        from agents import implementer_subagent

        result = implementer_subagent(model="anthropic:claude-haiku-4-5")
        assert "description" in result
        assert isinstance(result["description"], str)
        assert len(result["description"]) > 10

    def test_has_system_prompt_field(self) -> None:
        from agents import implementer_subagent

        result = implementer_subagent(model="anthropic:claude-haiku-4-5")
        assert "system_prompt" in result
        assert isinstance(result["system_prompt"], str)
        assert len(result["system_prompt"]) > 50

    def test_has_model_field_matching_param(self) -> None:
        from agents import implementer_subagent

        result = implementer_subagent(model="anthropic:claude-haiku-4-5")
        assert "model" in result
        assert result["model"] == "anthropic:claude-haiku-4-5"

    def test_has_tools_with_4_tools(self) -> None:
        """AC-004: Implementer SubAgent has the 4 tools from TASK-OEX-002."""
        from agents import implementer_subagent

        result = implementer_subagent(model="anthropic:claude-haiku-4-5")
        assert "tools" in result
        tools = result["tools"]
        assert isinstance(tools, list)
        assert len(tools) == 4
        for t in tools:
            assert isinstance(t, BaseTool)

    def test_tools_are_correct_tools(self) -> None:
        """The 4 tools should be the orchestrator tools."""
        from agents import implementer_subagent

        result = implementer_subagent(model="anthropic:claude-haiku-4-5")
        tool_names = {t.name for t in result["tools"]}
        assert "analyse_context" in tool_names
        assert "plan_pipeline" in tool_names
        assert "execute_command" in tool_names
        assert "verify_output" in tool_names

    def test_model_param_propagates(self) -> None:
        """Different model string should be reflected in the result."""
        from agents import implementer_subagent

        result = implementer_subagent(model="google:gemini-pro")
        assert result["model"] == "google:gemini-pro"


# ---------------------------------------------------------------------------
# AC-005 & AC-006: agents/evaluator.py exports evaluator_subagent function
# ---------------------------------------------------------------------------


class TestEvaluatorSubagent:
    """AC-005 & AC-006: evaluator_subagent factory returns correct SubAgent dict."""

    def test_evaluator_subagent_importable(self) -> None:
        from agents import evaluator_subagent

        assert callable(evaluator_subagent)

    def test_accepts_model_param(self) -> None:
        import inspect

        from agents import evaluator_subagent

        sig = inspect.signature(evaluator_subagent)
        assert "model" in sig.parameters

    def test_returns_dict(self) -> None:
        from agents import evaluator_subagent

        result = evaluator_subagent(model="anthropic:claude-sonnet-4-6")
        assert isinstance(result, dict)

    def test_has_name_field(self) -> None:
        from agents import evaluator_subagent

        result = evaluator_subagent(model="anthropic:claude-sonnet-4-6")
        assert "name" in result
        assert isinstance(result["name"], str)
        assert len(result["name"]) > 0

    def test_has_description_field(self) -> None:
        from agents import evaluator_subagent

        result = evaluator_subagent(model="anthropic:claude-sonnet-4-6")
        assert "description" in result
        assert isinstance(result["description"], str)
        assert len(result["description"]) > 10

    def test_has_system_prompt_field(self) -> None:
        from agents import evaluator_subagent

        result = evaluator_subagent(model="anthropic:claude-sonnet-4-6")
        assert "system_prompt" in result
        assert isinstance(result["system_prompt"], str)
        assert len(result["system_prompt"]) > 50

    def test_has_model_field_matching_param(self) -> None:
        from agents import evaluator_subagent

        result = evaluator_subagent(model="anthropic:claude-sonnet-4-6")
        assert "model" in result
        assert result["model"] == "anthropic:claude-sonnet-4-6"

    def test_has_tools_explicit_empty_list(self) -> None:
        """AC-006: Evaluator MUST have tools=[] — explicit empty list."""
        from agents import evaluator_subagent

        result = evaluator_subagent(model="anthropic:claude-sonnet-4-6")
        assert "tools" in result
        assert result["tools"] == []
        assert isinstance(result["tools"], list)

    def test_model_param_propagates(self) -> None:
        from agents import evaluator_subagent

        result = evaluator_subagent(model="google:gemini-flash")
        assert result["model"] == "google:gemini-flash"


# ---------------------------------------------------------------------------
# AC-007: agents/builder.py exports builder_async_subagent
# ---------------------------------------------------------------------------


class TestBuilderAsyncSubagent:
    """AC-007: builder_async_subagent is an AsyncSubAgent dict."""

    def test_builder_async_subagent_importable(self) -> None:
        from agents import builder_async_subagent

        assert callable(builder_async_subagent)

    def test_returns_dict(self) -> None:
        from agents import builder_async_subagent

        result = builder_async_subagent()
        assert isinstance(result, dict)

    def test_has_name_field(self) -> None:
        from agents import builder_async_subagent

        result = builder_async_subagent()
        assert "name" in result
        assert isinstance(result["name"], str)
        assert len(result["name"]) > 0

    def test_has_description_field(self) -> None:
        from agents import builder_async_subagent

        result = builder_async_subagent()
        assert "description" in result
        assert isinstance(result["description"], str)
        assert len(result["description"]) > 10

    def test_has_graph_id_field(self) -> None:
        from agents import builder_async_subagent

        result = builder_async_subagent()
        assert "graph_id" in result
        assert isinstance(result["graph_id"], str)
        assert len(result["graph_id"]) > 0

    def test_url_configurable(self) -> None:
        """url should be configurable via parameter."""
        from agents import builder_async_subagent

        result = builder_async_subagent(url="http://custom:8080")
        assert result.get("url") == "http://custom:8080"

    def test_default_url(self) -> None:
        """builder_async_subagent should have a sensible default or no url."""
        from agents import builder_async_subagent

        result = builder_async_subagent()
        # url is optional in AsyncSubAgent; if present, should be a string
        if "url" in result:
            assert isinstance(result["url"], str)


# ---------------------------------------------------------------------------
# AC-008: agents/__init__.py exports all agent factories/specs
# ---------------------------------------------------------------------------


class TestAgentsPackageExports:
    """AC-008: All agent factories are exported from agents package."""

    def test_exports_create_orchestrator(self) -> None:
        from agents import create_orchestrator

        assert callable(create_orchestrator)

    def test_exports_implementer_subagent(self) -> None:
        from agents import implementer_subagent

        assert callable(implementer_subagent)

    def test_exports_evaluator_subagent(self) -> None:
        from agents import evaluator_subagent

        assert callable(evaluator_subagent)

    def test_exports_builder_async_subagent(self) -> None:
        from agents import builder_async_subagent

        assert callable(builder_async_subagent)

    def test_all_in_dunder_all(self) -> None:
        """__all__ should list all four exports."""
        import agents

        assert hasattr(agents, "__all__")
        all_exports = agents.__all__
        assert "create_orchestrator" in all_exports
        assert "implementer_subagent" in all_exports
        assert "evaluator_subagent" in all_exports
        assert "builder_async_subagent" in all_exports


# ---------------------------------------------------------------------------
# AC-009: Lint/format checks (tested implicitly by ruff in CI)
# ---------------------------------------------------------------------------


class TestCodeQuality:
    """AC-009: Files pass lint/format. We verify structural quality here."""

    def test_agents_module_has_docstring(self) -> None:
        import agents.agents

        assert agents.agents.__doc__ is not None
        assert len(agents.agents.__doc__) > 10

    def test_create_orchestrator_has_docstring(self) -> None:
        from agents import create_orchestrator

        assert create_orchestrator.__doc__ is not None
        assert len(create_orchestrator.__doc__) > 10

    def test_implementer_subagent_has_docstring(self) -> None:
        from agents import implementer_subagent

        assert implementer_subagent.__doc__ is not None
        assert len(implementer_subagent.__doc__) > 10

    def test_evaluator_subagent_has_docstring(self) -> None:
        from agents import evaluator_subagent

        assert evaluator_subagent.__doc__ is not None
        assert len(evaluator_subagent.__doc__) > 10

    def test_builder_async_subagent_has_docstring(self) -> None:
        from agents import builder_async_subagent

        assert builder_async_subagent.__doc__ is not None
        assert len(builder_async_subagent.__doc__) > 10


# ---------------------------------------------------------------------------
# Integration: subagent names are unique
# ---------------------------------------------------------------------------


class TestSubagentNamesUnique:
    """All subagent names must be unique for the orchestrator to disambiguate."""

    def test_all_names_unique(self) -> None:
        from agents import builder_async_subagent, evaluator_subagent, implementer_subagent

        impl = implementer_subagent(model="anthropic:claude-haiku-4-5")
        evalu = evaluator_subagent(model="anthropic:claude-sonnet-4-6")
        build = builder_async_subagent()
        names = [impl["name"], evalu["name"], build["name"]]
        assert len(names) == len(set(names)), f"Duplicate subagent names: {names}"
