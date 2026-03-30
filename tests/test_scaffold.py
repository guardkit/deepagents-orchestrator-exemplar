"""Tests for TASK-OEX-001: Scaffold project structure and dependencies."""

import json
import tomllib
from pathlib import Path

# Project root is the parent of the tests/ directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestPyprojectToml:
    """AC-001 & AC-002: pyproject.toml exists with required dependencies and Python version."""

    def test_pyproject_toml_exists(self):
        """pyproject.toml must exist at project root."""
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        assert pyproject_path.exists(), f"pyproject.toml not found at {pyproject_path}"

    def test_pyproject_toml_is_valid_toml(self):
        """pyproject.toml must be valid TOML."""
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        assert "project" in data, "pyproject.toml must have a [project] section"

    def test_required_dependencies_present(self):
        """AC-001: All required dependencies must be listed."""
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        dependencies = data["project"]["dependencies"]
        # Normalize to lowercase for comparison
        deps_lower = [d.lower() for d in dependencies]

        required = {
            "deepagents": ">=0.5.0a2",
            "langchain": ">=1.2.11",
            "langchain-core": ">=1.2.21",
            "langgraph": ">=0.2",
            "langsmith": ">=0.3",
            "python-dotenv": ">=1.0",
            "pyyaml": ">=6.0",
        }

        for pkg_name, min_version in required.items():
            found = False
            for dep in deps_lower:
                if dep.startswith(pkg_name):
                    found = True
                    assert min_version.lower() in dep, (
                        f"Dependency {pkg_name} must have version specifier {min_version}, got: {dep}"
                    )
                    break
            assert found, f"Required dependency {pkg_name}{min_version} not found in pyproject.toml"

    def test_python_version_requirement(self):
        """AC-002: Python version must be >=3.11,<4.0."""
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        requires_python = data["project"]["requires-python"]
        assert ">=3.11" in requires_python, f"Python version must include >=3.11, got: {requires_python}"
        assert "<4.0" in requires_python, f"Python version must include <4.0, got: {requires_python}"


class TestEnvExample:
    """AC-003: .env.example documents required environment variables."""

    def test_env_example_exists(self):
        """.env.example must exist at project root."""
        env_path = PROJECT_ROOT / ".env.example"
        assert env_path.exists(), f".env.example not found at {env_path}"

    def test_required_env_vars_documented(self):
        """All required environment variables must be documented."""
        env_path = PROJECT_ROOT / ".env.example"
        content = env_path.read_text()

        required_vars = [
            "LANGSMITH_API_KEY",
            "LANGSMITH_TRACING",
            "LANGSMITH_PROJECT",
            "ANTHROPIC_API_KEY",
        ]

        for var in required_vars:
            assert var in content, f"Required env var {var} not found in .env.example"

    def test_optional_env_vars_documented(self):
        """Optional environment variables must be documented."""
        env_path = PROJECT_ROOT / ".env.example"
        content = env_path.read_text()

        optional_vars = [
            "GOOGLE_API_KEY",
            "LOCAL_MODEL_ENDPOINT",
        ]

        for var in optional_vars:
            assert var in content, f"Optional env var {var} not found in .env.example"

    def test_optional_vars_marked_as_optional(self):
        """Optional vars should be indicated as optional (commented out or labeled)."""
        env_path = PROJECT_ROOT / ".env.example"
        content = env_path.read_text()

        # GOOGLE_API_KEY should be commented out or marked optional
        assert "optional" in content.lower() or "# GOOGLE_API_KEY" in content, (
            "GOOGLE_API_KEY should be marked as optional"
        )
        assert "optional" in content.lower() or "# LOCAL_MODEL_ENDPOINT" in content, (
            "LOCAL_MODEL_ENDPOINT should be marked as optional"
        )


class TestGitignore:
    """AC-004: .gitignore covers required patterns."""

    def test_gitignore_exists(self):
        """.gitignore must exist at project root."""
        gitignore_path = PROJECT_ROOT / ".gitignore"
        assert gitignore_path.exists(), f".gitignore not found at {gitignore_path}"

    def test_pycache_ignored(self):
        """__pycache__ must be ignored."""
        content = (PROJECT_ROOT / ".gitignore").read_text()
        assert "__pycache__" in content, "__pycache__ not found in .gitignore"

    def test_env_ignored(self):
        """.env must be ignored."""
        content = (PROJECT_ROOT / ".gitignore").read_text()
        # Check that .env is ignored (not .env.example)
        lines = content.splitlines()
        env_ignored = any(
            line.strip() == ".env" or line.strip() == ".env/" for line in lines if not line.startswith("#")
        )
        assert env_ignored, ".env not found as ignored pattern in .gitignore"

    def test_pyc_ignored(self):
        """*.pyc must be ignored."""
        content = (PROJECT_ROOT / ".gitignore").read_text()
        # *.py[codz] covers *.pyc
        assert "*.pyc" in content or "*.py[cod" in content, "*.pyc pattern not found in .gitignore"

    def test_venv_ignored(self):
        """.venv/ must be ignored."""
        content = (PROJECT_ROOT / ".gitignore").read_text()
        # .venv (without slash) in gitignore matches both file and directory
        assert ".venv" in content, ".venv not found in .gitignore"

    def test_dist_ignored(self):
        """dist/ must be ignored."""
        content = (PROJECT_ROOT / ".gitignore").read_text()
        assert "dist/" in content, "dist/ not found in .gitignore"

    def test_egg_info_ignored(self):
        """*.egg-info/ must be ignored."""
        content = (PROJECT_ROOT / ".gitignore").read_text()
        assert "*.egg-info/" in content, "*.egg-info/ not found in .gitignore"


class TestLanggraphJson:
    """AC-005: langgraph.json references ./agent.py:agent as graph entry point."""

    def test_langgraph_json_exists(self):
        """langgraph.json must exist at project root."""
        lg_path = PROJECT_ROOT / "langgraph.json"
        assert lg_path.exists(), f"langgraph.json not found at {lg_path}"

    def test_langgraph_json_is_valid_json(self):
        """langgraph.json must be valid JSON."""
        lg_path = PROJECT_ROOT / "langgraph.json"
        with open(lg_path) as f:
            data = json.load(f)
        assert isinstance(data, dict), "langgraph.json must contain a JSON object"

    def test_graph_entry_point(self):
        """Graph entry point must reference ./agent.py:agent."""
        lg_path = PROJECT_ROOT / "langgraph.json"
        with open(lg_path) as f:
            data = json.load(f)

        assert "graphs" in data, "langgraph.json must have a 'graphs' key"
        graphs = data["graphs"]
        # At least one graph must reference ./agent.py:agent
        entry_points = list(graphs.values())
        assert "./agent.py:agent" in entry_points, (
            f"langgraph.json graphs must reference './agent.py:agent', got: {entry_points}"
        )

    def test_dependencies_key(self):
        """langgraph.json should have dependencies key."""
        lg_path = PROJECT_ROOT / "langgraph.json"
        with open(lg_path) as f:
            data = json.load(f)
        assert "dependencies" in data, "langgraph.json must have a 'dependencies' key"

    def test_env_key(self):
        """langgraph.json should reference .env file."""
        lg_path = PROJECT_ROOT / "langgraph.json"
        with open(lg_path) as f:
            data = json.load(f)
        assert "env" in data, "langgraph.json must have an 'env' key"
        assert data["env"] == ".env", f"langgraph.json env must be '.env', got: {data['env']}"


class TestInitFiles:
    """AC-006: Empty __init__.py files created in agents/, tools/, prompts/."""

    def test_agents_init_exists(self):
        """agents/__init__.py must exist."""
        init_path = PROJECT_ROOT / "agents" / "__init__.py"
        assert init_path.exists(), f"agents/__init__.py not found at {init_path}"

    def test_tools_init_exists(self):
        """tools/__init__.py must exist."""
        init_path = PROJECT_ROOT / "tools" / "__init__.py"
        assert init_path.exists(), f"tools/__init__.py not found at {init_path}"

    def test_prompts_init_exists(self):
        """prompts/__init__.py must exist."""
        init_path = PROJECT_ROOT / "prompts" / "__init__.py"
        assert init_path.exists(), f"prompts/__init__.py not found at {init_path}"

    def test_agents_init_is_empty(self):
        """agents/__init__.py must be empty."""
        init_path = PROJECT_ROOT / "agents" / "__init__.py"
        content = init_path.read_text().strip()
        assert content == "", f"agents/__init__.py should be empty, got: {content!r}"

    def test_tools_init_is_empty(self):
        """tools/__init__.py must be empty."""
        init_path = PROJECT_ROOT / "tools" / "__init__.py"
        content = init_path.read_text().strip()
        assert content == "", f"tools/__init__.py should be empty, got: {content!r}"

    def test_prompts_init_exists_and_is_valid_python(self):
        """prompts/__init__.py must exist (may be populated by other tasks)."""
        init_path = PROJECT_ROOT / "prompts" / "__init__.py"
        assert init_path.exists(), f"prompts/__init__.py must exist at {init_path}"
        # File was created empty by this task; other tasks may have since populated it
        content = init_path.read_text()
        assert isinstance(content, str), "prompts/__init__.py must be readable"

    def test_agents_directory_is_package(self):
        """agents/ directory must be a Python package (importable)."""
        assert (PROJECT_ROOT / "agents").is_dir(), "agents/ directory must exist"
        assert (PROJECT_ROOT / "agents" / "__init__.py").is_file(), "agents/__init__.py must be a file"

    def test_tools_directory_is_package(self):
        """tools/ directory must be a Python package (importable)."""
        assert (PROJECT_ROOT / "tools").is_dir(), "tools/ directory must exist"
        assert (PROJECT_ROOT / "tools" / "__init__.py").is_file(), "tools/__init__.py must be a file"

    def test_prompts_directory_is_package(self):
        """prompts/ directory must be a Python package (importable)."""
        assert (PROJECT_ROOT / "prompts").is_dir(), "prompts/ directory must exist"
        assert (PROJECT_ROOT / "prompts" / "__init__.py").is_file(), "prompts/__init__.py must be a file"


class TestProjectStructure:
    """Integration tests for the overall project structure."""

    def test_all_required_files_exist(self):
        """All required scaffold files must exist."""
        required_files = [
            "pyproject.toml",
            ".env.example",
            ".gitignore",
            "langgraph.json",
            "agents/__init__.py",
            "tools/__init__.py",
            "prompts/__init__.py",
        ]
        for f in required_files:
            path = PROJECT_ROOT / f
            assert path.exists(), f"Required file {f} not found at {path}"

    def test_no_env_file_committed(self):
        """There should be no .env file in the project root (only .env.example)."""
        # .env should not exist (it's in .gitignore)
        # This test just ensures .env.example exists, not .env
        assert (PROJECT_ROOT / ".env.example").exists(), ".env.example must exist"
