"""Core MCP server implementation using the Model Context Protocol."""

import logging
from asyncio.exceptions import CancelledError
from collections.abc import Callable
from typing import Any

from anyio import WouldBlock
from fastmcp import FastMCP

from . import __version__


class FabricMCP(FastMCP[None]):
    """Base class for the Model Context Protocol server."""

    def __init__(self, log_level: str = "INFO"):
        """Initialize the MCP server with a model."""
        super().__init__(f"Fabric MCP v{__version__}")
        self.mcp = self
        self.logger = logging.getLogger(__name__)
        self.__tools: list[Callable[..., Any]] = []
        self.log_level = log_level

        @self.tool()
        def fabric_list_patterns() -> list[str]:
            """Return a list of available fabric patterns."""
            # This is a placeholder for the actual implementation
            return ["pattern1", "pattern2", "pattern3"]

        self.__tools.append(fabric_list_patterns)

        @self.tool()
        def fabric_get_pattern_details(pattern_name: str) -> dict[Any, Any]:
            """Retrieve detailed information for a specific Fabric pattern."""
            # This is a placeholder for the actual implementation
            return {
                "name": pattern_name,
                "description": "Pattern description here",
                "system_prompt": "System prompt here",
                "user_prompt_template": "User prompt template here",
                "tags": ["tag1", "tag2"],
            }

        self.__tools.append(fabric_get_pattern_details)

        @self.tool()
        def fabric_run_pattern(
            pattern_name: str,
            input_text: str = "",
            stream: bool = False,
            model_name: str | None = None,
            strategy_name: str | None = None,
            variables: dict[str, str] | None = None,
            attachments: list[str] | None = None,
            temperature: float | None = None,
            top_p: float | None = None,
            presence_penalty: float | None = None,
            frequency_penalty: float | None = None,
        ) -> dict[Any, Any]:
            """
            Execute a Fabric pattern with options and optional streaming.

            Args:
                pattern_name: The name of the fabric pattern to run.
                input_text: The input text to be processed by the pattern.
                stream: Whether to stream the output.
                model_name: Optional model name to use.
                strategy_name: Optional strategy name to use.
                variables: Optional variables for the pattern.
                attachments: Optional file paths/URLs.
                temperature: Optional temperature parameter.
                top_p: Optional top_p parameter.
                presence_penalty: Optional presence_penalty parameter.
                frequency_penalty: Optional frequency_penalty parameter.

            Returns:
                dict[Any, Any]: Contains the output format and text.
            """
            # This is a placeholder for the actual implementation
            # Use parameters to avoid unused warnings
            _ = (
                stream,
                model_name,
                strategy_name,
                variables,
                attachments,
                temperature,
                top_p,
                presence_penalty,
                frequency_penalty,
            )

            return {
                "output_format": "markdown",
                "output_text": (
                    f"Pattern {pattern_name} executed with input: {input_text}"
                ),
            }

        self.__tools.append(fabric_run_pattern)

        @self.tool()
        def fabric_list_models() -> dict[Any, Any]:
            """Retrieve configured Fabric models by vendor."""
            # This is a placeholder for the actual implementation
            return {
                "all_models": ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"],
                "models_by_vendor": {
                    "openai": ["gpt-4", "gpt-3.5-turbo"],
                    "anthropic": ["claude-3-opus"],
                },
            }

        self.__tools.append(fabric_list_models)

        @self.tool()
        def fabric_list_strategies() -> dict[Any, Any]:
            """Retrieve available Fabric strategies."""
            # This is a placeholder for the actual implementation
            return {
                "strategies": [
                    {
                        "name": "default",
                        "description": "Default strategy for pattern execution",
                        "prompt": "Execute the pattern with default settings",
                    },
                    {
                        "name": "creative",
                        "description": "Creative strategy with higher temperature",
                        "prompt": "Execute the pattern with creative parameters",
                    },
                ]
            }

        self.__tools.append(fabric_list_strategies)

        @self.tool()
        def fabric_get_configuration() -> dict[Any, Any]:
            """Retrieve Fabric configuration with sensitive values redacted."""
            # This is a placeholder for the actual implementation
            return {
                "openai_api_key": "[REDACTED_BY_MCP_SERVER]",
                "ollama_url": "http://localhost:11434",
                "anthropic_api_key": "[REDACTED_BY_MCP_SERVER]",
                "fabric_config_dir": "~/.config/fabric",
            }

        self.__tools.append(fabric_get_configuration)

    def stdio(self):
        """Run the MCP server."""
        try:
            self.mcp.run()
        except (KeyboardInterrupt, CancelledError, WouldBlock):
            # Handle graceful shutdown
            self.logger.info("Server stopped by user.")
