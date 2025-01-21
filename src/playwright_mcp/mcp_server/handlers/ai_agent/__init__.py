"""AI agent module for Playwright MCP.

This module provides an AI agent that can analyze and interact with web pages
using natural language commands. It uses Pydantic AI for tool definitions
and Anthropic's Claude model for decision making.
"""

from .handler import handle_ai_agent

__all__ = ['handle_ai_agent'] 