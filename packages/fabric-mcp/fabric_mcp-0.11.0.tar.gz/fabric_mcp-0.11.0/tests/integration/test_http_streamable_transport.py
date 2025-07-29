"""Integration tests for the Fabric MCP Server HTTP Streamable Transport.

These tests verify the HTTP streamable transport functionality,
including all MCP tools over HTTP and configuration options.
"""

import asyncio
import os
import socket
import subprocess
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import httpx
import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# Type aliases for better readability
ServerConfig = dict[str, Any]
ToolResponse = dict[str, Any]


def find_free_port() -> int:
    """Find a free port to use for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@pytest.mark.integration
class TestHTTPStreamableTransport:
    """Integration tests for HTTP Streamable Transport."""

    @pytest.fixture
    def http_server_config(self) -> ServerConfig:
        """Configuration for the HTTP server."""
        return {
            "host": "127.0.0.1",
            "port": find_free_port(),  # Use dynamic port allocation
            "mcp_path": "/mcp",
        }

    @asynccontextmanager
    async def run_http_server(
        self, config: ServerConfig
    ) -> AsyncGenerator[ServerConfig, None]:
        """Context manager to run HTTP server during tests."""
        # Start server as subprocess for proper isolation
        server_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "fabric_mcp.cli",
                "--http-streamable",
                "--host",
                config["host"],
                "--port",
                str(config["port"]),
                "--mcp-path",
                config["mcp_path"],
                "--log-level",
                "info",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Wait for server to start with timeout
            server_url = (
                f"http://{config['host']}:{config['port']}{config['mcp_path']}/"
            )
            for _ in range(30):  # 3 second timeout
                try:
                    async with httpx.AsyncClient() as client:
                        await client.get(server_url, timeout=0.5)
                        break  # Server is responding
                except (httpx.ConnectError, httpx.TimeoutException) as exc:
                    # Check if process is still alive
                    if server_process.poll() is not None:
                        stdout, stderr = server_process.communicate()
                        raise RuntimeError(
                            f"Server process died: stdout={stdout}, stderr={stderr}"
                        ) from exc
                    await asyncio.sleep(0.1)
            else:
                # Server failed to start, get logs
                server_process.terminate()
                stdout, stderr = server_process.communicate(timeout=5)
                raise RuntimeError(
                    f"Server failed to start on {config['host']}:{config['port']}\n"
                    f"stdout: {stdout}\nstderr: {stderr}"
                )

            yield config

        finally:
            # Clean up server process
            if server_process.poll() is None:
                # Try graceful shutdown first
                server_process.terminate()
                try:
                    server_process.wait(timeout=3.0)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    server_process.kill()
                    server_process.wait(timeout=1.0)

    @pytest.mark.asyncio
    async def test_http_server_starts_and_responds(
        self, http_server_config: ServerConfig
    ) -> None:
        """Test that HTTP server starts and responds to basic requests."""
        async with self.run_http_server(http_server_config) as config:
            # Test basic connectivity
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}/"

            async with httpx.AsyncClient() as client:
                # Should get MCP protocol response (not simple HTTP response)
                response = await client.get(url)
                # Expect 406 since we're not using proper MCP headers
                assert response.status_code == 406
                assert "text/event-stream" in response.json()["error"]["message"]

    @pytest.mark.asyncio
    async def test_mcp_client_connection(
        self, http_server_config: ServerConfig
    ) -> None:
        """Test MCP client can connect and list tools."""
        async with self.run_http_server(http_server_config) as config:
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}"

            # Create MCP client with HTTP transport
            transport = StreamableHttpTransport(url=url)
            client = Client(transport)

            async with client:
                # Test list_tools
                tools = await client.list_tools()
                assert tools is not None
                assert isinstance(tools, list)

                # Verify expected tools are present
                tool_names: list[str] = [
                    tool.name
                    for tool in tools  # type: ignore[misc]
                ]
                expected_tools = [
                    "fabric_list_patterns",
                    "fabric_get_pattern_details",
                    "fabric_run_pattern",
                    "fabric_list_models",
                    "fabric_list_strategies",
                    "fabric_get_configuration",
                ]

                for expected_tool in expected_tools:
                    assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_fabric_list_patterns_over_http(
        self, http_server_config: ServerConfig
    ) -> None:
        """Test fabric_list_patterns tool over HTTP."""
        async with self.run_http_server(http_server_config) as config:
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}"

            transport = StreamableHttpTransport(url=url)
            client = Client(transport)

            async with client:
                result = await client.call_tool("fabric_list_patterns")
                assert result is not None
                assert isinstance(result, list)
                # Should return list of patterns (currently hardcoded)
                patterns_text = result[0].text  # type: ignore[misc]
                assert isinstance(patterns_text, str)
                assert len(patterns_text) > 0

    @pytest.mark.asyncio
    async def test_fabric_get_pattern_details_over_http(
        self, http_server_config: ServerConfig
    ) -> None:
        """Test fabric_get_pattern_details tool over HTTP."""
        async with self.run_http_server(http_server_config) as config:
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}"

            transport = StreamableHttpTransport(url=url)
            client = Client(transport)

            async with client:
                result = await client.call_tool(
                    "fabric_get_pattern_details", {"pattern_name": "test_pattern"}
                )
                assert result is not None
                assert isinstance(result, list)

                details_text = result[0].text  # type: ignore[misc]
                assert isinstance(details_text, str)
                # The tool returns JSON string, we could parse it to validate structure
                assert "name" in details_text or "description" in details_text

    @pytest.mark.asyncio
    async def test_fabric_run_pattern_over_http(
        self, http_server_config: ServerConfig
    ) -> None:
        """Test fabric_run_pattern tool over HTTP (non-streaming)."""
        async with self.run_http_server(http_server_config) as config:
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}"

            transport = StreamableHttpTransport(url=url)
            client = Client(transport)

            async with client:
                result = await client.call_tool(
                    "fabric_run_pattern",
                    {
                        "pattern_name": "test_pattern",
                        "input_text": "test input",
                        "stream": False,
                    },
                )
                assert result is not None
                assert isinstance(result, list)

                output_text = result[0].text  # type: ignore[misc]
                assert isinstance(output_text, str)
                assert len(output_text) > 0

    @pytest.mark.asyncio
    async def test_fabric_run_pattern_streaming_over_http(
        self, http_server_config: ServerConfig
    ) -> None:
        """Test fabric_run_pattern tool over HTTP with streaming."""
        async with self.run_http_server(http_server_config) as config:
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}"

            transport = StreamableHttpTransport(url=url)
            client = Client(transport)

            async with client:
                result = await client.call_tool(
                    "fabric_run_pattern",
                    {
                        "pattern_name": "test_pattern",
                        "input_text": "test input",
                        "stream": True,
                    },
                )
                assert result is not None
                assert isinstance(result, list)

                output_text = result[0].text  # type: ignore[misc]
                assert isinstance(output_text, str)
                assert len(output_text) > 0

    @pytest.mark.asyncio
    async def test_fabric_list_models_over_http(
        self, http_server_config: ServerConfig
    ) -> None:
        """Test fabric_list_models tool over HTTP."""
        async with self.run_http_server(http_server_config) as config:
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}"

            transport = StreamableHttpTransport(url=url)
            client = Client(transport)

            async with client:
                result = await client.call_tool("fabric_list_models")
                assert result is not None
                assert isinstance(result, list)

                models_text = result[0].text  # type: ignore[misc]
                assert isinstance(models_text, str)
                assert len(models_text) > 0

    @pytest.mark.asyncio
    async def test_fabric_list_strategies_over_http(
        self, http_server_config: ServerConfig
    ) -> None:
        """Test fabric_list_strategies tool over HTTP."""
        async with self.run_http_server(http_server_config) as config:
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}"

            transport = StreamableHttpTransport(url=url)
            client = Client(transport)

            async with client:
                result = await client.call_tool("fabric_list_strategies")
                assert result is not None
                assert isinstance(result, list)

                strategies_text = result[0].text  # type: ignore[misc]
                assert isinstance(strategies_text, str)
                assert len(strategies_text) > 0

    @pytest.mark.asyncio
    async def test_fabric_get_configuration_over_http(
        self, http_server_config: ServerConfig
    ) -> None:
        """Test fabric_get_configuration tool over HTTP."""
        async with self.run_http_server(http_server_config) as config:
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}"

            transport = StreamableHttpTransport(url=url)
            client = Client(transport)

            async with client:
                result = await client.call_tool("fabric_get_configuration")
                assert result is not None
                assert isinstance(result, list)

                config_text = result[0].text  # type: ignore[misc]
                assert isinstance(config_text, str)
                # Should have redacted sensitive values
                assert "[REDACTED_BY_MCP_SERVER]" in config_text

    @pytest.mark.asyncio
    async def test_custom_host_port_path_configuration(self) -> None:
        """Test server with custom host, port, and path configuration."""
        custom_config: ServerConfig = {
            "host": "127.0.0.1",
            "port": find_free_port(),
            "mcp_path": "/custom-path",
        }

        async with self.run_http_server(custom_config) as config:
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}"

            transport = StreamableHttpTransport(url=url)
            client = Client(transport)

            async with client:
                tools = await client.list_tools()
                assert tools is not None
                assert isinstance(tools, list)

    @pytest.mark.asyncio
    async def test_mcp_error_handling_over_http(
        self, http_server_config: ServerConfig
    ) -> None:
        """Test MCP error handling over HTTP."""
        async with self.run_http_server(http_server_config) as config:
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}"

            transport = StreamableHttpTransport(url=url)
            client = Client(transport)

            async with client:
                # Test calling non-existent tool
                with pytest.raises(Exception):  # Should raise MCP error
                    await client.call_tool("non_existent_tool")

    @pytest.mark.asyncio
    async def test_concurrent_http_requests(
        self, http_server_config: ServerConfig
    ) -> None:
        """Test handling multiple concurrent HTTP requests."""
        async with self.run_http_server(http_server_config) as config:
            url = f"http://{config['host']}:{config['port']}{config['mcp_path']}"

            transport = StreamableHttpTransport(url=url)
            client = Client(transport)

            async with client:
                # Make multiple concurrent requests
                tasks: list[Any] = []
                for _ in range(5):
                    task = asyncio.create_task(client.call_tool("fabric_list_patterns"))
                    tasks.append(task)

                results: list[list[Any]] = await asyncio.gather(*tasks)

                # All requests should succeed
                for result in results:
                    assert result is not None
                    assert isinstance(result, list)
                    assert len(result) > 0
                    # Check that the first item has the expected content format
                    first_item = result[0]
                    assert hasattr(first_item, "text") or hasattr(first_item, "type")


@pytest.mark.integration
class TestHTTPStreamableTransportCLI:
    """Integration tests for CLI with HTTP Streamable Transport."""

    def test_cli_http_streamable_help(self) -> None:
        """Test CLI shows HTTP streamable options in help."""
        result = subprocess.run(
            [sys.executable, "-m", "fabric_mcp.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            check=False,
        )

        assert result.returncode == 0
        assert "--http-streamable" in result.stdout
        assert "--host" in result.stdout
        assert "--port" in result.stdout
        assert "--mcp-path" in result.stdout

    def test_cli_mutual_exclusion_stdio_http(self) -> None:
        """Test CLI rejects both --stdio and --http-streamable."""
        result = subprocess.run(
            [sys.executable, "-m", "fabric_mcp.cli", "--stdio", "--http-streamable"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            check=False,
        )

        assert result.returncode == 1
        assert "mutually exclusive" in result.stderr.lower()
