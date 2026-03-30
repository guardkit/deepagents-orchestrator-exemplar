"""Orchestrator re-export shim.

Provides ``from agents.orchestrator import create_orchestrator`` compatibility
with the smoke-test import paths defined in the project specification.
"""

from agents.agents import create_orchestrator

__all__ = ["create_orchestrator"]
