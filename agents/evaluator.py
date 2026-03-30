"""Evaluator re-export shim.

Provides ``from agents.evaluator import evaluator_subagent`` compatibility
with the smoke-test import paths defined in the project specification.
"""

from agents.agents import evaluator_subagent

__all__ = ["evaluator_subagent"]
