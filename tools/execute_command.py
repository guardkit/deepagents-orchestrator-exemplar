"""execute_command re-export shim.

Provides ``from tools.execute_command import execute_command`` compatibility
with the smoke-test import paths defined in the project specification.
"""

from tools.orchestrator_tools import execute_command

__all__ = ["execute_command"]
