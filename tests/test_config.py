"""Tests for orchestrator-config.yaml structure and content.

Validates that the configuration file meets all acceptance criteria:
- AC-001: orchestrator-config.yaml exists and contains required sections
- AC-002: orchestrator.reasoning_model in provider:model format
- AC-003: orchestrator.implementation_model in provider:model format
- AC-004: orchestrator.checkpoint_level is a string
- AC-005: project section with name and description
- AC-012: Model values use provider:model format compatible with init_chat_model()
"""

import os
import re

import pytest
import yaml

# Base path for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "orchestrator-config.yaml")

# Regex for provider:model format — provider is alphanumeric/hyphens,
# model is alphanumeric/hyphens/dots/underscores
PROVIDER_MODEL_PATTERN = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9_-]*:[a-zA-Z][a-zA-Z0-9._-]*$"
)


@pytest.fixture
def config():
    """Load and return the parsed YAML configuration."""
    assert os.path.isfile(CONFIG_PATH), (
        f"orchestrator-config.yaml not found at {CONFIG_PATH}"
    )
    with open(CONFIG_PATH, "r") as f:
        data = yaml.safe_load(f)
    assert data is not None, "orchestrator-config.yaml is empty"
    return data


class TestConfigFileExists:
    """AC-001: orchestrator-config.yaml exists and is valid YAML."""

    def test_config_file_exists(self):
        assert os.path.isfile(CONFIG_PATH), (
            f"Expected orchestrator-config.yaml at {CONFIG_PATH}"
        )

    def test_config_file_is_valid_yaml(self):
        with open(CONFIG_PATH, "r") as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict), "Config must parse to a YAML mapping"

    def test_config_has_orchestrator_section(self, config):
        assert "orchestrator" in config, (
            "Config must have an 'orchestrator' section"
        )

    def test_config_has_project_section(self, config):
        assert "project" in config, "Config must have a 'project' section"


class TestReasoningModel:
    """AC-002: orchestrator.reasoning_model in provider:model format."""

    def test_reasoning_model_exists(self, config):
        assert "reasoning_model" in config["orchestrator"], (
            "orchestrator section must contain reasoning_model"
        )

    def test_reasoning_model_is_string(self, config):
        value = config["orchestrator"]["reasoning_model"]
        assert isinstance(value, str), "reasoning_model must be a string"

    def test_reasoning_model_provider_model_format(self, config):
        value = config["orchestrator"]["reasoning_model"]
        assert PROVIDER_MODEL_PATTERN.match(value), (
            f"reasoning_model '{value}' must match 'provider:model' format"
        )

    def test_reasoning_model_has_provider(self, config):
        value = config["orchestrator"]["reasoning_model"]
        parts = value.split(":")
        assert len(parts) == 2, (
            f"reasoning_model '{value}' must have exactly one colon separator"
        )
        assert len(parts[0]) > 0, "Provider part must not be empty"
        assert len(parts[1]) > 0, "Model part must not be empty"


class TestImplementationModel:
    """AC-003: orchestrator.implementation_model in provider:model format."""

    def test_implementation_model_exists(self, config):
        assert "implementation_model" in config["orchestrator"], (
            "orchestrator section must contain implementation_model"
        )

    def test_implementation_model_is_string(self, config):
        value = config["orchestrator"]["implementation_model"]
        assert isinstance(value, str), "implementation_model must be a string"

    def test_implementation_model_provider_model_format(self, config):
        value = config["orchestrator"]["implementation_model"]
        assert PROVIDER_MODEL_PATTERN.match(value), (
            f"implementation_model '{value}' must match 'provider:model' format"
        )

    def test_implementation_model_has_provider(self, config):
        value = config["orchestrator"]["implementation_model"]
        parts = value.split(":")
        assert len(parts) == 2, (
            f"implementation_model '{value}' must have exactly one colon separator"
        )
        assert len(parts[0]) > 0, "Provider part must not be empty"
        assert len(parts[1]) > 0, "Model part must not be empty"


class TestCheckpointLevel:
    """AC-004: orchestrator.checkpoint_level is a string."""

    def test_checkpoint_level_exists(self, config):
        assert "checkpoint_level" in config["orchestrator"], (
            "orchestrator section must contain checkpoint_level"
        )

    def test_checkpoint_level_is_string(self, config):
        value = config["orchestrator"]["checkpoint_level"]
        assert isinstance(value, str), "checkpoint_level must be a string"

    def test_checkpoint_level_not_empty(self, config):
        value = config["orchestrator"]["checkpoint_level"]
        assert len(value.strip()) > 0, "checkpoint_level must not be empty"

    def test_checkpoint_level_is_valid_option(self, config):
        value = config["orchestrator"]["checkpoint_level"]
        valid_options = {"minimal", "standard", "verbose"}
        assert value in valid_options, (
            f"checkpoint_level '{value}' must be one of {valid_options}"
        )


class TestProjectSection:
    """AC-005: project section with name and description."""

    def test_project_name_exists(self, config):
        assert "name" in config["project"], (
            "project section must contain name"
        )

    def test_project_name_is_string(self, config):
        value = config["project"]["name"]
        assert isinstance(value, str), "project.name must be a string"

    def test_project_name_not_empty(self, config):
        value = config["project"]["name"]
        assert len(value.strip()) > 0, "project.name must not be empty"

    def test_project_description_exists(self, config):
        assert "description" in config["project"], (
            "project section must contain description"
        )

    def test_project_description_is_string(self, config):
        value = config["project"]["description"]
        assert isinstance(value, str), "project.description must be a string"

    def test_project_description_not_empty(self, config):
        value = config["project"]["description"]
        assert len(value.strip()) > 0, "project.description must not be empty"


class TestInitChatModelCompatibility:
    """AC-012: Model values use provider:model format compatible with init_chat_model()."""

    def test_reasoning_model_init_chat_model_compatible(self, config):
        """Verify reasoning_model can be split into provider and model for init_chat_model()."""
        value = config["orchestrator"]["reasoning_model"]
        provider, model = value.split(":")
        # init_chat_model() expects a non-empty provider and model name
        assert provider.isidentifier() or provider.replace("-", "_").isidentifier(), (
            f"Provider '{provider}' should be a valid identifier for init_chat_model()"
        )
        assert len(model) > 0, "Model name must not be empty"

    def test_implementation_model_init_chat_model_compatible(self, config):
        """Verify implementation_model can be split into provider and model for init_chat_model()."""
        value = config["orchestrator"]["implementation_model"]
        provider, model = value.split(":")
        assert provider.isidentifier() or provider.replace("-", "_").isidentifier(), (
            f"Provider '{provider}' should be a valid identifier for init_chat_model()"
        )
        assert len(model) > 0, "Model name must not be empty"

    def test_models_use_known_providers(self, config):
        """Check that model providers are from known LLM providers."""
        known_providers = {
            "anthropic", "openai", "google_genai", "google_vertexai",
            "ollama", "together", "fireworks", "mistral", "cohere",
            "huggingface", "bedrock", "azure_openai",
        }
        for key in ("reasoning_model", "implementation_model"):
            value = config["orchestrator"][key]
            provider = value.split(":")[0]
            assert provider in known_providers, (
                f"Provider '{provider}' in {key} is not a known provider. "
                f"Known: {known_providers}"
            )
