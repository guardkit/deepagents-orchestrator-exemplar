"""verify_output re-export shim.

Provides ``from tools.verify_output import verify_output`` compatibility
with the smoke-test import paths defined in the project specification.
"""

from tools.orchestrator_tools import verify_output

__all__ = ["verify_output"]
