"""Implementer re-export shim.

Provides ``from agents.implementer import implementer_subagent`` compatibility
with the smoke-test import paths defined in the project specification.
"""

from agents.agents import implementer_subagent

__all__ = ["implementer_subagent"]
