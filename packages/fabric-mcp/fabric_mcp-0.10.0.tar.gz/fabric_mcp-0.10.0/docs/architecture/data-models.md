# Data Models

The Fabric MCP Server primarily deals with transforming data between the Model Context Protocol (MCP) and the Fabric REST API. It does not maintain its own persistent database or complex internal domain entities beyond what is necessary for request/response handling and configuration.

## Core Application Entities / Domain Objects

Conceptually, the server handles:

* **MCP Requests/Responses:** Structures defined by the Model Context Protocol and specific to each MCP tool. These are detailed in the "Internal APIs Provided (MCP Tools)" section of this document.
* **Fabric API Requests/Responses:** Structures defined by the `fabric --serve` REST API. These are detailed in the "External APIs Consumed" section, with specific Go structs like `ChatRequest`, `PromptRequest`, `StreamResponse`, `StrategyMeta`, and configuration/model data structures from the `restapi-code.json` source.
* **Configuration Settings:** Simple key-value pairs loaded from environment variables (e.g., `FABRIC_BASE_URL`, `FABRIC_API_KEY`, `FABRIC_MCP_LOG_LEVEL`).

## API Payload Schemas (MCP Tools & Fabric API)

The detailed JSON schemas for data exchanged are best understood in the context of the APIs themselves:

* **Fabric REST API (Consumed):** The request and response schemas for the Fabric API endpoints (e.g., `/chat`, `/patterns/names`, `/config`, `/models/names`, `/strategies`) have been defined in the **[External APIs Consumed](https://www.google.com/search?q=%23fabric-rest-api)** section, based on the provided Go source code.
* **MCP Tools (Provided):** The parameter and return value schemas for each MCP tool provided by this server (e.g., `fabric_list_patterns`, `fabric_run_pattern`) have been defined in the **[Internal APIs Provided (MCP Tools)](https://www.google.com/search?q=%23internal-apis-provided-mcp-tools)** section. These define the contract with MCP clients.

## Database Schemas

* **Not Applicable:** The Fabric MCP Server is a stateless application. It does not have its own database and relies on the connected `fabric --serve` instance for any data persistence related to patterns, models, configurations, etc..
