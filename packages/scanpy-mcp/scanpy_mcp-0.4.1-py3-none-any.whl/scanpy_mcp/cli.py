"""
Command-line interface for scanpy-mcp.

This module provides a CLI entry point for the scanpy-mcp package.
"""

from scmcp_shared.cli import MCPCLI
from .server import ScanpyMCPManager

cli = MCPCLI(
    name="scanpy-mcp", 
    help_text="Scanpy MCP Server CLI",
    manager=ScanpyMCPManager
)
