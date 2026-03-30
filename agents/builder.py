"""Builder re-export shim.

Provides ``from agents.builder import builder_async_subagent`` compatibility
with the smoke-test import paths defined in the project specification.
"""

from agents.agents import builder_async_subagent

__all__ = ["builder_async_subagent"]
