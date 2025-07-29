"""CLI entry point for fabric-mcp."""

from typing import Any

import click

from fabric_mcp import __version__

from .core import FabricMCP
from .utils import Log


def validate_http_options(
    ctx: click.Context, param: click.Parameter, value: Any
) -> Any:
    """Validate that HTTP-specific options are only used with HTTP transport."""
    transport = ctx.params.get("transport")
    if (
        transport != "http"
        and param.name is not None
        and ctx.get_parameter_source(param.name)
        == click.core.ParameterSource.COMMANDLINE
    ):
        raise click.UsageError(f"{param.opts[0]} is only valid with --transport http")
    return value


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    required=True,
    help="Transport mechanism to use for the MCP server.",
)
@click.option(
    "--host",
    default="127.0.0.1",
    show_default=True,
    callback=validate_http_options,
    help="Host to bind the HTTP server to (HTTP transport only).",
)
@click.option(
    "--port",
    default=8000,
    type=int,
    show_default=True,
    callback=validate_http_options,
    help="Port to bind the HTTP server to (HTTP transport only).",
)
@click.option(
    "--mcp-path",
    default="/mcp",
    show_default=True,
    callback=validate_http_options,
    help="MCP endpoint path (HTTP transport only).",
)
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
    default="info",
    show_default=True,
    help="Set the logging level.",
)
@click.version_option(version=__version__, prog_name="fabric-mcp")
def main(
    transport: str,
    host: str,
    port: int,
    mcp_path: str,
    log_level: str,
) -> None:
    """A Model Context Protocol server for Fabric AI."""

    log = Log(log_level)
    logger = log.logger

    fabric_mcp = FabricMCP(log_level)

    if transport == "stdio":
        logger.info(
            "Starting server with stdio transport (log level: %s)", log.level_name
        )
        fabric_mcp.stdio()
        logger.info("Server stopped.")
    elif transport == "http":
        logger.info(
            "Starting server with streamable HTTP transport at "
            "http://%s:%d%s (log level: %s)",
            host,
            port,
            mcp_path,
            log.level_name,
        )
        fabric_mcp.http_streamable(host=host, port=port, mcp_path=mcp_path)
        logger.info("Server stopped.")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
