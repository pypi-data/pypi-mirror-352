# Security Best Practices

The following security considerations and practices are mandatory for the development and operation of the Fabric MCP Server.

* **Input Sanitization/Validation:**

  * All parameters received from MCP clients for MCP tool execution (e.g., `pattern_name`, `input_text`, `model_name` for `fabric_run_pattern`) MUST be validated by the respective tool implementation in `core.py` before being used or passed to the `Fabric API Client`.
  * Validation should check for expected types, formats (e.g., ensuring `pattern_name` is a string and does not contain malicious path traversal characters if used in constructing API paths, though `httpx` typically handles URL encoding), and reasonable length limits to prevent abuse or unexpected behavior.
  * The `click` framework provides some initial validation for CLI arguments.

* **Output Encoding:**

  * The primary output to MCP clients is structured JSON (for tool responses or MCP errors) or SSE data chunks (which are also JSON formatted as per Fabric's `StreamResponse`). The `FastMCP` library and standard JSON serialization libraries are expected to handle correct encoding, preventing injection issues into the MCP communication channel.
  * Data relayed from the Fabric API is assumed to be correctly formatted by Fabric; our server focuses on faithfully transmitting it within the MCP structure.

* **Secrets Management:**

  * The `FABRIC_API_KEY` is a critical secret and MUST be handled securely.
  * It MUST be provided to the server exclusively via the `FABRIC_API_KEY` environment variable.
  * The server MUST NEVER hardcode the `FABRIC_API_KEY` or include it directly in source control.
  * The `FABRIC_API_KEY` MUST NOT be logged in clear text. If logging API interactions for debugging, the key itself must be masked or omitted from logs.
  * The `api_client.py` will read this key from the environment via the Configuration Component and include it in the `X-API-Key` header for requests to the Fabric API.
  * The `fabric_get_configuration` MCP tool has a specific NFR to redact API keys (and other known sensitive values) received from the Fabric API `/config` endpoint before relaying them to the MCP client, using a placeholder like `"[REDACTED_BY_MCP_SERVER]"`.

* **Dependency Security:**

  * Project dependencies managed by `uv` via `pyproject.toml` and `uv.lock` should be regularly checked for known vulnerabilities.
  * Tools like `uv audit` (if available and analogous to `pip-audit` or `npm audit`) or other vulnerability scanners (e.g., Snyk, Dependabot alerts integrated with GitHub) should be used periodically or as part of the CI process.
  * Vulnerable dependencies, especially high or critical ones, must be updated promptly. New dependencies should be vetted before addition.

* **Authentication/Authorization:**

  * **To Fabric API:** The Fabric MCP Server authenticates to the Fabric REST API using the `FABRIC_API_KEY` if provided.
  * **MCP Client to Fabric MCP Server:** The MVP of the Fabric MCP Server does not define its own user authentication or authorization layer for incoming MCP client connections. Security for these connections relies on the inherent security of the chosen transport:
    * `stdio`: Assumes a secure local environment where the client process and server process are run by the same trusted user.
    * `http`/`sse`: For network-based transports, it's recommended to run the server behind a reverse proxy (e.g., Nginx, Caddy) that can enforce TLS (HTTPS), and potentially client certificate authentication or network-level access controls (firewalls, IP whitelisting) if needed by the deployment environment. These external measures are outside the direct scope of the `fabric-mcp` application code but are operational best practices.

* **Principle of Least Privilege (Implementation):**

  * The OS user account running the `fabric-mcp` server process should have only the necessary permissions required for its operation (e.g., execute Python, bind to a configured network port if using HTTP/SSE, read environment variables, make outbound network connections to the Fabric API).
  * It should not run with elevated (e.g., root) privileges unless absolutely necessary for a specific, justified reason (none anticipated).

* **API Security (for HTTP/SSE Transports):**

  * **HTTPS:** While the Python ASGI server (like Uvicorn, which FastMCP might use under the hood for HTTP transports) can serve HTTP directly, production deployments MUST use a reverse proxy to terminate TLS and serve over HTTPS.
  * **Standard HTTP Security Headers:** A reverse proxy should also be configured to add standard security headers like `Strict-Transport-Security` (HSTS), `Content-Security-Policy` (CSP) if serving any HTML content (not typical for this MCP server), `X-Content-Type-Options`, etc.
  * **Rate Limiting & Throttling:** Not in scope for MVP but could be implemented at a reverse proxy layer in the future if abuse becomes a concern.

* **Error Handling & Information Disclosure:**

  * As outlined in the "Error Handling Strategy," error messages returned to MCP clients (via MCP error objects) or logged to the console must not leak sensitive internal information such as stack traces, internal file paths, or raw database errors (from Fabric, if they were to occur and be relayed). Generic error messages with correlation IDs (for server-side log lookup) are preferred for client-facing errors when the detail is sensitive.

* **Logging:**

  * Ensure that logs, especially at `DEBUG` level, do not inadvertently include sensitive data from requests or responses. API keys are explicitly forbidden from being logged.
