"""Additional unit tests for fabric_mcp.cli module."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from fabric_mcp import __version__
from fabric_mcp.cli import main


class TestCLIMain:
    """Test cases for the main CLI function."""

    def test_version_flag(self):
        """Test --version flag displays version and exits."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        # Click version option exits with code 0
        assert result.exit_code == 0

        # Check that version was printed to output
        assert f"fabric-mcp, version {__version__}" in result.output

    def test_help_flag(self):
        """Test --help flag displays help and exits."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        # Click help option exits with code 0
        assert result.exit_code == 0

        # Check that help was printed
        assert "A Model Context Protocol server for Fabric AI" in result.output
        assert "--stdio" in result.output
        assert "--log-level" in result.output

    def test_no_args_shows_help_and_exits(self):
        """Test that running with no arguments shows help and exits with error."""
        runner = CliRunner()
        result = runner.invoke(main, [])

        # Should exit with error code
        assert result.exit_code == 1

        # Check that help was printed to stderr (captured in output by CliRunner)
        assert "A Model Context Protocol server for Fabric AI" in result.output

    def test_only_log_level_without_stdio_shows_help(self):
        """Test that only --log-level without --stdio shows help."""
        runner = CliRunner()
        result = runner.invoke(main, ["--log-level", "debug"])

        assert result.exit_code == 1
        assert "A Model Context Protocol server for Fabric AI" in result.output

    @patch("fabric_mcp.cli.FabricMCP")
    @patch("fabric_mcp.cli.Log")
    def test_stdio_flag_creates_server_and_runs(
        self, mock_log_class: Mock, mock_fabric_mcp_class: Mock
    ):
        """Test that --stdio flag creates server and runs it."""
        # Setup mocks
        mock_log = Mock()
        mock_log.level_name = "INFO"
        mock_log.logger = Mock()
        mock_log_class.return_value = mock_log

        mock_server = Mock()
        mock_fabric_mcp_class.return_value = mock_server

        runner = CliRunner()
        result = runner.invoke(main, ["--stdio"])

        # Should exit successfully
        assert result.exit_code == 0

        # Verify Log was created with correct level
        mock_log_class.assert_called_once_with("info")

        # Verify FabricMCP was created
        mock_fabric_mcp_class.assert_called_once()

        # Verify stdio() was called
        mock_server.stdio.assert_called_once()

    @patch("fabric_mcp.cli.FabricMCP")
    @patch("fabric_mcp.cli.Log")
    def test_stdio_with_custom_log_level(
        self, mock_log_class: Mock, mock_fabric_mcp_class: Mock
    ):
        """Test --stdio with custom log level."""
        mock_log = Mock()
        mock_log.level_name = "DEBUG"
        mock_log.logger = Mock()
        mock_log_class.return_value = mock_log

        mock_server = Mock()
        mock_fabric_mcp_class.return_value = mock_server

        runner = CliRunner()
        result = runner.invoke(main, ["--stdio", "--log-level", "debug"])

        assert result.exit_code == 0

        # Verify Log was created with debug level
        mock_log_class.assert_called_once_with("debug")

        # Verify FabricMCP was created
        mock_fabric_mcp_class.assert_called_once()

    @patch("fabric_mcp.cli.FabricMCP")
    @patch("fabric_mcp.cli.Log")
    def test_stdio_with_short_log_level_flag(
        self, mock_log_class: Mock, mock_fabric_mcp_class: Mock
    ):
        """Test --stdio with short form -l for log level."""
        mock_log = Mock()
        mock_log.level_name = "ERROR"
        mock_log.logger = Mock()
        mock_log_class.return_value = mock_log

        mock_server = Mock()
        mock_fabric_mcp_class.return_value = mock_server

        runner = CliRunner()
        result = runner.invoke(main, ["--stdio", "-l", "error"])

        assert result.exit_code == 0
        mock_log_class.assert_called_once_with("error")
        mock_fabric_mcp_class.assert_called_once()

    @patch("fabric_mcp.cli.FabricMCP")
    @patch("fabric_mcp.cli.Log")
    def test_stdio_logs_startup_and_shutdown_messages(
        self, mock_log_class: Mock, mock_fabric_mcp_class: Mock
    ):
        """Test that appropriate log messages are generated."""
        mock_log = Mock()
        mock_log.level_name = "INFO"
        mock_logger = Mock()
        mock_log.logger = mock_logger
        mock_log_class.return_value = mock_log

        mock_server = Mock()
        mock_fabric_mcp_class.return_value = mock_server

        runner = CliRunner()
        result = runner.invoke(main, ["--stdio"])

        assert result.exit_code == 0

        # Check that startup message was logged
        startup_calls = [
            call
            for call in mock_logger.info.call_args_list
            if "Starting server" in str(call)
        ]
        assert len(startup_calls) == 1
        assert "Starting server with log level" in str(startup_calls[0])
        assert "'INFO'" in str(startup_calls[0])

        # Check that shutdown message was logged
        shutdown_calls = [
            call
            for call in mock_logger.info.call_args_list
            if "Server stopped" in str(call)
        ]
        assert len(shutdown_calls) == 1

    def test_log_level_choices(self):
        """Test that valid log levels are accepted and invalid ones are rejected."""
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        runner = CliRunner()

        for level in valid_levels:
            with patch("fabric_mcp.cli.FabricMCP"):
                with patch("fabric_mcp.cli.Log"):
                    result = runner.invoke(main, ["--stdio", "--log-level", level])
                    # Should not raise an exception and exit successfully
                    assert result.exit_code == 0

        # Test invalid log level
        result = runner.invoke(main, ["--stdio", "--log-level", "invalid"])
        # Click should exit with error for invalid choice
        assert result.exit_code != 0

    def test_default_log_level_is_info(self):
        """Test that default log level is 'info'."""
        with (
            patch("fabric_mcp.cli.Log") as mock_log_class,
            patch("fabric_mcp.cli.FabricMCP") as mock_fabric_mcp_class,
        ):
            mock_log = Mock()
            mock_log.level_name = "INFO"
            mock_log.logger = Mock()
            mock_log_class.return_value = mock_log

            mock_fabric_mcp = Mock()
            mock_fabric_mcp_class.return_value = mock_fabric_mcp

            runner = CliRunner()
            result = runner.invoke(main, ["--stdio"])

            assert result.exit_code == 0

            # Verify default log level was used
            mock_log_class.assert_called_once_with("info")
