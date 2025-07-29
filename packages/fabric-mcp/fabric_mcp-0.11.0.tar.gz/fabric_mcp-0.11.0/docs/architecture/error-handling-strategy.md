# Error Handling Strategy

A robust error handling strategy is crucial for providing a reliable and user-friendly experience. This section outlines the approach for handling errors within the Fabric MCP Server.

* **General Approach:**

  * The primary mechanism for error handling within the Python application will be through exceptions. Custom exceptions may be defined for specific error conditions arising from the Fabric API client or core logic to allow for more granular error management.
  * Errors propagated to the MCP client will be formatted as standard MCP error objects, including a URN-style `type`, a `title`, and a `detail` message, as specified in the DX/Interaction document.
  * For CLI operations, errors will be clearly reported to `stderr`, potentially using `rich` for better formatting, and the server will exit with a non-zero status code for critical startup failures.

* **Logging:**

  * **Library/Method:** The `rich` library will be used for enhanced console output, and Python's standard `logging` module will be configured to work with it for structured logging.
  * **Format:** Logs should be structured (e.g., JSON format is preferred for production-like deployments if easily configurable, otherwise human-readable with clear timestamp, level, and message). For `rich`-based console output, a human-readable, color-coded format will be used.
  * **Levels:** Standard Python logging levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) will be used. The log level will be configurable via the `--log-level` CLI flag and the `FABRIC_MCP_LOG_LEVEL` environment variable.
  * **Context:** Logs for errors should include relevant contextual information such as:
    * Timestamp
    * Log level
    * Module/function where the error occurred
    * A unique request ID or correlation ID if feasible (especially for HTTP transports)
    * Sanitized key parameters related to the operation
    * The error message and potentially a stack trace for `DEBUG` level.

* **Specific Handling Patterns:**

  * **External API Calls (to `fabric --serve`):**
    * **HTTP Errors:** The `Fabric API Client` (`api_client.py`) will handle HTTP status codes from the Fabric API.
      * `4xx` errors (e.g., `401 Unauthorized`, `403 Forbidden`, `404 Not Found`) will be translated into specific MCP error types and logged appropriately. For instance, a `404` when fetching a pattern could become `urn:fabric-mcp:error:pattern-not-found`.
      * `5xx` server errors from Fabric will be treated as critical failures of the upstream service and result in an MCP error like `urn:fabric-mcp:error:fabric-api-unavailable` or `urn:fabric-mcp:error:fabric-internal-error`.
    * **Connection Errors:** Network issues (e.g., connection refused, timeouts) when calling the Fabric API will be caught by `httpx` and should result in an MCP error (e.g., `urn:fabric-mcp:error:fabric-api-unavailable`).
    * **Retries:** The `Fabric API Client` will use `httpx-retries` to automatically retry idempotent requests on transient network errors or specific server-side error codes (e.g., 502, 503, 504) as configured. Max retries and backoff strategy will be defined.
    * **Timeouts:** Explicit connect and read timeouts will be configured for `httpx` to prevent indefinite blocking.
    * **SSE Stream Errors:** If an error occurs *during* an active SSE stream from the Fabric API (e.g., Fabric sends an error event or the connection drops), the `Fabric API Client` will detect this. The MCP Tool Implementation for `fabric_run_pattern` will then terminate the MCP stream to the client and send a distinct MCP error object (e.g., `urn:fabric-mcp:error:fabric-stream-interrupted`).
  * **Internal Errors / Business Logic Exceptions:**
    * Unexpected errors within the Fabric MCP Server's core logic will be caught by a top-level error handler for each MCP tool invocation.
    * These will be logged with detailed stack traces (at `DEBUG` or `ERROR` level).
    * A generic MCP error (e.g., `urn:fabric-mcp:error:internal-server-error`) will be sent to the client to avoid exposing internal details, but with a unique identifier (correlation ID if implemented) that can be used to find the detailed log.
  * **MCP Request Validation Errors:**
    * If an MCP client sends a malformed request (e.g., missing required parameters, incorrect data types for parameters), the FastMCP library or the tool implementation layer should catch this.
    * An MCP error with a type like `urn:fabric-mcp:error:invalid-request` or `urn:mcp:error:validation` will be returned to the client with details about the validation failure.
  * **Configuration Errors:**
    * Missing or invalid essential configurations (e.g., unparseable `FABRIC_BASE_URL`) at startup will result in clear error messages logged to `stderr` and the server may fail to start.
  * **Transaction Management:** Not applicable, as the Fabric MCP Server is stateless. Data consistency is the responsibility of the `fabric --serve` instance.
