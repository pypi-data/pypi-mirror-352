# Epic Overview

## Epic 1: Foundational Server Setup & Basic Operations

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
  - **Story 1.7: Implement SSE Transport for MCP Server**
    - User Story: As a Server Operator, I want to be able to run the Fabric MCP Server using FastMCP's (deprecated) "SSE" transport so that specific MCP clients expecting an SSE connection can interact with it at a configurable endpoint (e.g., `/sse`).
    - Acceptance Criteria:
            1. Server configurable and launchable with FastMCP's "SSE" transport (via CLI or programmatically).
            2. Binds to configurable host/port.
            3. MCP SSE endpoint path configurable (default `/sse`).
            4. All defined MCP tools functional over SSE, including streaming for `fabric_run_pattern` (stream chunks as SSE events).
            5. MCP errors correctly transmitted over SSE. HTTP-specific errors handled by ASGI server.
            6. Documentation updated for running with SSE, noting FastMCP's deprecation.
            7. Integration tests validate MCP tool functionalities (including streaming) using an SSE-configured MCP client. Tests verify host/port/SSE path config.

## Epic 2: Fabric Pattern Discovery & Introspection

- **Goal:** Enable MCP clients to dynamically discover available Fabric patterns and retrieve detailed information (system prompts, metadata) about specific patterns.
- **Stories:**
  - **Story 2.1: Implement `fabric_list_patterns` MCP Tool**
    - User Story: As an MCP Client Developer, I want to use the `fabric_list_patterns` tool to retrieve a list of all available pattern names from the connected Fabric instance so that I can display them to the end-user.
    - Acceptance Criteria:
            1. Tool implemented in `src/fabric_mcp/core.py`, replacing placeholder.
            2. Tool correctly registered and advertised via `list_tools()` (no params, returns `list[str]`) per `design.md`.
            3. Uses `FabricApiClient` for GET to Fabric API pattern listing endpoint (e.g., `/patterns`).
            4. Parses pattern names from Fabric API JSON response.
            5. Returns MCP success response with JSON array of pattern name strings (empty list if none).
            6. Returns structured MCP error if Fabric API errors or connection fails.
            7. Unit tests: mock `FabricApiClient` for success (multiple patterns, empty list), API errors, connection errors.
            8. Integration tests: (vs. live local `fabric --serve`) verify correct list retrieval.
  - **Story 2.2: Implement `fabric_get_pattern_details` MCP Tool**
    - User Story: As an MCP Client Developer, I want to use the `fabric_get_pattern_details` tool by providing a pattern name, to retrieve its system prompt and metadata from the Fabric instance, so I can display this information to the end-user.
    - Acceptance Criteria:
            1. Tool implemented in `src/fabric_mcp/core.py`, replacing placeholder.
            2. Tool registered and advertised via `list_tools()` (requires `pattern_name: str`, returns object) per `design.md`.
            3. Correctly processes mandatory `pattern_name` string parameter.
            4. Uses `FabricApiClient` for GET to Fabric API pattern details endpoint (e.g., `/patterns/<pattern_name>`).
            5. Parses system prompt (Markdown) and metadata from Fabric API response.
            6. MCP success response contains JSON object with `system_prompt: string` and `metadata: object`.
            7. Returns structured MCP error if Fabric API indicates pattern not found (e.g., 404).
            8. Returns structured MCP error for other Fabric API errors or connection failures.
            9. Unit tests: mock `FabricApiClient` for success, pattern not found (404), other API errors, connection errors, unexpected valid JSON.
            10. Integration tests: (vs. live local `fabric --serve`) for existing and non-existent patterns, validating MCP response/error.

## Epic 3: Core Fabric Pattern Execution with Strategy & Parameter Control

- **Goal:** Allow MCP clients to execute specified Fabric patterns, apply operational strategies, control execution with various parameters (model, temperature, variables, attachments), and receive output, including support for streaming.
- **Stories:**
  - **Story 3.1: Implement Basic `fabric_run_pattern` Tool (Non-Streaming)**
    - User Story: As an MCP Client Developer, I want to use the `fabric_run_pattern` tool to execute a named Fabric pattern with optional `input_text`, and receive its complete output in a non-streaming manner, so that I can integrate Fabric's fundamental pattern execution capability.
    - Acceptance Criteria:
            1. Tool implemented in `src/fabric_mcp/core.py` for basic, non-streaming execution.
            2. Advertised via `list_tools()` with at least `pattern_name: string (req)`, `input_text: string (opt)`, `stream: boolean (opt, default:false)`.
            3. Invokes Fabric API POST (e.g., `/chat`) via `FabricApiClient` with `pattern_name`, `input_text`; request is non-streaming.
            4. Waits for complete Fabric API response, parses LLM output.
            5. Returns MCP success with complete LLM output.
            6. Returns MCP client-side error if `pattern_name` missing.
            7. Returns structured MCP error for Fabric API errors or connection errors.
            8. Unit tests: mock `FabricApiClient` for correct request (name, input, non-streaming), successful response parsing, API errors, missing MCP params.
            9. Integration tests: (vs. live local `fabric --serve`) execute simple pattern with name/input, verify complete non-streaming output; test non-existent pattern for MCP error.
  - **Story 3.2: Implement `fabric_list_strategies` MCP Tool**
    - User Story: As an MCP Client Developer, I want to use the `fabric_list_strategies` tool to retrieve a list of all available operational strategies from the connected Fabric instance, so that end-users can be aware of or select different strategies if patterns support them.
    - Acceptance Criteria:
            1. Tool implemented in `src/fabric_mcp/core.py`.
            2. Registered and advertised via `list_tools()` (no params, returns list of objects) per `design.md`.
            3. Uses `FabricApiClient` for GET to Fabric API `/strategies` endpoint.
            4. Parses JSON response (array of strategy objects with `name`, `description`, `prompt`).
            5. MCP success response contains JSON array of strategy objects (name, description, prompt). Empty list if none.
            6. Returns structured MCP error for Fabric API errors or connection failures.
            7. Unit tests: mock `FabricApiClient` for success (list of strategies, empty list), API errors.
            8. Integration tests: (vs. live local `fabric --serve` with strategies configured) verify correct list of strategies; test with no strategies for empty list.
  - **Story 3.3: Enhance `fabric_run_pattern` with Execution Control Parameters (Model, LLM Params, Strategy)**
    - User Story: As an MCP Client Developer, I want to enhance the `fabric_run_pattern` tool to allow specifying optional `model_name`, LLM tuning parameters (`temperature`, `top_p`, `presence_penalty`, `frequency_penalty`), and an optional `strategy_name` (selected from those available via `fabric_list_strategies`) so that I can have finer control over the pattern execution by the Fabric instance.
    - Acceptance Criteria:
            1. `fabric_run_pattern` definition via `list_tools()` updated for optional `model_name` (str), `temperature` (float), `top_p` (float), `presence_penalty` (float), `frequency_penalty` (float), `strategy_name` (str).
            2. Tool parses these optional params; if provided, includes them in Fabric API request (e.g., `PromptRequest.Model`, `ChatOptions`, `PromptRequest.StrategyName`). Omits if not provided.
            3. Integration tests: verify `model_name` override, `strategy_name` application (e.g., "cot") affects output, LLM tuning params affect output.
            4. Returns structured MCP error if Fabric API rejects these parameters.
            5. Unit tests: mock `FabricApiClient` for request construction with these params (individual, mixed, omitted), API errors for invalid params.
            6. Integration tests: (vs. live local `fabric --serve`) test `model_name` override, `strategy_name` application, (if feasible) LLM tuning param effect; test invalid model/strategy names for MCP error.
  - **Story 3.4: Implement Streaming Output for `fabric_run_pattern` Tool**
    - User Story: As an MCP Client Developer, I want the `fabric_run_pattern` tool to support a `stream` parameter, which, when true, provides the Fabric pattern's output as a real-time stream, so that I can build more responsive and interactive client experiences.
    - Acceptance Criteria:
            1. Tool processes optional `stream: boolean` MCP parameter. `stream=true` initiates streaming; `stream=false`/omitted uses non-streaming.
            2. When `stream=true`, `FabricApiClient` requests SSE stream from Fabric API. **Client MUST use SSE-compatible mechanism (e.g., `httpx-sse`) to consume and parse `text/event-stream` (`data:` fields) from Fabric API.**
            3. Data chunks from Fabric API SSE events relayed to MCP client via `FastMCP` streaming over active transport (stdio, Streamable HTTP, SSE).
            4. Real-time data transfer with minimal latency.
            5. Handles errors during Fabric API SSE stream (e.g., invalid event, Fabric error mid-stream) by terminating MCP stream and sending MCP error.
            6. Unit tests: mock `FabricApiClient` for `stream=true` configuring SSE consumption, receiving/processing SSE chunks, stream termination (success/error).
            7. Integration tests: (vs. live local `fabric --serve`) execute streaming pattern with `stream=true`, verify multiple chunks and correct assembled output; confirm `stream=false` still works.
  - **Story 3.5: Add Support for `variables` and `attachments` to `fabric_run_pattern` Tool**
    - User Story: As an MCP Client Developer, I want to be able to pass `variables` (as a map of key-value strings) and `attachments` (as a list of file paths/URLs) to the `fabric_run_pattern` tool, so that I can execute more complex and context-rich Fabric patterns.
    - Acceptance Criteria:
            1. `fabric_run_pattern` definition via `list_tools()` updated for optional `variables` (map[string]string) and `attachments` (list[string]).
            2. If `variables` provided, parsed and included in Fabric API request payload. Omitted if not provided.
            3. If `attachments` provided, parsed and list of strings included in Fabric API request. Omitted if not provided. (Server only passes strings, Fabric resolves paths/URLs).
            4. Integration tests (mock Fabric API): verify `FabricApiClient` sends `variables` and `attachments` in requests. (Live Fabric API test if pattern exists to demonstrate use).
            5. Returns structured MCP error if Fabric API errors on `variables`/`attachments` processing.
            6. Unit tests: mock `FabricApiClient` for request construction with `variables` (empty, populated), `attachments` (empty, populated), both; simulate Fabric API errors.
            7. Integration tests: (vs. live local `fabric --serve`, ideally with test pattern) execute with `variables`/`attachments` and confirm (if possible) Fabric received/used them.

## Epic 4: Fabric Environment & Configuration Insights

- **Goal:** Provide MCP clients with the ability to list available Fabric models and strategies (strategy listing now moved to Epic 3), and to retrieve the current Fabric operational configuration securely.
- **Stories:**
  - **Story 4.1: Implement `fabric_list_models` MCP Tool**
    - User Story: As an MCP Client Developer, I want to use the `fabric_list_models` tool to retrieve a list of all AI models configured and available in the connected Fabric instance (potentially categorized by vendor), so that I can inform users or make programmatic choices about model selection for pattern execution.
    - Acceptance Criteria:
            1. Tool implemented in `src/fabric_mcp/core.py`.
            2. Registered and advertised via `list_tools()` (no params, returns object) per `design.md`.
            3. Uses `FabricApiClient` for GET to Fabric API `/models/names`.
            4. Parses JSON response from Fabric API (expected: list of all models, map of models by vendor).
            5. MCP success response contains structured JSON (e.g., `{"all_models": [...], "models_by_vendor": {...}}`). Empty lists/objects if none.
            6. Returns structured MCP error for Fabric API errors or connection failures.
            7. Unit tests: mock `FabricApiClient` for success (models/vendors, empty), API errors.
            8. Integration tests: (vs. live local `fabric --serve`) verify response reflects local Fabric model config; test with no models if possible.
  - **Story 4.3: Implement Secure `fabric_get_configuration` MCP Tool with Targeted Redaction**
    - User Story: As an MCP Client Developer, I want to use the `fabric_get_configuration` tool to retrieve the current operational configuration settings of the connected Fabric instance, **with assurances that sensitive values like API keys are redacted**, so that I can display relevant non-sensitive settings or understand the Fabric environment's setup securely.
    - Acceptance Criteria:
            1. Tool implemented in `src/fabric_mcp/core.py`. Registered and advertised via `list_tools()` (no params, returns map/object) per `design.md`.
            2. Uses `FabricApiClient` for GET to Fabric API `/config` endpoint.
            3. Parses JSON response (key-value map) from Fabric API. **Implements targeted redaction:** uses predefined list of sensitive key patterns (e.g., `*_API_KEY`, `*_TOKEN`). For matching keys with non-empty actual values, replaces value with `"[REDACTED_BY_MCP_SERVER]"`. Non-sensitive config values and empty string values are passed through.
            4. Returns MCP success response with processed (redacted where needed) JSON object.
            5. Returns structured MCP error for Fabric API errors or connection failures.
            6. Documentation notes redaction behavior and meaning of empty strings vs. redacted placeholders.
            7. Unit tests: mock `FabricApiClient`; test redaction logic (sensitive keys with values are redacted, sensitive keys with empty values passed as empty, non-sensitive keys passed through); test API errors.
            8. Integration tests: (vs. live local `fabric --serve` with dummy sensitive env vars set for Fabric) verify MCP response shows keys with `"[REDACTED_BY_MCP_SERVER]"` for sensitive values, and correct pass-through for non-sensitive/empty values.
