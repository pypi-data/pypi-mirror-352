# 5. Technical Assumptions

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

## Testing requirements

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
