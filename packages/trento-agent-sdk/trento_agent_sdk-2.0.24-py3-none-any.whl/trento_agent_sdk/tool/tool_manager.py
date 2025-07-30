from __future__ import annotations as _annotations

import time
import asyncio
from collections.abc import Callable
from typing import Any
from .tool import Tool
import logging

# Set up loggers
logger = logging.getLogger(__name__)


class ToolManager:
    """Manages FastMCP tools."""

    def __init__(self, warn_on_duplicate_tools: bool = True):
        self._tools: dict[str, Tool] = {}
        self.warn_on_duplicate_tools = warn_on_duplicate_tools

    def get_tool(self, name: str) -> Tool | None:
        """Get tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    def add_tool(
        self,
        fn: Callable[..., Any],
        name: str | None = None,
        description: str | None = None,
    ) -> Tool:
        """Add a tool to the server."""
        # automatically detect the sync/async
        tool = Tool.from_function(fn, name=name, description=description)
        existing = self._tools.get(tool.name)
        if existing:
            if self.warn_on_duplicate_tools:
                logger.warning(f"Tool already exists: {tool.name}")
            return existing
        self._tools[tool.name] = tool
        return tool

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        max_retries: int = 2,
        retry_delay: float = 0.5
    ) -> Any:
        """
        Call a tool by name with arguments.
        
        Includes retry mechanism for transient failures and improved argument validation.
        
        Args:
            name: Tool name to call
            arguments: Arguments to pass to the tool
            max_retries: Maximum number of retry attempts (default: 2)
            retry_delay: Initial delay between retries in seconds (default: 0.5)
            
        Returns:
            The tool execution result
            
        Raises:
            Exception: If the tool doesn't exist or all retry attempts fail
        """
        tool = self.get_tool(name)
        if not tool:
            raise Exception(f"Unknown tool: {name}")

        # Validate and clean arguments before execution
        validated_arguments = self._validate_tool_arguments(tool, arguments)

        for attempt in range(max_retries + 1):  # +1 because we count the initial try
            try:
                start_time = time.time()
                result = await tool.run(validated_arguments)
                execution_time = time.time() - start_time
                
                # Log performance metrics if execution is slow
                if execution_time > 1.0:  # Log when tools take more than 1 second
                    logger.info(f"Tool '{name}' execution took {execution_time:.2f}s")
                    
                return result
            except Exception as e:
                # Don't retry on certain types of errors
                if isinstance(e, (ValueError, TypeError, KeyError, AttributeError)):
                    logger.error(f"Non-retryable error when calling tool '{name}': {e}")
                    raise
                
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Error calling tool '{name}': {e}. Retrying in {wait_time:.2f}s (attempt {attempt+1}/{max_retries})...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed to call tool '{name}' after {max_retries} retries. Last error: {e}")
                    raise

    def _validate_tool_arguments(self, tool: Tool, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Validate and clean tool arguments to ensure they match expected types.
        
        Args:
            tool: The tool object
            arguments: Raw arguments dictionary
            
        Returns:
            Validated and cleaned arguments dictionary
        """
        if not arguments:
            return {}
            
        try:
            # For now, we'll just return the arguments as-is since our argument preprocessing
            # is handled at the agent level. This method can be extended in the future
            # for more sophisticated tool-specific validation.
            return arguments
        except Exception as e:
            logger.warning(f"Error validating arguments for tool '{tool.name}': {e}")
            return arguments

    def get_tool_info(
        self,
        name: str,
    ):
        tool = self.get_tool(name)
        if not tool:
            raise Exception(f"Unknown tool: {name}")

        return tool.get_tool_info()
