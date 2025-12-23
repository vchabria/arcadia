"""
Python SDK for inbound order automation

Provides a clean, agent-safe interface for direct Python usage.
No MCP, FastAPI, or HTTP dependencies.
"""

from .client import InboundOrderClient

__all__ = ["InboundOrderClient"]

