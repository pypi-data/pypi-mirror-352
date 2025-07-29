# Core Workflow / Sequence Diagrams

These diagrams illustrate the primary interaction flows within the Fabric MCP Server system.

## 1. MCP Client: Tool Discovery (`list_tools`)

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant ServerCore as Fabric MCP Server (FastMCP Core)
    participant ToolLogic as MCP Tool Implementations (core.py)

    Client->>ServerCore: MCP Request: list_tools()
    ServerCore->>ToolLogic: Request tool definitions
    ToolLogic-->>ServerCore: Provide tool definitions (e.g., for fabric_list_patterns, fabric_run_pattern, etc.)
    ServerCore-->>Client: MCP Response: list_tools_result (with tool details)
```

**Description:**

1. The MCP Client sends a `list_tools()` request to the Fabric MCP Server.
2. The FastMCP Core (ServerCore) receives this and queries the MCP Tool Implementations (ToolLogic) for the definitions of all registered tools.
3. The ToolLogic provides these definitions.
4. The ServerCore formats this into an MCP `list_tools_result` and sends it back to the Client.

## 2. MCP Client: Execute Non-Streaming Pattern (e.g., `fabric_list_models`)

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant ServerCore as Fabric MCP Server (FastMCP Core)
    participant ToolLogic as MCP Tool Implementations (core.py)
    participant FabricClient as Fabric API Client (api_client.py)
    participant FabricAPI as fabric --serve API

    Client->>ServerCore: MCP Request: fabric_list_models(params)
    ServerCore->>ToolLogic: Invoke fabric_list_models logic
    ToolLogic->>FabricClient: Request to fetch models from Fabric
    FabricClient->>FabricAPI: GET /models/names
    alt Successful Response
        FabricAPI-->>FabricClient: HTTP 200 OK (JSON list of models)
        FabricClient-->>ToolLogic: Return parsed model data
        ToolLogic-->>ServerCore: Provide formatted MCP success response
        ServerCore-->>Client: MCP Response: fabric_list_models_result (with model data)
    else Error Response from Fabric API
        FabricAPI-->>FabricClient: HTTP Error (e.g., 4xx, 5xx)
        FabricClient-->>ToolLogic: Return error information
        ToolLogic-->>ServerCore: Provide formatted MCP error response
        ServerCore-->>Client: MCP Error Response (e.g., urn:fabric-mcp:error:fabric-api-error)
    end
```

**Description (Revised for clarity):**

1. The MCP Client sends a request for a tool like `fabric_list_models`.
2. The ServerCore passes this to the specific ToolLogic implementation.
3. ToolLogic instructs the FabricClient to fetch the required data.
4. FabricClient makes a `GET /models/names` HTTP request to the `fabric --serve` API.
5. **If successful:**
      * FabricAPI returns an HTTP 200 OK response with the JSON data.
      * FabricClient parses this and returns it to ToolLogic.
      * ToolLogic formats the data into the MCP success response structure.
      * ServerCore sends the final MCP success response to the Client.
6. **If an error occurs at the Fabric API level:**
      * FabricAPI returns an HTTP error (e.g., 4xx or 5xx).
      * FabricClient conveys this error information to ToolLogic.
      * ToolLogic constructs an appropriate MCP error response.
      * ServerCore sends the MCP error response to the Client.

## 3. MCP Client: Execute Streaming Pattern (`fabric_run_pattern` with `stream: true`)

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant ServerCore as Fabric MCP Server (FastMCP Core)
    participant ToolLogic as MCP Tool Implementations (core.py)
    participant FabricClient as Fabric API Client (api_client.py)
    participant FabricAPI as fabric --serve API

    Client->>ServerCore: MCP Request: fabric_run_pattern(pattern_name="...", stream=true, ...)
    ServerCore->>ToolLogic: Invoke fabric_run_pattern logic (streaming)
    ToolLogic->>FabricClient: Request to run pattern (streaming) on Fabric
    FabricClient->>FabricAPI: POST /chat (with streaming headers, SSE request)
    FabricAPI-->>FabricClient: SSE Stream: event (data: chunk1)
    FabricClient-->>ToolLogic: Forward SSE chunk1
    ToolLogic-->>ServerCore: Send MCP stream data (chunk1)
    ServerCore-->>Client: MCP Stream Chunk (chunk1)

    FabricAPI-->>FabricClient: SSE Stream: event (data: chunk2)
    FabricClient-->>ToolLogic: Forward SSE chunk2
    ToolLogic-->>ServerCore: Send MCP stream data (chunk2)
    ServerCore-->>Client: MCP Stream Chunk (chunk2)

    alt Successful Stream Completion
        FabricAPI-->>FabricClient: SSE Stream: event (type: "complete")
        FabricClient-->>ToolLogic: Notify stream completion
        ToolLogic-->>ServerCore: Signal MCP stream end
        ServerCore-->>Client: MCP Stream End
    else Error During Stream
        FabricAPI-->>FabricClient: SSE Stream: event (type: "error", content: "error details") or connection error
        FabricClient-->>ToolLogic: Notify stream error
        ToolLogic-->>ServerCore: Provide MCP error object
        ServerCore-->>Client: MCP Error Response
    end
```

**Description:**

1. Client requests `fabric_run_pattern` with `stream: true`.
2. ServerCore invokes the ToolLogic for `fabric_run_pattern`.
3. ToolLogic instructs FabricClient to execute the pattern with streaming.
4. FabricClient makes a `POST /chat` request to FabricAPI, establishing an SSE connection.
5. FabricAPI sends SSE events (data chunks).
6. FabricClient receives these chunks and forwards them to ToolLogic.
7. ToolLogic wraps these chunks into MCP stream data and sends them via ServerCore to the Client.
8. This continues until the FabricAPI SSE stream ends (e.g., with a "complete" type event) or an error occurs. The Fabric MCP Server then appropriately signals the end of the MCP stream or sends an MCP error to the client.

## 4. Server Startup & Fabric API Connectivity Check

```mermaid
sequenceDiagram
    participant User as User/Operator
    participant CLI as CLI Handler (cli.py)
    participant Config as Configuration Component
    participant ServerCore as Fabric MCP Server (FastMCP Core)
    participant FabricClient as Fabric API Client (api_client.py)
    participant FabricAPI as fabric --serve API
    participant Logger as Logging Component

    User->>CLI: Executes `fabric-mcp --transport stdio --log-level DEBUG`
    CLI->>Config: Load environment variables (FABRIC_BASE_URL, FABRIC_API_KEY, etc.)
    CLI->>Logger: Set log level (e.g., DEBUG)
    CLI->>FabricClient: Initiate connectivity check
    FabricClient->>FabricAPI: Attempt lightweight GET (e.g., /config or /patterns/names)
    alt Fabric API Connected
        FabricAPI-->>FabricClient: Successful HTTP Response
        FabricClient-->>CLI: Report success
        CLI->>Logger: Log "Successfully connected to Fabric API at {FABRIC_BASE_URL}."
        CLI->>ServerCore: Initialize and start with configured transport (stdio)
        ServerCore->>Logger: Log "Fabric MCP Server started on stdio transport."
        ServerCore-->>User: Server ready for MCP connections
    else Fabric API Connection Failed
        FabricAPI-->>FabricClient: HTTP Error (e.g., connection refused, 401)
        FabricClient-->>CLI: Report failure with error details
        CLI->>Logger: Log "ERROR: Failed to connect to Fabric API at {FABRIC_BASE_URL}. Details: {error}."
        CLI-->>User: Exit with error message (or server starts but logs prominently)
    end
```

**Description:**

1. User starts the server via the CLI, providing transport and log level arguments.
2. The CLI loads configuration from environment variables.
3. The CLI initiates a connectivity check via the FabricClient.
4. The FabricClient attempts a lightweight GET request to the Fabric API (e.g., `/config` or `/patterns/names`).
5. If successful, a success message is logged, and the MCP Server Core is initialized and started.
6. If it fails, an actionable error message is logged, and the server might exit or start with a prominent error warning.
