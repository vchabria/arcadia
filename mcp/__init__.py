"""
MCP (Model Context Protocol) adapter layer

Thin wrapper around core business logic to expose via MCP protocol.
No business logic should exist here - only protocol handling.
"""

from .server import app

__all__ = ["app"]

