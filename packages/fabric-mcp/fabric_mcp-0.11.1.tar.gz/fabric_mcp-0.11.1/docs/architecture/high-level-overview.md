# High-Level Overview

The Fabric MCP Server is designed as a **monolithic service**, operating within a **single repository (monorepo)** structure as established in the PRD's technical assumptions. Its primary function is to serve as an intermediary, translating requests from Model Context Protocol (MCP) clients into appropriate REST API calls to a running `fabric --serve` instance. Conversely, it translates responses, including Server-Sent Event (SSE) streams from the Fabric API, back into MCP-compliant messages for the client.

The system exposes Fabric's core capabilities—such as pattern discovery, detailed introspection, execution (with support for various parameters and streaming), model and strategy listing, and configuration retrieval—through a set of standardized MCP tools. Users interact with these tools via their preferred MCP-compatible client applications (e.g., IDE extensions, chat interfaces), which connect to this server using one of the supported transport protocols: stdio, Streamable HTTP, or SSE.

The typical interaction flow is as follows:

1. An MCP client connects to the Fabric MCP Server.
2. The client discovers available tools (e.g., `fabric_run_pattern`) via MCP.
3. Upon user action in the client, an MCP request is sent to this server.
4. The Fabric MCP Server makes a corresponding HTTP request to the `fabric --serve` API.
5. The Fabric API processes the request and responds (potentially with an SSE stream for pattern execution).
6. The Fabric MCP Server relays this response, correctly formatted for MCP, back to the client.

This architecture ensures that the Fabric MCP Server remains a distinct layer, abstracting the specifics of Fabric's REST API and providing a standardized MCP interface, without requiring any modifications to the core Fabric framework.
