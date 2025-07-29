# Architectural / Design Patterns Adopted

The Fabric MCP Server will adopt several key architectural patterns to ensure a robust, maintainable, and clear design, conducive to implementation by AI developer agents.

* **Adapter Pattern:** This is fundamental to the server's purpose. The server will act as an adapter between the Model Context Protocol (MCP) interface exposed to clients and the REST/SSE API of the `fabric --serve` instance. Specific MCP tool implementations will adapt MCP requests and data structures into formats suitable for the Fabric API, and vice-versa for responses.
* **Facade Pattern:** The MCP tools themselves (e.g., `fabric_run_pattern`, `fabric_list_patterns`) will serve as a simplified facade over the potentially more detailed interactions required with the Fabric API. This shields MCP clients from the complexities of direct Fabric API communication.
* **Service Layer / Modular Design:** The application will be structured with clear separation of concerns:
  * **MCP Transport Handling Layer:** Managed by FastMCP, responsible for receiving MCP requests and sending MCP responses over stdio, Streamable HTTP, or SSE.
  * **Core Logic/Orchestration Layer:** Contains the implementation of the MCP tools. This layer orchestrates the translation of MCP requests, calls to the Fabric API client, and the formatting of responses.
  * **Fabric API Client Layer:** A dedicated module (`api_client.py` as per existing structure) responsible for all communication with the `fabric --serve` REST API, including handling HTTP requests, SSE stream consumption, and authentication.
* **Asynchronous Processing & Streaming:** Given the requirement to handle streaming output from Fabric patterns (via SSE) and relay it to MCP clients, the server will heavily rely on asynchronous programming paradigms (e.g., Python's `asyncio`, `httpx` async client) to manage concurrent connections and data streams efficiently.
* **Configuration Management:** Externalized configuration via environment variables (`FABRIC_BASE_URL`, `FABRIC_API_KEY`, `FABRIC_MCP_LOG_LEVEL`) as defined in the PRD will be used to manage operational parameters, promoting flexibility and adherence to twelve-factor app principles.
