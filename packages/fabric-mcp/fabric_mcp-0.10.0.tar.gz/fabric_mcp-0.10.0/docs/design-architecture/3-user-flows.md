# 3. User Flows

(Summaries of the collaboratively defined user flows)

## User Flow 1 (Revised): General Developer (End User) - Configure and use `fabric-mcp` in stdio mode with a managing client tool

- **Persona:** General Developer (End User).
- **Goal:** Easily configure a local MCP-compatible tool to automatically launch and use `fabric-mcp` in `stdio` mode.
- **Key Steps:** Install `fabric-mcp`; ensure Fabric prerequisites and env vars are set; configure client tool with `fabric-mcp` command (e.g., in JSON settings specifying `type: "stdio"`, `command: "fabric-mcp"`, `args: ["--transport", "stdio"]`); client tool manages server lifecycle and connection; utilize Fabric via client.
- **Feedback:** Clear success/failure from installation and client tool connection; `fabric-mcp` provides meaningful exit codes/stderr for startup failures when managed as a subprocess.

## User Flow 2 (Revised): MCP Client Developer - Discover, Understand, and Test Available Fabric Tools using MCP Inspector

- **Persona:** MCP Client Developer.
- **Goal:** Interactively discover, understand contracts of, and test `fabric-mcp` tools using the MCP Inspector.
- **Key Steps:** Run `make dev`; access Inspector in browser; connect to server; explore `list_tools()` output; select tools to view detailed definitions; interactively execute tools and observe requests/responses.
- **Feedback:** Terminal output for `make dev`; Inspector UI shows connection status, tool lists, definitions, and real-time execution results.

## User Flow 3: MCP Client Developer - Execute a Fabric Pattern with Input and Streaming

- **Persona:** MCP Client Developer.
- **Goal:** Programmatically execute a Fabric pattern with input, requesting and receiving a real-time streamed output.
- **Key Steps:** Construct MCP request to `fabric_run_pattern` (with `pattern_name`, `input_text`, `stream=true`, etc.); send request; server processes and initiates streaming from Fabric API (SSE); server relays stream chunks via MCP; client handles streamed data; stream terminates (success or error with MCP error object).
- **Feedback:** Client receives streamed data chunks incrementally; final MCP error if stream aborts.

## User Flow 4 (Revised): Server Administrator/Operator - Configure Fabric API Connection and Log Level (with startup check)

- **Persona:** Server Administrator/Operator (often the Developer End User).
- **Goal:** Correctly configure `fabric-mcp` for Fabric API connection, verify connection at startup, and set log level.
- **Key Steps:** Set `FABRIC_BASE_URL`, `FABRIC_API_KEY`, `FABRIC_MCP_LOG_LEVEL` env vars; start/restart `fabric-mcp`; server performs startup connectivity check to Fabric API (e.g., `/config` or `/version`); monitor logs.
- **Feedback:** Clear startup log messages indicating success or specific failure reasons for Fabric API connection; ongoing logs reflect chosen log level.

## User Flow 5: General Developer (End User) - Launch server in Streamable HTTP mode

- **Persona:** General Developer (End User).
- **Goal:** Launch `fabric-mcp` in Streamable HTTP mode and connect an MCP client using this transport.
- **Key Steps:** Run `fabric-mcp --transport http --host <h> --port <p> --path <pa>`; server starts and logs listening address; configure client tool with server address; client connects; utilize Fabric via client.
- **Feedback:** Server logs listening endpoint; client tool confirms connection. Clear error if port is in use.

## User Flow 6: MCP Client Developer - Get Fabric configuration securely

- **Persona:** MCP Client Developer.
- **Goal:** Retrieve current Fabric operational configuration with sensitive values redacted.
- **Key Steps:** Client sends MCP request to `fabric_get_configuration`; server calls Fabric API `/config`; server redacts sensitive keys (e.g., `*_API_KEY` becomes `"[REDACTED_BY_MCP_SERVER]"`); server returns redacted configuration object.
- **Feedback:** Client receives configuration object with sensitive data protected.

## User Flow 7: Server Administrator/Operator - Troubleshoot Fabric API Connection Issue

- **Persona:** Server Administrator/Operator (often the Developer End User).
- **Goal:** Diagnose and resolve issues preventing `fabric-mcp` from connecting to `fabric --serve`.
- **Key Steps:** Observe symptoms; increase log verbosity (`FABRIC_MCP_LOG_LEVEL=DEBUG`); inspect detailed error logs (connection refused, auth errors, timeouts); formulate hypothesis and take corrective action (check URL, key, Fabric server status); restart and re-verify with startup check and/or client test.
- **Feedback:** Detailed and actionable error messages in logs; successful connection message upon resolution.
