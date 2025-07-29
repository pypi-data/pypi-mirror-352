"""
MCP Feedback Collector Web界面模块

基于Flask的Web界面，提供远程访问支持
"""

from .app import create_app, WebInterface

__all__ = ["create_app", "WebInterface"]
