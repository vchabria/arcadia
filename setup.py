"""
Setup script for inbound-order-automation

This allows the package to be installed via pip:
    pip install .                    # SDK only (no MCP server)
    pip install .[mcp]               # SDK + MCP server
    pip install .[full]              # Everything including NovaAct
    pip install .[dev]               # Development dependencies
"""

from setuptools import setup

# Configuration is in pyproject.toml
setup()

