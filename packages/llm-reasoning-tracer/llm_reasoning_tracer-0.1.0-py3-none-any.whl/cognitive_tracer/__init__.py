"""
LLM Reasoning Tracer

This package provides a lightweight LangChain callback handler that traces
intermediate reasoning steps, tool usage, and outputs during LLM agent execution.
"""

from .tracer import CognitiveTracer

__all__ = ["CognitiveTracer"]
__version__ = "0.1.0"
