# Epic 2: Fabric Pattern Discovery & Introspection

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
