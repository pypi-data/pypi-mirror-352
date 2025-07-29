# 1. Overall UX Goals & Principles (Adapted for DX/OpX)

These goals and principles are derived from our collaborative discussion and the PRD's "User Interaction and Design Goals" section.

## 1.1. Target User Personas

- **MCP Client Developers:** Engineers building applications that will interact with the Fabric MCP Server via its MCP tools. Their goal is to easily discover, integrate, and utilize Fabric's functionalities within their own applications.
- **Server Administrators/Operators:** Individuals responsible for deploying, configuring, monitoring, and maintaining the Fabric MCP Server instance. Often, this role may be fulfilled by the developer end-user themselves. Their goal is a straightforward and trouble-free operational experience.
- **General Developers (End Users):** Developers who want to use the `fabric-mcp` server with existing LLM interaction environments (like Claude Desktop, VSCode extensions with MCP support, Void Editor, etc.). Their primary goal is to easily launch the server (often managed by their client tool) and connect their preferred tools to leverage Fabric's capabilities seamlessly.

## 1.2. Usability Goals

- **For MCP Client Developers:**
  - **Ease of Learning & Discoverability:** MCP tools must be easy to understand, with clear purposes, parameters, and discoverable functionalities (e.g., via MCP's `list_tools()` mechanism or the MCP Inspector).
  - **Efficiency of Use:** Interactions with MCP tools should be straightforward, minimizing the effort required for developers to integrate and achieve their objectives. This includes interactive debugging via tools like the FastMCP Inspector.
  - **Error Prevention & Clear Recovery:** The server must provide clear, structured, and informative feedback and error responses, enabling developers to effectively handle various outcomes and debug integrations.
- **For Server Administrators/Operators (often the Developer End User):**
  - **Ease of Setup & Operation:** Setting up, configuring (e.g., via environment variables like `FABRIC_BASE_URL`, `FABRIC_API_KEY`, `FABRIC_MCP_LOG_LEVEL`), and running the server (via its click-based CLI) must be simple and well-documented. This includes a startup connectivity check to the Fabric API for immediate feedback.
  - **Clarity of Monitoring:** Log output should be informative and structured, facilitating easy monitoring and troubleshooting based on the configured log level.
- **For General Developers (End Users):**
  - **Effortless Server Launch & Connection:** Starting the server with desired transport modes (stdio, Streamable HTTP, SSE), often managed by a client tool, should be very simple using the click-based CLI and standard configurations. Connecting their LLM tools should be straightforward with clear instructions or defaults.
  - **Clear Transport Mode Guidance:** Users must easily understand how to select and configure the different transport modes via the `--transport` CLI flag and associated options.
  - **Minimal Friction Onboarding:** The process from installing the server to having it running and connected to a client should be as smooth as possible.

## 1.3. Core DX/OpX Design Principles

- **Intuitive:** Command-line options, MCP tool names, parameters, and responses should be as self-explanatory as possible.
- **Informative:** Always provide clear, concise, and valuable information, whether it's successful output, help text, or error messages.
- **Consistent:** Maintain consistency in terminology, command structures, parameter naming, API response formats, and error reporting across all interaction points.
- **Robust & Forgiving:** Design for graceful error handling. Anticipate potential issues and provide helpful guidance to the user.
- **Efficient:** Streamline common tasks and interactions to save users time and effort.
- **Discoverable:** Users should be able to easily find out what they can do and how to do it (e.g., comprehensive `--help` for CLI, clear `list_tools()` for MCP, and interactive exploration via MCP Inspector).
