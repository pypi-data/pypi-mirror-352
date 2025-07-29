# Fabric MCP Server Product Requirements Document (PRD)

- [Fabric MCP Server Product Requirements Document (PRD)](#fabric-mcp-server-product-requirements-document-prd)
  - [1. Goal, Objective and Context](#1-goal-objective-and-context)
    - [Goal](#goal)
    - [Objective](#objective)
    - [Context](#context)
  - [2. Functional Requirements (MVP)](#2-functional-requirements-mvp)
  - [3. Non Functional Requirements (MVP)](#3-non-functional-requirements-mvp)
  - [4. User Interaction and Design Goals](#4-user-interaction-and-design-goals)
    - [A. Developer Experience (DX) Goals (for MCP Client Developers)](#a-developer-experience-dx-goals-for-mcp-client-developers)
    - [B. Operational Design Goals (for Server Administrators/Users)](#b-operational-design-goals-for-server-administratorsusers)
  - [5. Technical Assumptions](#5-technical-assumptions)
    - [Testing requirements](#testing-requirements)
  - [Epic Overview](#epic-overview)
    - [Epic 1: Foundational Server Setup \& Basic Operations](#epic-1-foundational-server-setup--basic-operations)
    - [Epic 2: Fabric Pattern Discovery \& Introspection](#epic-2-fabric-pattern-discovery--introspection)
    - [Epic 3: Core Fabric Pattern Execution with Strategy \& Parameter Control](#epic-3-core-fabric-pattern-execution-with-strategy--parameter-control)
    - [Epic 4: Fabric Environment \& Configuration Insights](#epic-4-fabric-environment--configuration-insights)
  - [6. Key Reference Documents](#6-key-reference-documents)
  - [7. Out of Scope Ideas Post MVP](#7-out-of-scope-ideas-post-mvp)
  - [8. Change Log](#8-change-log)

## 1. Goal, Objective and Context

### Goal

The primary goal of the Fabric MCP Server project is to seamlessly integrate the open-source [Fabric AI framework by Daniel Miessler][fabricGithubLink] with any [Model Context Protocol (MCP)][MCP] compatible application. This will empower users to leverage Fabric's powerful patterns, models, and configurations directly within their existing MCP-enabled environments (like IDE extensions or chat interfaces) without context switching, leading to enhanced developer productivity and more sophisticated AI-assisted interactions.

### Objective

- To develop a standalone server application that acts as a bridge between Fabric's REST API (exposed by `fabric --serve`) and MCP clients.
- To translate MCP requests into corresponding Fabric API calls and relay Fabric's responses (including streaming) back to the MCP client.
- To expose core Fabric functionalities like listing patterns, getting pattern details, running patterns, listing models/strategies, and retrieving configuration through standardized MCP tools.
- To adhere to the open MCP standard for AI tool integration, fostering interoperability.

### Context

The Fabric MCP Server addresses the need for integrating Fabric's specialized prompt engineering capabilities and AI workflows into diverse LLM interaction environments. It aims to eliminate the current barrier of potentially needing a separate interface for Fabric, thereby streamlining workflows and directly enhancing user productivity and the quality of AI assistance within their preferred tools. This project leverages the existing Fabric CLI and its REST API without requiring modifications to the core Fabric codebase. It is important to note that this project refers to the [open-source Fabric AI framework by Daniel Miessler][fabricGithubLink], not other software products with similar names.

## 2. Functional Requirements (MVP)

The Fabric MCP Server, for its MVP, will provide the following functionalities to an MCP-compatible client:

1. **MCP Standard Compliance & Basic Operation:**
    - The server MUST correctly implement the Model Context Protocol (MCP) for communication with MCP clients.
    - The server MUST allow MCP clients to discover available Fabric-related tools (e.g., via MCP's `list_tools()` mechanism).
    - The server MUST be able to start and listen for connections from MCP clients (e.g., initially via stdio, with options for Streamable HTTP and SSE transports).
    - The server MUST process valid MCP requests and return appropriately structured MCP responses.

2. **Fabric Instance Connectivity & Configuration:**
    - The server MUST connect to a running Fabric instance via its REST API using a configurable base URL (`FABRIC_BASE_URL`).
    - The server MUST support authentication with the Fabric REST API using a configurable API key (`FABRIC_API_KEY`), if provided.
    - The server's logging behavior MUST be configurable via a log level setting (`FABRIC_MCP_LOG_LEVEL`).

3. **Exposing Fabric Pattern Functionality:**
    - **List Patterns:** Users MUST be able to request and receive a list of available Fabric patterns.
    - **Get Pattern Details:** Users MUST be able to request and receive details for a specific Fabric pattern, including its system prompt and metadata, by providing the pattern's name.
    - **Run Pattern:**
        - Users MUST be able to execute a specified Fabric pattern by providing its name.
        - The server MUST allow users to provide optional input text for the pattern.
        - The server MUST allow users to specify optional parameters for pattern execution, such as model name, LLM tuning parameters (`temperature`, `top_p`, `presence_penalty`, `frequency_penalty`), an operational `strategy_name`, `variables` (map[string]string), and `attachments` (list of strings).
        - The server MUST be able to return the output generated by the Fabric pattern to the user.
        - The server MUST support streaming the pattern's output to the MCP client if requested by the client (via `stream=true` parameter) and supported by the Fabric API (which uses SSE).

4. **Exposing Fabric Model & Strategy Information:**
    - **List Models:** Users MUST be able to request and receive a list of configured Fabric models, potentially organized by vendor.
    - **List Strategies:** Users MUST be able to request and receive a list of available Fabric strategies, including their name, description, and prompt.

5. **Exposing Fabric Configuration:**
    - **Get Configuration:** Users MUST be able to request and receive the current Fabric operational configuration settings. The server MUST redact sensitive values (like API keys) before relaying this information.

## 3. Non Functional Requirements (MVP)

1. **Performance:**
    - The server SHOULD respond to MCP client requests in a timely manner, ensuring a responsive experience for the end-user interacting via the MCP client.
    - For pattern execution requests involving streaming (`stream=true`), the server MUST efficiently proxy the data stream (received as SSE from Fabric API) to the MCP client to enable real-time display of output.
2. **Reliability & Error Handling:**
    - The server MUST reliably translate valid MCP requests into appropriate Fabric API calls and accurately translate Fabric API responses back into MCP responses.
    - The server MUST gracefully handle errors originating from the Fabric API (e.g., Fabric API unavailable, authentication errors, invalid pattern names, model errors). Such errors MUST be reported back to the MCP client using clear, structured MCP error responses.
    - The server application itself MUST be stable and avoid crashes due to common operational issues or malformed (but parsable by MCP) requests.
3. **Security:**
    - If a `FABRIC_API_KEY` is configured for accessing the Fabric REST API, the server MUST handle this key securely and ensure it is not exposed to MCP clients or inadvertently logged.
    - For the `fabric_get_configuration` tool, the server MUST implement logic to redact known sensitive keys (e.g., API keys) received from the Fabric API before relaying the configuration to the MCP client, replacing actual secret values with a placeholder like `"[REDACTED_BY_MCP_SERVER]"`.
    - The server should be developed following security best practices to avoid introducing vulnerabilities.
4. **Maintainability & Code Quality (for the Fabric MCP Server codebase):**
    - The server's codebase MUST adhere to the development workflow, code style, quality standards, and testing practices outlined in the project's contribution guidelines (e.g., `contributing.md`, `contributing-detailed.md`). This includes mandatory formatting, linting, type checking, and achieving defined code coverage targets.
5. **Compatibility & Interoperability:**
    - The server MUST adhere to the Model Context Protocol (MCP) specification (e.g., version 2025-03-26 as referenced in `design.md`) to ensure compatibility with MCP clients.
    - A critical constraint is that the server MUST integrate with the Fabric framework by solely using its existing REST API (`fabric --serve`) and MUST NOT require any modifications to the core Fabric codebase.
6. **Configurability:**
    - The server's core operational parameters, including the Fabric API base URL (`FABRIC_BASE_URL`), Fabric API key (`FABRIC_API_KEY`), and its own internal logging verbosity (`FABRIC_MCP_LOG_LEVEL`), MUST be configurable via environment variables.
    - The server MUST support configuration for its listening transport (stdio, Streamable HTTP, SSE), including host, port, and path where applicable.
7. **Logging:**
    - The server MUST generate logs based on the configured `FABRIC_MCP_LOG_LEVEL`. These logs should be sufficient for troubleshooting and monitoring server activity.
8. **Deployment & Operation:** (Revised)
    - The server MUST be runnable as a standalone process. It MUST support MCP communication via:
        - stdio (e.g., when launched with CLI flags that specify normal input/output via terminal).
        - Streamable HTTP transport, configurable to listen on a specific host, port, and path (e.g., `http://localhost:8000/mcp`).
        - SSE transport, configurable to listen on a specific host, port, and path (e.g., `http://localhost:8000/sse`).

## 4. User Interaction and Design Goals

As the Fabric MCP Server is a backend application, this section focuses on the **Developer Experience (DX)** for engineers building MCP client applications that will interact with this server, and the **Operational Simplicity** for individuals deploying and running the server.

### A. Developer Experience (DX) Goals (for MCP Client Developers)

1. **Intuitive MCP Tool Design:**
    - The MCP tools exposed by the server (e.g., `fabric_list_patterns`, `fabric_run_pattern`) MUST be designed to be as self-explanatory and intuitive as possible.
    - Tool names, parameter names, and descriptions (discoverable via MCP's `list_tools()`) SHOULD clearly indicate their purpose and usage.
2. **High Information Value & Ease of Use:**
    - The information returned by the MCP tools (e.g., pattern details, model lists, pattern outputs) SHOULD be high-value, accurate, and presented in a format that is easy for MCP client applications to parse and utilize.
    - Interactions with the tools SHOULD be straightforward, adhering to MCP standards.
3. **Clear Feedback & Error Reporting:**
    - Success and error responses from MCP tools MUST be clear, structured, and informative, enabling MCP client developers to effectively handle various outcomes and debug integrations.
4. **Automated & Synchronized Development Environment:** (Updated)
    - The project leverages `pre-commit` hooks (for conventional commits, branch protection) and an enhanced `Makefile` (for streamlined setup, testing, formatting, safe merges, and MCP inspector integration) to ensure an automatically updating, consistent, and high-quality development environment. This aims for minimal tooling maintenance overhead and maximum team synchronization on development standards.
5. **Interactive Debugging & Testing:** (New)
    - A `make dev` target is provided, utilizing `pnpm` to install `@modelcontextprotocol/inspector`, allowing developers to easily run the Fabric MCP Server with the FastMCP Inspector for interactive testing and debugging of MCP functionalities directly in a browser.

### B. Operational Design Goals (for Server Administrators/Users)

1. **Simplicity of Setup & Initial Run:**
    - Setting up and running the Fabric MCP Server SHOULD be straightforward.
    - Installation via PyPI (`pip install fabric-mcp` or `uv pip install fabric-mcp`) SHOULD be simple and reliable.
    - Initiating the server (e.g., with flags for stdio transport, or with flags for HTTP/SSE transport) SHOULD be via simple commands.
2. **Clarity of Configuration:**
    - Configuration via environment variables (`FABRIC_BASE_URL`, `FABRIC_API_KEY`, `FABRIC_MCP_LOG_LEVEL`) MUST be clearly documented and easy to understand.
    - Configuration for HTTP-based transports (host, port, path) MUST also be clearly documented.
3. **Informative Log Output:**
    - The server's log output, controlled by `FABRIC_MCP_LOG_LEVEL`, SHOULD be clear, structured (where appropriate), and provide sufficient detail for monitoring and troubleshooting.
4. **Deployment Flexibility:**
    - Support for stdio, Streamable HTTP, and SSE transports provides flexibility for various deployment scenarios. Dockerization (as seen in the Fabric project's Dockerfile) could be a future consideration for `fabric-mcp` to further enhance ease of deployment.

## 5. Technical Assumptions

This section outlines the foundational technical decisions and assumptions for the Fabric MCP Server project.

1. **Repository & Service Architecture:**
    - **Repository Structure:** The project will be developed and maintained within a **single repository (monorepo)**, as per the existing project structure.
    - **Service Architecture:** The Fabric MCP Server itself will be a **monolithic service** (a single, standalone deployable application).
2. **Primary Language & Runtime:**
    - The server will be implemented in **Python**.
    - The required Python version is **>=3.11**.
3. **Key Frameworks & Libraries:**
    - **MCP Implementation:** The server will use the **FastMCP library** (`fastmcp>=2.5.1`). This builds upon `modelcontextprotocol>=0.1.0`.
    - **HTTP Client (for Fabric API):** The `httpx` library (`httpx>=0.28.1`) will be used for REST API calls to Fabric, with `httpx-retries>=0.4.0` for retries, and `httpx-sse` for consuming SSE streams from Fabric API.
    - **CLI Framework:** The CLI will utilize the **`click` library** (`click>=8.1.8` is an existing dependency). This involves refactoring the current CLI from `argparse`.
    - **Logging/Console Output:** The `rich` library (`rich>=14.0.0`) will be used for enhanced terminal output.
4. **Development Environment & Tooling:** (Revised)
    - Package and environment management will be handled by `uv`.
    - `pre-commit` hooks are configured via `.pre-commit-config.yaml` to enforce standards like conventional commit messages and branch protection. The `Makefile` integrates `pre-commit` for autoupdates and installation during `make bootstrap`.
    - Code linting and formatting will primarily use `ruff`, with `isort` for import sorting and `pylint` for additional checks. These are integrated into `pre-commit` workflows and/or `make lint` targets.
    - Type checking will be enforced using `pyright`, typically invoked via `make lint`.
    - Testing will be done using `pytest` with `pytest-cov` for coverage, executable via `make test`.
    - `pnpm` is utilized as the Node package manager for installing specific development tools like `@modelcontextprotocol/inspector`.
    - The project utilizes an enhanced `Makefile` for streamlined developer workflows, including `bootstrap`, `format`, `lint`, `test`, `build`, a safe `merge` target, and a `dev` target for launching the server with the FastMCP Inspector.
5. **External API Interaction:**
    - The primary external dependency is the **Fabric REST API** (from Daniel Miessler's Fabric project, exposed by `fabric --serve`). This API uses SSE for streaming responses.
    - Connection to this API will be configured via `FABRIC_BASE_URL` and `FABRIC_API_KEY` environment variables.
6. **Transport Protocol (MVP):** (Revised)
    - The Fabric MCP Server will support multiple MCP transport mechanisms for client connections:
        - **stdio:** Default for simple CLI execution (stdio mode) and for clients managing the server as a subprocess.
        - **Streamable HTTP:** The recommended HTTP-based transport (as per FastMCP documentation), serving MCP over a standard HTTP endpoint (e.g., `/mcp`).
        - **SSE (Server-Sent Events):** An alternative HTTP-based transport serving MCP over an SSE endpoint (e.g., `/sse`) to support clients that specifically expect this, while noting that FastMCP documentation refers to its server-side SSE transport as deprecated in favor of Streamable HTTP.
7. **No Core Fabric Modifications:**
    - A fundamental assumption is that this project will **not require any changes to the core Fabric framework codebase**. It will integrate solely via the existing Fabric REST API.

### Testing requirements

The project already establishes a foundation of unit testing with `pytest` and a 90% code coverage target, as well as linting and type checking. Beyond this, the MVP validation will focus on the following:

1. **Integration Testing:**
    - Integration tests MUST validate the Fabric MCP Server's interaction with a live (locally running) `fabric --serve` instance.
    - Key scenarios SHOULD cover the successful execution of each defined MCP tool against the live Fabric backend, verifying correct request formation and response parsing.
2. **End-to-End (E2E) Testing:**
    - E2E tests MUST be developed to simulate an MCP client interacting with the Fabric MCP Server across all supported transports (stdio, Streamable HTTP, SSE).
    - These tests SHOULD cover common user workflows for each defined MCP tool.
    - This may involve creating a lightweight test MCP client or leveraging existing MCP client development tools for test automation.
3. **Specific Validation Focus Areas:**
    - **Request/Response Translation:** Testing MUST explicitly verify the correct translation of MCP tool parameters into Fabric API requests and the accurate mapping of Fabric API responses (both success and error states, including SSE streams) back into the MCP format over the active transport.
    - **Streaming Functionality:** For pattern executions involving streaming, tests MUST ensure the stream is proxied efficiently and reliably from the Fabric API (SSE) to the MCP client over all supported transports.
    - **Error Handling & Robustness:** The server's behavior when encountering errors from the Fabric API MUST be thoroughly tested to ensure graceful failure and informative error reporting to the MCP client over all supported transports.
4. **Manual Testing:**
    - While automated testing is prioritized, the need for specific manual testing scripts or checklists will be evaluated as development progresses. The `make dev` target using the MCP Inspector provides a means for interactive manual testing.

## Epic Overview

### Epic 1: Foundational Server Setup & Basic Operations

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

### Epic 2: Fabric Pattern Discovery & Introspection

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

### Epic 3: Core Fabric Pattern Execution with Strategy & Parameter Control

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

### Epic 4: Fabric Environment & Configuration Insights

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

## 6. Key Reference Documents

{This section will be populated by the PO Agent after sharding this PRD using the `doc-sharding-task`. It will primarily link to `docs/index.md` which catalogs all sharded documentation files derived from this PRD and subsequent architectural documents.}

## 7. Out of Scope Ideas Post MVP

- **Write/Update Operations for Fabric Configuration via MCP:** The current `fabric_get_configuration` tool is read-only. An MCP tool to modify Fabric's configuration (potentially using Fabric API's POST `/config/update` endpoint) is out of scope for MVP.
- **Direct MCP Tools for Specialized Fabric Features:** Fabric's CLI offers many specific functionalities (e.g., YouTube processing, Jina AI scraping, detailed context/session management beyond simple naming). Direct MCP tool mappings for these specialized features are out of scope for this MVP, which focuses on core pattern interaction and information retrieval.
- **Advanced `fabric_run_pattern` Variable Types:** While the MVP supports string-to-string variables for patterns, future enhancements could explore richer structured data types if Fabric's capabilities evolve in that direction.
- **More Advanced MCP Features from FastMCP:** Capabilities like client-side LLM sampling initiated by the server or richer resource interactions are not planned for this MVP.
- **Enhanced Filtering/Searching for List Tools:** Adding server-side filtering or searching capabilities to `fabric_list_patterns` and `fabric_list_strategies` is deferred; current implementation relies on clients to handle large lists.

## 8. Change Log

| Version | Date       | Author        | Description of Changes                                                                                                                               |
| :------ | :--------- | :------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.0.1   | 2025-05-27 | Kayvan Sylvan  | Format fixes. Table of Contents. |
| 1.0.0   | 2025-05-27 | BMad (as PM)  | Initial PRD draft completed for MVP. Epics 1-4 defined. Transports: stdio, Streamable HTTP, SSE. Key redaction for config. Dev env updates included. |

[fabricGithubLink]: https://github.com/danielmiessler/fabric
[MCP]: https://modelcontextprotocol.io/
