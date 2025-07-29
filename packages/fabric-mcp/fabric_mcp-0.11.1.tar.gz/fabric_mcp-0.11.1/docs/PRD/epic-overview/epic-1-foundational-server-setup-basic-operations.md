# Epic 1: Foundational Server Setup & Basic Operations

- **Goal:** Establish a runnable Fabric MCP server with essential CLI capabilities (including the planned refactor to `click`), basic MCP communication (tool discovery), connectivity to a configured Fabric instance, core server configuration handling, packaging, and support for stdio, Streamable HTTP, and SSE transport layers. This provides the installable and operable foundation for all subsequent features.
- **Stories:**
  - **Story 1.1: Verify and Document Existing Project Scaffolding**
    - User Story: As a Project Maintainer, I want to verify and document the existing project scaffolding (Python environment, `uv` setup, `pyproject.toml`, basic source layout, development tooling including `pre-commit` and MCP Inspector setup) so that it serves as a stable and understood base for further development.
    - Acceptance Criteria:
            1. The `pyproject.toml` file accurately defines project metadata (name, dynamic version, description, authors, license).
            2. The `pyproject.toml` specifies `requires-python = ">=3.11"`.
            3. Core development dependencies (`hatch`, `ruff`, `pytest`, `uv`, `pre-commit`) are correctly listed.
            4. `make bootstrap` successfully sets up/validates the dev environment and pre-commit hooks.
            5. Source code directory structure (`src/fabric_mcp/`, `tests/`) is confirmed.
            6. `Makefile` provides functional targets: `bootstrap`, `format`, `lint`, `test`, `coverage`, `build`, `dev`.
            7. A new file, `docs/contributing-cheatsheet.md`, is created and populated with a summary of the verified project setup, including Python version, key development tools (`uv`, `ruff`, `pytest`, `hatch`, `pre-commit`, `pnpm` for MCP Inspector), and essential `make` commands, highlighting automated updates and MCP Inspector usage.
            8. The main `README.md` is updated to link to `docs/contributing-cheatsheet.md` and `docs/contributing-cheatsheet.md`.
            9. The `.pre-commit-config.yaml` is implemented and configured for conventional commits and branch protection.
  - **Story 1.2: Implement Core CLI with `click` (Refactor from `argparse`)**
    - User Story: As a Server Operator, I want the Fabric MCP Server to have a CLI built with `click` so that command-line interactions are user-friendly, well-documented, and extensible.
    - Acceptance Criteria:
            1. CLI entry point (`fabric_mcp.cli:main`) refactored to use `click`.
            2. Supports commandline flag for stdio mode.
            3. Supports `--log-level` (and short form `-l`) with choices and default `INFO`.
            4. Supports `--version` flag.
            5. Provides comprehensive `--help` via `click`.
            6. No-args (without specified transport mode or info flags) prints help to stderr and exits non-zero.
            7. `click`-based CLI is clear and well-structured.
            8. Existing CLI tests updated for `click` and pass.
  - **Story 1.3: Establish and Test Fabric API Client Connectivity**
    - User Story: As the Fabric MCP Server, I want to reliably connect to and authenticate with the configured Fabric REST API instance using the `FabricApiClient` so that I can relay subsequent operational requests.
    - Acceptance Criteria:
            1. `FabricApiClient` initializes `base_url` from `FABRIC_BASE_URL` (default `http://127.0.0.1:8080`).
            2. `FabricApiClient` initializes `api_key` from `FABRIC_API_KEY` and includes `X-API-Key` header if key provided.
            3. `FabricApiClient` includes `User-Agent` header.
            4. Test: Successful basic GET request to mock Fabric API (2xx).
            5. Test: `FabricApiClient` handles connection errors (Fabric API down) by raising `httpx.RequestError`.
            6. Test: `FabricApiClient` handles Fabric API auth errors (401/403) by raising `httpx.HTTPStatusError`.
            7. Retry mechanism (via `RetryTransport`) tested for configured status codes/methods.
            8. Sensitive info (`FABRIC_API_KEY`) redacted from `FabricApiClient` debug logs.
  - **Story 1.4: Implement Basic MCP Server Handshake & Tool Discovery**
    - User Story: As an MCP Client, I want to connect to the Fabric MCP Server, complete the MCP handshake, and discover the list of available tools (even if initially as stubs) so that I know what operations I can perform.
    - Acceptance Criteria:
            1. Server launched in stdio mode initializes `FastMCP` loop.
            2. Server correctly identifies itself (name "Fabric MCP", version from `__about__.py`) during MCP handshake.
            3. Server successfully responds to MCP `list_tools()` request.
            4. `list_tools()` response includes definitions for all 6 core tools from `design.md`.
            5. Tool definitions in `list_tools()` response accurately reflect parameters/return types per `design.md` (even if underlying functions are stubs).
            6. Server handles basic MCP requests for stubbed tools gracefully.
            7. Integration tests verify client can connect, discover tools, and receive valid (even if placeholder) responses.
  - **Story 1.5: Ensure MVP Package Build and PyPI Readiness**
    - User Story: As a Project Maintainer, I want the Fabric MCP Server to be correctly configured for building distributions (sdist and wheel) using `hatch` and ready for an initial MVP publication to PyPI (starting with TestPyPI).
    - Acceptance Criteria:
            1. `pyproject.toml` fully configured for `hatchling` build (metadata, Python version, dependencies, scripts).
            2. `make build` (or `uv run hatch build`) successfully generates sdist and wheel in `dist/`.
            3. Wheel can be installed in a clean virtual env via `pip` and `uv`.
            4. Installed `fabric-mcp` script is executable and responds to `--version` / `--help`.
            5. Package successfully uploaded to TestPyPI and installable from TestPyPI.
            6. (Optional) Package successfully uploaded to official PyPI.
            7. `README.md` includes PyPI installation instructions.
  - **Story 1.6: Implement Streamable HTTP Transport for MCP Server**
    - User Story: As a Server Operator, I want to be able to run the Fabric MCP Server using FastMCP's "Streamable HTTP" transport so that MCP clients can connect to it over HTTP at a configurable endpoint (e.g., `/mcp`).
    - Acceptance Criteria:
            1. Server configurable and launchable with FastMCP's "Streamable HTTP" transport (via CLI or programmatically).
            2. Binds to configurable host/port (e.g., default `127.0.0.1:8000`).
            3. MCP endpoint path configurable (default `/mcp`).
            4. All defined MCP tools (pattern list/details/run, model/strategy list, config get) are functional over Streamable HTTP, including streaming for `fabric_run_pattern`.
            5. MCP errors correctly transmitted over Streamable HTTP. HTTP-specific errors handled by underlying ASGI server.
            6. Documentation updated for running with Streamable HTTP transport.
            7. Integration tests validate all key MCP tool functionalities (including streaming) using an HTTP-based MCP client. Tests verify host/port/path config.
  - **Story 1.7: Reorganize CLI Arguments with Transport Selection and Validation**
    - User Story: As a Server Operator, I want the CLI to use a cleaner `--transport` option with proper validation so that the interface is more intuitive and prevents invalid option combinations.
    - Acceptance Criteria:
            1. Replace `--stdio` and `--http-streamable` flags with a single `--transport` option accepting `stdio|http` (default: `stdio`).
            2. HTTP-specific options (`--host`, `--port`, `--mcp-path`) are only valid when `--transport http` is used.
            3. Click callback validation prevents HTTP-specific options from being used with `stdio` transport.
            4. Help text clearly indicates which options are transport-specific.
            5. Default values are shown in help text for all options.
            6. Existing functionality remains unchanged - only the CLI interface changes.
            7. All existing CLI tests updated and passing.
            8. Integration tests verify both transport modes work correctly with new CLI interface.
  - **Story 1.8: Implement SSE Transport for MCP Server**
    - User Story: As a Server Operator, I want to be able to run the Fabric MCP Server using FastMCP's (deprecated) "SSE" transport so that specific MCP clients expecting an SSE connection can interact with it at a configurable endpoint (e.g., `/sse`).
    - Acceptance Criteria:
            1. Add `sse` as a third option to the `--transport` choice (making it `stdio|http|sse`).
            2. SSE-specific options (`--host`, `--port`, `--sse-path`) are only valid when `--transport sse` is used.
            3. Click callback validation prevents SSE-specific options from being used with other transports.
            4. Server configurable and launchable with FastMCP's "SSE" transport via `--transport sse`.
            5. All defined MCP tools functional over SSE, including streaming for `fabric_run_pattern` (stream chunks as SSE events).
            6. MCP errors correctly transmitted over SSE. HTTP-specific errors handled by ASGI server.
            7. Documentation updated for running with SSE, noting FastMCP's deprecation.
            8. Integration tests validate MCP tool functionalities (including streaming) using an SSE-configured MCP client. Tests verify host/port/SSE path config.
