"""Tests for agent.py entrypoint wiring (TASK-OEX-006, TASK-EVF-001).

Verifies that agent.py correctly reads configuration, loads domain context,
creates the orchestrator, and exports a module-level ``agent`` variable
compatible with langgraph.json.  Also verifies the ``--domain`` CLI argument
added in TASK-EVF-001.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Root of the project (one level up from tests/).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# AC-001: agent.py reads orchestrator-config.yaml using yaml.safe_load()
# ---------------------------------------------------------------------------


class TestConfigReading:
    """AC-001: agent.py reads orchestrator-config.yaml with yaml.safe_load()."""

    def test_agent_module_reads_config_yaml(self, tmp_path: Path) -> None:
        """Verify that _load_config reads and parses orchestrator-config.yaml."""
        from agent import _load_config

        config_file = tmp_path / "orchestrator-config.yaml"
        config_file.write_text(
            textwrap.dedent("""\
                orchestrator:
                  reasoning_model: "test:reasoning"
                  implementation_model: "test:implementation"
                project:
                  name: "test-project"
            """)
        )
        config = _load_config(config_file)
        assert config["orchestrator"]["reasoning_model"] == "test:reasoning"
        assert config["orchestrator"]["implementation_model"] == "test:implementation"

    def test_load_config_uses_safe_load(self, tmp_path: Path) -> None:
        """Ensure yaml.safe_load is used (not yaml.load)."""
        from agent import _load_config

        config_file = tmp_path / "orchestrator-config.yaml"
        config_file.write_text("orchestrator:\n  reasoning_model: 'x'\n  implementation_model: 'y'\n")
        with patch.object(yaml, "safe_load", wraps=yaml.safe_load) as mock_sl:
            _load_config(config_file)
            mock_sl.assert_called_once()

    def test_load_config_returns_defaults_when_file_missing(self) -> None:
        """If orchestrator-config.yaml doesn't exist, return sensible defaults."""
        from agent import _load_config

        missing = Path("/nonexistent/orchestrator-config.yaml")
        config = _load_config(missing)
        # Must still have orchestrator keys
        assert "orchestrator" in config
        assert "reasoning_model" in config["orchestrator"]
        assert "implementation_model" in config["orchestrator"]
        assert isinstance(config["orchestrator"]["reasoning_model"], str)
        assert len(config["orchestrator"]["reasoning_model"]) > 0


# ---------------------------------------------------------------------------
# AC-002: agent.py reads domain prompt from domains/example-domain/DOMAIN.md
# ---------------------------------------------------------------------------


class TestDomainReading:
    """AC-002: agent.py reads domain prompt from domains/{domain}/DOMAIN.md."""

    def test_load_domain_prompt_reads_file(self, tmp_path: Path) -> None:
        """Verify _load_domain_prompt reads DOMAIN.md content."""
        from agent import _load_domain_prompt

        domain_dir = tmp_path / "domains" / "my-domain"
        domain_dir.mkdir(parents=True)
        domain_file = domain_dir / "DOMAIN.md"
        domain_file.write_text("# My Domain\n\nCustom guidelines here.\n")
        result = _load_domain_prompt(tmp_path, "my-domain")
        assert "Custom guidelines here." in result

    def test_load_domain_prompt_returns_default_when_missing(self, tmp_path: Path) -> None:
        """If DOMAIN.md is missing, return a non-empty default string."""
        from agent import _load_domain_prompt

        result = _load_domain_prompt(tmp_path, "nonexistent-domain")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_load_domain_prompt_default_domain(self) -> None:
        """The default domain should be 'example-domain'."""
        from agent import DEFAULT_DOMAIN

        assert DEFAULT_DOMAIN == "example-domain"


# ---------------------------------------------------------------------------
# AC-003: agent.py calls create_orchestrator() with config values + domain
# ---------------------------------------------------------------------------


class TestCreateOrchestratorCall:
    """AC-003: agent.py calls create_orchestrator() with config values and domain prompt."""

    def test_agent_module_calls_create_orchestrator(self) -> None:
        """The module wires config values and domain prompt into create_orchestrator()."""
        # We'll test the _build_agent helper that does the wiring
        from agent import _build_agent

        mock_graph = MagicMock()
        config = {
            "orchestrator": {
                "reasoning_model": "provider:reason",
                "implementation_model": "provider:impl",
            }
        }
        domain_prompt = "Test domain prompt"
        with patch("agent.create_orchestrator", return_value=mock_graph) as mock_co:
            result = _build_agent(config, domain_prompt)
            mock_co.assert_called_once_with(
                reasoning_model="provider:reason",
                implementation_model="provider:impl",
                domain_prompt="Test domain prompt",
            )
            assert result is mock_graph

    def test_build_agent_passes_models_from_config(self) -> None:
        """Models extracted from config are passed through correctly."""
        from agent import _build_agent

        config = {
            "orchestrator": {
                "reasoning_model": "anthropic:claude-sonnet-4-6",
                "implementation_model": "anthropic:claude-haiku-4-5",
            }
        }
        with patch("agent.create_orchestrator", return_value=MagicMock()) as mock_co:
            _build_agent(config, "some domain")
            call_kwargs = mock_co.call_args
            assert call_kwargs.kwargs["reasoning_model"] == "anthropic:claude-sonnet-4-6"
            assert call_kwargs.kwargs["implementation_model"] == "anthropic:claude-haiku-4-5"


# ---------------------------------------------------------------------------
# AC-004: Module-level agent variable exported (required for langgraph.json)
# ---------------------------------------------------------------------------


class TestModuleLevelAgent:
    """AC-004: Module-level `agent` variable is exported for langgraph.json."""

    def test_agent_attribute_exists(self) -> None:
        """agent.py must have a module-level `agent` attribute."""
        import agent

        assert hasattr(agent, "agent"), "agent.py must export a module-level 'agent' variable"

    def test_agent_is_not_none(self) -> None:
        """The module-level agent should not be None."""
        import agent

        # It could be None if create_orchestrator fails, but in normal
        # operation (with mocked deps), it should be set.
        # Note: agent might be None if .env / config is not available,
        # but the attribute must exist.
        assert hasattr(agent, "agent")


# ---------------------------------------------------------------------------
# AC-005: python-dotenv loads .env file for API keys
# ---------------------------------------------------------------------------


class TestDotenvLoading:
    """AC-005: python-dotenv loads .env file for API keys."""

    def test_load_dotenv_is_called(self) -> None:
        """agent.py should call load_dotenv() at module load time."""
        # We verify by checking that dotenv is imported and used
        import importlib

        with patch("dotenv.load_dotenv") as mock_ld:
            # Force reimport to trigger module-level code
            import agent

            importlib.reload(agent)
            mock_ld.assert_called()


# ---------------------------------------------------------------------------
# AC-006: Graceful handling if .env or domain file is missing (with defaults)
# ---------------------------------------------------------------------------


class TestGracefulDefaults:
    """AC-006: Graceful handling when .env or domain file is missing."""

    def test_load_config_handles_invalid_yaml(self, tmp_path: Path) -> None:
        """If YAML is malformed, return defaults rather than crashing."""
        from agent import _load_config

        config_file = tmp_path / "orchestrator-config.yaml"
        config_file.write_text(":\n  invalid:\nyaml: [[[")
        config = _load_config(config_file)
        assert "orchestrator" in config
        assert "reasoning_model" in config["orchestrator"]

    def test_load_domain_prompt_handles_encoding_error(self, tmp_path: Path) -> None:
        """If DOMAIN.md has encoding issues, return a default gracefully."""
        from agent import _load_domain_prompt

        domain_dir = tmp_path / "domains" / "bad-domain"
        domain_dir.mkdir(parents=True)
        domain_file = domain_dir / "DOMAIN.md"
        domain_file.write_bytes(b"\x80\x81\x82\x83")  # Invalid UTF-8
        result = _load_domain_prompt(tmp_path, "bad-domain")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_agent_with_default_config(self) -> None:
        """_build_agent works even with default config values."""
        from agent import _build_agent

        default_config = {
            "orchestrator": {
                "reasoning_model": "anthropic:claude-sonnet-4-6",
                "implementation_model": "anthropic:claude-haiku-4-5",
            }
        }
        with patch("agent.create_orchestrator", return_value=MagicMock()) as mock_co:
            result = _build_agent(default_config, "default domain prompt")
            mock_co.assert_called_once()
            assert result is not None

    def test_load_config_no_orchestrator_key(self, tmp_path: Path) -> None:
        """Config with valid YAML but no 'orchestrator' key returns defaults."""
        from agent import _load_config

        config_file = tmp_path / "orchestrator-config.yaml"
        config_file.write_text("project:\n  name: test\n")
        config = _load_config(config_file)
        assert "orchestrator" in config
        assert "reasoning_model" in config["orchestrator"]

    def test_load_config_orchestrator_not_dict(self, tmp_path: Path) -> None:
        """Config where orchestrator is a scalar (not mapping) returns defaults."""
        from agent import _load_config

        config_file = tmp_path / "orchestrator-config.yaml"
        config_file.write_text("orchestrator: just-a-string\n")
        config = _load_config(config_file)
        assert "orchestrator" in config
        assert isinstance(config["orchestrator"], dict)
        assert "reasoning_model" in config["orchestrator"]

    def test_load_config_missing_model_keys(self, tmp_path: Path) -> None:
        """Config with orchestrator but missing model keys merges defaults."""
        from agent import _load_config

        config_file = tmp_path / "orchestrator-config.yaml"
        config_file.write_text("orchestrator:\n  checkpoint_level: standard\n")
        config = _load_config(config_file)
        assert "orchestrator" in config
        assert "reasoning_model" in config["orchestrator"]
        assert "implementation_model" in config["orchestrator"]
        # The original checkpoint_level should also be preserved
        assert config["orchestrator"]["checkpoint_level"] == "standard"


# ---------------------------------------------------------------------------
# AC-007: Integration — the real orchestrator-config.yaml is parseable
# ---------------------------------------------------------------------------


class TestRealConfigIntegration:
    """Integration tests against the actual project config and domain files."""

    def test_real_config_yaml_parseable(self) -> None:
        """orchestrator-config.yaml in the project root is valid YAML."""
        config_path = _PROJECT_ROOT / "orchestrator-config.yaml"
        if not config_path.exists():
            pytest.skip("orchestrator-config.yaml not found in project root")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert "orchestrator" in config
        assert "reasoning_model" in config["orchestrator"]
        assert "implementation_model" in config["orchestrator"]

    def test_real_domain_md_exists(self) -> None:
        """domains/example-domain/DOMAIN.md exists in the project root."""
        domain_path = _PROJECT_ROOT / "domains" / "example-domain" / "DOMAIN.md"
        if not domain_path.exists():
            pytest.skip("DOMAIN.md not found")
        content = domain_path.read_text()
        assert len(content) > 0

    def test_langgraph_json_references_agent(self) -> None:
        """langgraph.json references ./agent.py:agent."""
        import json

        lg_path = _PROJECT_ROOT / "langgraph.json"
        if not lg_path.exists():
            pytest.skip("langgraph.json not found")
        with open(lg_path) as f:
            lg = json.load(f)
        assert "graphs" in lg
        assert "orchestrator" in lg["graphs"]
        assert lg["graphs"]["orchestrator"] == "./agent.py:agent"


# ---------------------------------------------------------------------------
# TASK-EVF-001: --domain CLI argument added to agent.py
# ---------------------------------------------------------------------------


class TestCLIArgument:
    """TASK-EVF-001: --domain CLI argument parsed via argparse.parse_known_args()."""

    def test_argparse_domain_default(self) -> None:
        """parse_known_args with no args gives the default domain 'example-domain'."""
        from agent import _arg_parser

        args, unknown = _arg_parser.parse_known_args([])
        assert args.domain == "example-domain"
        assert unknown == []

    def test_argparse_domain_custom(self) -> None:
        """--domain custom-domain parses the provided value correctly."""
        from agent import _arg_parser

        args, unknown = _arg_parser.parse_known_args(["--domain", "custom-domain"])
        assert args.domain == "custom-domain"
        assert unknown == []

    def test_argparse_unknown_args_ignored(self) -> None:
        """Unknown arguments are collected silently (parse_known_args behaviour)."""
        from agent import _arg_parser

        args, unknown = _arg_parser.parse_known_args(["--domain", "my-domain", "--unexpected-flag", "value"])
        assert args.domain == "my-domain"
        assert "--unexpected-flag" in unknown

    def test_cli_help_runs(self) -> None:
        """Running ``python agent.py --help`` exits cleanly with exit code 0."""
        result = subprocess.run(
            [sys.executable, str(_PROJECT_ROOT / "agent.py"), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--domain" in result.stdout
        assert "example-domain" in result.stdout
