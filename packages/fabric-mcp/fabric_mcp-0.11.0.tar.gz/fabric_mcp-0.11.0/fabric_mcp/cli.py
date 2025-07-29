"""CLI entry point for fabric-mcp."""

import click

from fabric_mcp import __version__

from .core import FabricMCP
from .utils import Log


@click.command()
@click.option(
    "--stdio",
    is_flag=True,
    help="Run the server in stdio mode (default).",
)
@click.option(
    "--http-streamable",
    is_flag=True,
    help="Run the server with streamable HTTP transport.",
)
@click.option(
    "--host",
    default="127.0.0.1",
    help="Host to bind the HTTP server to (default: 127.0.0.1).",
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="Port to bind the HTTP server to (default: 8000).",
)
@click.option(
    "--mcp-path",
    default="/mcp",
    help="MCP endpoint path (default: /mcp).",
)
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
    default="info",
    help="Set the logging level (default: info)",
)
@click.version_option(version=__version__, prog_name="fabric-mcp")
def main(
    stdio: bool,
    http_streamable: bool,
    host: str,
    port: int,
    mcp_path: str,
    log_level: str,
) -> None:
    """A Model Context Protocol server for Fabric AI."""

    # Ensure exactly one transport option is selected
    if stdio and http_streamable:
        click.echo(
            "Error: --stdio and --http-streamable are mutually exclusive.", err=True
        )
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit(1)

    if not stdio and not http_streamable:
        # Show help if no transport is specified
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit(0)

    log = Log(log_level)
    logger = log.logger

    fabric_mcp = FabricMCP(log_level)

    if stdio:
        logger.info(
            "Starting server with stdio transport (log level: %s)", log.level_name
        )
        fabric_mcp.stdio()
        logger.info("Server stopped.")
    elif http_streamable:
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
