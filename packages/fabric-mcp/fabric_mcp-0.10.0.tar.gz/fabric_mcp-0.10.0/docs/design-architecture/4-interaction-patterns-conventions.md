# 4. Interaction Patterns & Conventions

## 4.1. CLI Interaction Conventions

- **Output Formatting (Leveraging `click` and `rich`):**
  - **Help Text (`--help`):** Standard `click` structure with clear usage, description, options list (grouped if numerous), arguments, choices, and default values explicitly stated.
  - **Informational Messages:** Clear, direct, potentially prefixed (e.g., `[INFO]`), and can use sparse, meaningful color (e.g., green for success) via `rich`.
  - **Error Message Standards:** Clearly prefixed (e.g., `[ERROR]`), styled (e.g., red via `rich`), contextual, and actionable, suggesting causes or fixes where possible.

## 4.2. MCP Tool Interaction Conventions

- **Adherence to MCP Specification:** The server will comply with the Model Context Protocol specification, with `FastMCP` handling low-level details.
- **Parameter Naming (Requests):** All MCP tool parameter names will use `snake_case` (e.g., `pattern_name`, `input_text`).
- **Data Typing (Requests & Responses):** Data types specified in `list_tools()` for parameters and return values must be accurate and consistently applied.
- **Response Data Structures (Success):**
  - Responses will be JSON. Keys within response objects will also use `snake_case` for consistency.
  - Lists will be returned as JSON arrays (empty `[]` if no items).
  - Detailed objects will have clearly defined and consistent field names.
  - "Not Found" for specific items results in an MCP error, not an empty success response.
- **Error Response Content (MCP Errors):**
  - Uses standard MCP error structure. Application-specific error conditions will be identified by URN-style error `type` (e.g., `urn:fabric-mcp:error:fabric-api-unavailable`, `urn:fabric-mcp:error:pattern-not-found`) with clear, human-readable `title` and `detail` messages.
- **Streaming Data Conventions (`fabric_run_pattern` with `stream=true`):**
  - Content of MCP stream data chunks will be the raw string data from Fabric API's SSE `data:` fields.
  - Successful stream termination is handled by MCP/FastMCP.
  - Errors occurring *during* an active stream from Fabric API will cause `fabric-mcp` to terminate the MCP stream and send a distinct MCP error object to the client (e.g., `urn:fabric-mcp:error:fabric-stream-interrupted`).

## 4.3. Language, Tone, and Terminology

- **Tone:** Professional, clear, concise, helpful, neutral, and accurate. Avoid overly casual or unhelpful error messages.
- **Terminology:** Consistent use of key terms like "Pattern," "Strategy," "Model," "Transport," "MCP Tool" across CLI, logs, MCP definitions, and documentation.
- **Capitalization:** Consistent capitalization for "Fabric," "MCP," transport names (e.g., "Streamable HTTP"), environment variables (`UPPER_SNAKE_CASE`), CLI flags (`kebab-case`), and MCP tool/parameter names (`snake_case`).
- **Action-Oriented Language:** Use clear verbs where appropriate.
