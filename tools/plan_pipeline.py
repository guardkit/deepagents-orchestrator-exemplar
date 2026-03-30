"""plan_pipeline re-export shim.

Provides ``from tools.plan_pipeline import plan_pipeline`` compatibility
with the smoke-test import paths defined in the project specification.
"""

from tools.orchestrator_tools import plan_pipeline

__all__ = ["plan_pipeline"]
