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
    "-l",
    "--log-level",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
    default="info",
    help="Set the logging level (default: info)",
)
@click.version_option(version=__version__, prog_name="fabric-mcp")
def main(stdio: bool, log_level: str) -> None:
    """A Model Context Protocol server for Fabric AI."""

    # If --stdio is not provided, show help and exit non-zero
    if not stdio:
        ctx = click.get_current_context()
        click.echo(ctx.get_help(), err=True)
        ctx.exit(1)

    log = Log(log_level)
    logger = log.logger

    # Add main logic based on args here
    if stdio:
        logger.info("Starting server with log level %s", log.level_name)
        fabric_mcp = FabricMCP()
        fabric_mcp.stdio()
        logger.info("Server stopped.")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
