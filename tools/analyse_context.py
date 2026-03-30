"""analyse_context re-export shim.

Provides ``from tools.analyse_context import analyse_context`` compatibility
with the smoke-test import paths defined in the project specification.
"""

from tools.orchestrator_tools import analyse_context

__all__ = ["analyse_context"]
