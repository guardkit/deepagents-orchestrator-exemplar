"""Tests for orchestrator tools.

Verifies all four tools: analyse_context, plan_pipeline, execute_command, verify_output.
Tests cover: decorator usage, return types, error handling, docstrings, and __init__ exports.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from langchain_core.tools import BaseTool

# ---------------------------------------------------------------------------
# Import tests — verify tools/__init__.py exports all four tools
# ---------------------------------------------------------------------------


class TestToolExports:
    """Verify tools package exports all four tools correctly."""

    def test_analyse_context_importable(self) -> None:
        from tools import analyse_context

        assert analyse_context is not None

    def test_plan_pipeline_importable(self) -> None:
        from tools import plan_pipeline

        assert plan_pipeline is not None

    def test_execute_command_importable(self) -> None:
        from tools import execute_command

        assert execute_command is not None

    def test_verify_output_importable(self) -> None:
        from tools import verify_output

        assert verify_output is not None


# ---------------------------------------------------------------------------
# Decorator tests — all tools must be @tool decorated (BaseTool instances)
# ---------------------------------------------------------------------------


class TestToolDecorators:
    """Verify all tools use @tool(parse_docstring=True) decorator."""

    def test_analyse_context_is_tool(self) -> None:
        from tools import analyse_context

        assert isinstance(analyse_context, BaseTool)

    def test_plan_pipeline_is_tool(self) -> None:
        from tools import plan_pipeline

        assert isinstance(plan_pipeline, BaseTool)

    def test_execute_command_is_tool(self) -> None:
        from tools import execute_command

        assert isinstance(execute_command, BaseTool)

    def test_verify_output_is_tool(self) -> None:
        from tools import verify_output

        assert isinstance(verify_output, BaseTool)


# ---------------------------------------------------------------------------
# Docstring tests — parse_docstring=True requires Args section
# ---------------------------------------------------------------------------


class TestToolDocstrings:
    """Verify all tools have proper docstrings with Args section."""

    def test_analyse_context_has_description(self) -> None:
        from tools import analyse_context

        assert analyse_context.description
        assert len(analyse_context.description) > 10

    def test_plan_pipeline_has_description(self) -> None:
        from tools import plan_pipeline

        assert plan_pipeline.description
        assert len(plan_pipeline.description) > 10

    def test_execute_command_has_description(self) -> None:
        from tools import execute_command

        assert execute_command.description
        assert len(execute_command.description) > 10

    def test_verify_output_has_description(self) -> None:
        from tools import verify_output

        assert verify_output.description
        assert len(verify_output.description) > 10


# ---------------------------------------------------------------------------
# analyse_context tests
# ---------------------------------------------------------------------------


class TestAnalyseContext:
    """Test analyse_context tool behavior."""

    def test_returns_string(self) -> None:
        from tools import analyse_context

        result = analyse_context.invoke({"query": "test query", "domain": "testing"})
        assert isinstance(result, str)

    def test_reads_existing_file(self, tmp_path: pytest.TempPathFactory) -> None:
        """When query points to a readable file, return its content summary."""
        from tools import analyse_context

        test_file = tmp_path / "context.md"
        test_file.write_text("# Project Context\nThis is a test project.")
        result = analyse_context.invoke({"query": str(test_file), "domain": "testing"})
        assert isinstance(result, str)
        assert "test project" in result.lower() or "context" in result.lower()

    def test_handles_missing_file_gracefully(self) -> None:
        """When query references a non-existent file, return error string instead of raising."""
        from tools import analyse_context

        result = analyse_context.invoke({"query": "/nonexistent/path/file.md", "domain": "testing"})
        assert isinstance(result, str)
        # Should not raise — should return an informative string

    def test_never_raises_exception(self) -> None:
        from tools import analyse_context

        # Even with bizarre input, should return a string
        result = analyse_context.invoke({"query": "", "domain": ""})
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# plan_pipeline tests
# ---------------------------------------------------------------------------


class TestPlanPipeline:
    """Test plan_pipeline tool behavior."""

    def test_returns_string(self) -> None:
        from tools import plan_pipeline

        result = plan_pipeline.invoke({"task": "build feature", "context": "python project"})
        assert isinstance(result, str)

    def test_returns_valid_json_string(self) -> None:
        """Pipeline plan should be a parseable JSON string."""
        from tools import plan_pipeline

        result = plan_pipeline.invoke({"task": "build feature", "context": "python project"})
        parsed = json.loads(result)
        assert isinstance(parsed, (dict, list))

    def test_json_contains_steps(self) -> None:
        """Pipeline plan JSON should contain steps."""
        from tools import plan_pipeline

        result = plan_pipeline.invoke({"task": "implement auth", "context": "web app"})
        parsed = json.loads(result)
        assert "steps" in parsed
        assert isinstance(parsed["steps"], list)
        assert len(parsed["steps"]) > 0

    def test_never_raises_exception(self) -> None:
        from tools import plan_pipeline

        result = plan_pipeline.invoke({"task": "", "context": ""})
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# execute_command tests
# ---------------------------------------------------------------------------


class TestExecuteCommand:
    """Test execute_command tool behavior."""

    def test_returns_string(self) -> None:
        from tools import execute_command

        result = execute_command.invoke({"command": "echo", "arguments": "hello"})
        assert isinstance(result, str)

    def test_returns_execution_result(self) -> None:
        """Should return a meaningful execution result string."""
        from tools import execute_command

        result = execute_command.invoke({"command": "test_cmd", "arguments": "--verbose"})
        assert isinstance(result, str)
        assert len(result) > 0

    def test_handles_empty_args(self) -> None:
        from tools import execute_command

        result = execute_command.invoke({"command": "status", "arguments": ""})
        assert isinstance(result, str)

    def test_never_raises_exception(self) -> None:
        from tools import execute_command

        result = execute_command.invoke({"command": "", "arguments": ""})
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# verify_output tests
# ---------------------------------------------------------------------------


class TestVerifyOutput:
    """Test verify_output tool behavior."""

    def test_returns_string(self) -> None:
        from tools import verify_output

        result = verify_output.invoke({"output_path": "/tmp/test", "criteria": "exists"})
        assert isinstance(result, str)

    def test_existing_path_passes(self, tmp_path: pytest.TempPathFactory) -> None:
        """When output_path exists, verification should indicate success."""
        from tools import verify_output

        test_file = tmp_path / "output.txt"
        test_file.write_text("output content")
        result = verify_output.invoke({"output_path": str(test_file), "criteria": "file exists"})
        assert isinstance(result, str)
        assert "pass" in result.lower() or "success" in result.lower() or "verified" in result.lower()

    def test_missing_path_fails_verification(self) -> None:
        """When output_path does not exist, verification should indicate failure."""
        from tools import verify_output

        result = verify_output.invoke({"output_path": "/nonexistent/output.txt", "criteria": "file exists"})
        assert isinstance(result, str)
        assert "fail" in result.lower() or "not found" in result.lower() or "error" in result.lower()

    def test_checks_content_criteria(self, tmp_path: pytest.TempPathFactory) -> None:
        """When criteria mention content, should check file content."""
        from tools import verify_output

        test_file = tmp_path / "result.json"
        test_file.write_text('{"status": "ok"}')
        result = verify_output.invoke({"output_path": str(test_file), "criteria": "contains valid JSON"})
        assert isinstance(result, str)

    def test_never_raises_exception(self) -> None:
        from tools import verify_output

        result = verify_output.invoke({"output_path": "", "criteria": ""})
        assert isinstance(result, str)

    def test_non_empty_criteria_with_content(self, tmp_path: pytest.TempPathFactory) -> None:
        """When criteria include 'non-empty' and file has content, should pass."""
        from tools import verify_output

        test_file = tmp_path / "data.txt"
        test_file.write_text("some content")
        result = verify_output.invoke({"output_path": str(test_file), "criteria": "file is non-empty"})
        assert isinstance(result, str)
        assert "passed" in result.lower()

    def test_non_empty_criteria_with_empty_file(self, tmp_path: pytest.TempPathFactory) -> None:
        """When criteria include 'non-empty' and file is empty, should fail."""
        from tools import verify_output

        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        result = verify_output.invoke({"output_path": str(test_file), "criteria": "file is non-empty"})
        assert isinstance(result, str)
        assert "failed" in result.lower()

    def test_invalid_json_criteria(self, tmp_path: pytest.TempPathFactory) -> None:
        """When criteria include 'json' but content is not valid JSON, should fail."""
        from tools import verify_output

        test_file = tmp_path / "bad.json"
        test_file.write_text("not json at all {{{")
        result = verify_output.invoke({"output_path": str(test_file), "criteria": "contains valid JSON"})
        assert isinstance(result, str)
        assert "failed" in result.lower()

    def test_directory_verification(self, tmp_path: pytest.TempPathFactory) -> None:
        """When output_path is a directory, should still pass existence check."""
        from tools import verify_output

        result = verify_output.invoke({"output_path": str(tmp_path), "criteria": "exists"})
        assert isinstance(result, str)
        assert "passed" in result.lower()

    def test_not_empty_criteria_variant(self, tmp_path: pytest.TempPathFactory) -> None:
        """'not empty' variant of the non-empty criteria check."""
        from tools import verify_output

        test_file = tmp_path / "content.txt"
        test_file.write_text("hello")
        result = verify_output.invoke({"output_path": str(test_file), "criteria": "file is not empty"})
        assert isinstance(result, str)
        assert "passed" in result.lower()


# ---------------------------------------------------------------------------
# Error-path tests — use mocking to trigger exception handlers
# ---------------------------------------------------------------------------


class TestAnalyseContextErrors:
    """Test analyse_context error handling paths."""

    def test_os_error_returns_string(self) -> None:
        """When file read raises OSError, should return error string."""
        from tools.orchestrator_tools import analyse_context as ac_func

        with patch("tools.orchestrator_tools.Path") as mock_path:
            mock_instance = mock_path.return_value
            mock_instance.is_file.side_effect = OSError("Permission denied")
            result = ac_func.invoke({"query": "/some/path", "domain": "test"})
            assert isinstance(result, str)
            assert "error" in result.lower()

    def test_unexpected_error_returns_string(self) -> None:
        """When an unexpected error occurs, should return error string."""
        from tools.orchestrator_tools import analyse_context as ac_func

        with patch("tools.orchestrator_tools.Path") as mock_path:
            mock_instance = mock_path.return_value
            mock_instance.is_file.side_effect = RuntimeError("unexpected")
            result = ac_func.invoke({"query": "/some/path", "domain": "test"})
            assert isinstance(result, str)
            assert "error" in result.lower()


class TestPlanPipelineErrors:
    """Test plan_pipeline error handling paths."""

    def test_json_serialization_error_returns_string(self) -> None:
        """When JSON serialization fails, should return error JSON string."""
        from tools.orchestrator_tools import plan_pipeline as pp_func

        with patch("tools.orchestrator_tools.json.dumps") as mock_dumps:
            # First call raises, second call (in except) succeeds
            mock_dumps.side_effect = [TypeError("not serializable"), '{"error": "test", "steps": []}']
            result = pp_func.invoke({"task": "test", "context": "ctx"})
            assert isinstance(result, str)

    def test_unexpected_error_returns_string(self) -> None:
        """When an unexpected error occurs, should return error JSON string."""
        from tools.orchestrator_tools import plan_pipeline as pp_func

        with patch("tools.orchestrator_tools.json.dumps") as mock_dumps:
            mock_dumps.side_effect = [RuntimeError("unexpected"), '{"error": "unexpected", "steps": []}']
            result = pp_func.invoke({"task": "test", "context": "ctx"})
            assert isinstance(result, str)


class TestVerifyOutputErrors:
    """Test verify_output error handling paths."""

    def test_os_error_on_path_check(self) -> None:
        """When Path.exists() raises OSError, should return error string."""
        from tools.orchestrator_tools import verify_output as vo_func

        with patch("tools.orchestrator_tools.Path") as mock_path:
            mock_instance = mock_path.return_value
            mock_instance.__str__ = lambda self: "/test/path"
            mock_instance.exists.side_effect = OSError("disk error")
            # Need str(path).strip() to not be empty
            result = vo_func.invoke({"output_path": "/test/path", "criteria": "exists"})
            assert isinstance(result, str)
            assert "error" in result.lower()

    def test_unexpected_error_returns_string(self) -> None:
        """When an unexpected error occurs, should return error string."""
        from tools.orchestrator_tools import verify_output as vo_func

        with patch("tools.orchestrator_tools.Path") as mock_path:
            mock_instance = mock_path.return_value
            mock_instance.__str__ = lambda self: "/test/path"
            mock_instance.exists.side_effect = RuntimeError("unexpected")
            result = vo_func.invoke({"output_path": "/test/path", "criteria": "exists"})
            assert isinstance(result, str)
            assert "error" in result.lower()

    def test_unreadable_file_returns_error(self, tmp_path: pytest.TempPathFactory) -> None:
        """When a file can't be read, should return verification failed."""
        from tools.orchestrator_tools import verify_output as vo_func

        test_file = tmp_path / "unreadable.bin"
        test_file.write_bytes(b"\x80\x81\x82\x83")

        with patch("tools.orchestrator_tools.Path") as mock_path_cls:
            mock_path = mock_path_cls.return_value
            mock_path.__str__ = lambda self: str(test_file)
            mock_path.exists.return_value = True
            mock_path.is_file.return_value = True
            mock_path.read_text.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")
            result = vo_func.invoke({"output_path": str(test_file), "criteria": "readable"})
            assert isinstance(result, str)
            assert "failed" in result.lower()
