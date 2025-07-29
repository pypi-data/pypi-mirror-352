"""
MCP Feedback Collector v3.2.0 - Interactive user feedback collection and AI chat for MCP servers.

This package provides a modern dual-function system for Model Context Protocol (MCP)
servers, featuring AI work report feedback collection and AI intelligent chat functionality.
Built with PyQt6 GUI and Flask Web interfaces, supporting both local and remote deployments.
"""

__version__ = "3.2.0"
__author__ = "MCP Feedback Collector Team"
__email__ = "feedback@example.com"
__description__ = "A modern MCP server with dual interface: GUI and Web support"
__license__ = "MIT"

# 保持向后兼容
from .server import main

__all__ = ["main"]