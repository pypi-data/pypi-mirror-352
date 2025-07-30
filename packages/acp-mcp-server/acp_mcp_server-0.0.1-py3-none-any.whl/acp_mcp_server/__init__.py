# acp_mcp_server/__init__.py
"""
ACP-MCP Bridge Server

A bridge server that connects Agent Communication Protocol (ACP) agents
with Model Context Protocol (MCP) clients.

Supports multiple transport modes:
- STDIO (default, for Claude Desktop)
- SSE (Server-Sent Events)
- Streamable HTTP
"""

from .server import ACPMCPServer, main

__version__ = "2.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = ["ACPMCPServer", "main"]
