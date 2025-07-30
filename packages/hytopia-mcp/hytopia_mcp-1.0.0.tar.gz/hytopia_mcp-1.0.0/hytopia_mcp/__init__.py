"""
HYTOPIA MCP Server - Optimized for Claude Code Development

This MCP server provides intelligent tools for navigating and understanding the HYTOPIA SDK,
making it easier for Claude Code to assist with game development.
"""

__version__ = "1.0.0"
__author__ = "HYTOPIA MCP Team"

from .server import create_server

__all__ = ["create_server"]