# 3. Non Functional Requirements (MVP)

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
