# Fabric MCP Server - DX/Interaction Specification

- [Fabric MCP Server - DX/Interaction Specification](#fabric-mcp-server---dxinteraction-specification)
  - [Introduction](#introduction)
  - [1. Overall UX Goals \& Principles (Adapted for DX/OpX)](#1-overall-ux-goals--principles-adapted-for-dxopx)
    - [1.1. Target User Personas](#11-target-user-personas)
    - [1.2. Usability Goals](#12-usability-goals)
    - [1.3. Core DX/OpX Design Principles](#13-core-dxopx-design-principles)
  - [2. Information Architecture (IA)](#2-information-architecture-ia)
    - [2.1. CLI Command Structure \& Design](#21-cli-command-structure--design)
    - [2.2. MCP Tool Organization \& Discoverability](#22-mcp-tool-organization--discoverability)
    - [2.3. Configuration Information](#23-configuration-information)
    - [2.4. User-Facing Documentation Structure (Conceptual)](#24-user-facing-documentation-structure-conceptual)
  - [3. User Flows](#3-user-flows)
    - [User Flow 1 (Revised): General Developer (End User) - Configure and use `fabric-mcp` in stdio mode with a managing client tool](#user-flow-1-revised-general-developer-end-user---configure-and-use-fabric-mcp-in-stdio-mode-with-a-managing-client-tool)
    - [User Flow 2 (Revised): MCP Client Developer - Discover, Understand, and Test Available Fabric Tools using MCP Inspector](#user-flow-2-revised-mcp-client-developer---discover-understand-and-test-available-fabric-tools-using-mcp-inspector)
    - [User Flow 3: MCP Client Developer - Execute a Fabric Pattern with Input and Streaming](#user-flow-3-mcp-client-developer---execute-a-fabric-pattern-with-input-and-streaming)
    - [User Flow 4 (Revised): Server Administrator/Operator - Configure Fabric API Connection and Log Level (with startup check)](#user-flow-4-revised-server-administratoroperator---configure-fabric-api-connection-and-log-level-with-startup-check)
    - [User Flow 5: General Developer (End User) - Launch server in Streamable HTTP mode](#user-flow-5-general-developer-end-user---launch-server-in-streamable-http-mode)
    - [User Flow 6: MCP Client Developer - Get Fabric configuration securely](#user-flow-6-mcp-client-developer---get-fabric-configuration-securely)
    - [User Flow 7: Server Administrator/Operator - Troubleshoot Fabric API Connection Issue](#user-flow-7-server-administratoroperator---troubleshoot-fabric-api-connection-issue)
  - [4. Interaction Patterns \& Conventions](#4-interaction-patterns--conventions)
    - [4.1. CLI Interaction Conventions](#41-cli-interaction-conventions)
    - [4.2. MCP Tool Interaction Conventions](#42-mcp-tool-interaction-conventions)
    - [4.3. Language, Tone, and Terminology](#43-language-tone-and-terminology)
  - [5. Accessibility (AX) Requirements (for CLI \& MCP Tool DX)](#5-accessibility-ax-requirements-for-cli--mcp-tool-dx)
  - [Change Log](#change-log)

## Introduction

This document defines the Developer Experience (DX) and Operational Experience (OpX) goals, architecture, flows, and conventions for the Fabric MCP Server. It focuses on its Command Line Interface (CLI), Model Context Protocol (MCP) tool interactions, and overall usability for its technical user personas. It adapts principles from traditional UI/UX design to a backend server context that primarily interacts via CLI and API. All design choices aim to support the goals and requirements outlined in the main Product Requirements Document (PRD).

## 1. Overall UX Goals & Principles (Adapted for DX/OpX)

These goals and principles are derived from our collaborative discussion and the PRD's "User Interaction and Design Goals" section.

### 1.1. Target User Personas

- **MCP Client Developers:** Engineers building applications that will interact with the Fabric MCP Server via its MCP tools. Their goal is to easily discover, integrate, and utilize Fabric's functionalities within their own applications.
- **Server Administrators/Operators:** Individuals responsible for deploying, configuring, monitoring, and maintaining the Fabric MCP Server instance. Often, this role may be fulfilled by the developer end-user themselves. Their goal is a straightforward and trouble-free operational experience.
- **General Developers (End Users):** Developers who want to use the `fabric-mcp` server with existing LLM interaction environments (like Claude Desktop, VSCode extensions with MCP support, Void Editor, etc.). Their primary goal is to easily launch the server (often managed by their client tool) and connect their preferred tools to leverage Fabric's capabilities seamlessly.

### 1.2. Usability Goals

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

### 1.3. Core DX/OpX Design Principles

- **Intuitive:** Command-line options, MCP tool names, parameters, and responses should be as self-explanatory as possible.
- **Informative:** Always provide clear, concise, and valuable information, whether it's successful output, help text, or error messages.
- **Consistent:** Maintain consistency in terminology, command structures, parameter naming, API response formats, and error reporting across all interaction points.
- **Robust & Forgiving:** Design for graceful error handling. Anticipate potential issues and provide helpful guidance to the user.
- **Efficient:** Streamline common tasks and interactions to save users time and effort.
- **Discoverable:** Users should be able to easily find out what they can do and how to do it (e.g., comprehensive `--help` for CLI, clear `list_tools()` for MCP, and interactive exploration via MCP Inspector).

## 2. Information Architecture (IA)

### 2.1. CLI Command Structure & Design

- **Main Command:** `fabric-mcp`.
- **Overall Structure:** Flat, with a primary mandatory `--transport <MODE>` flag for server operation, where `<MODE>` is one of `stdio`, `http`, or `sse` (case-insensitive).
- **Key Flags/Options:**
  - `--transport {stdio|http|sse}`: Specifies the MCP transport mode.
  - `--host <hostname>`: For `http`/`sse` transports, specifies host. (Default: e.g., `127.0.0.1`).
  - `--port <port_number>`: For `http`/`sse` transports, specifies port. (Default: e.g., `8000` for HTTP, `8001` for SSE to avoid conflict).
  - `--path <http_path>`: For `http`/`sse` transports, specifies MCP endpoint path. (Default: e.g., `/mcp` for HTTP, `/sse` for SSE).
  - `--log-level {DEBUG|INFO|WARNING|ERROR|CRITICAL}`: Sets logging verbosity. (Default: `INFO`).
  - `--version`: Displays server version.
  - `--help` / `-h`: Displays help message.
- **Flag Naming Convention:** `kebab-case` (e.g., `--log-level`).
- **Help Message Structure (`fabric-mcp --help`):** Generated by `click`. Must include usage line, brief description, and clearly list all options with arguments, choices, descriptions, and default values. Options should be grouped logically (e.g., "Transport Options," "General Options").
- **No-Args/Invalid-Args Behavior:** If `--transport` is not specified, or an invalid mode/option is given, the CLI prints help to stderr and exits with a non-zero status code.
- **Shell Completion:** The CLI design with `--transport <MODE>` supports discoverability via shell completion, a desired DX feature.
- **Startup Connectivity Check:** On startup, `fabric-mcp` will attempt to query a lightweight endpoint (e.g., `/config` or `/version`) of the configured Fabric API to verify connectivity and authentication, providing clear success or actionable error messages in the logs.

### 2.2. MCP Tool Organization & Discoverability

- **Tool Naming Convention:** `fabric_verb_noun` (e.g., `fabric_list_patterns`).
- **Discoverability via `list_tools()`:** This MCP command is the primary mechanism for client developers to discover tools. The response for each tool MUST include:
  - `name`: Exact tool name.
  - `description`: Clear, concise, user-centric explanation.
  - `parameters`: List of parameter objects, each detailing `name` (snake_case), `type`, `required` (boolean), and `description` (purpose, constraints, defaults).
  - `return_value`: Object detailing `type` and `description` of the expected successful response.
- **Consistency:** Enforced for parameter naming and data structures across all tools.
- **Getting Tool Details:** The `list_tools()` response serves as the comprehensive definition. The MCP Inspector is the recommended way for developers to explore these details interactively.

### 2.3. Configuration Information

- **Naming Conventions:** Environment variables in `UPPER_SNAKE_CASE` (e.g., `FABRIC_API_KEY`); CLI flags in `kebab-case`.
- **Discoverability/Documentation:** A dedicated "Configuration" section in `README.md` and comprehensive details in `fabric-mcp --help` for CLI options.
- **Defaults:** Sensible defaults for log level, transport host/port/path MUST be used and clearly documented.
- **Precedence:** For settings configurable by both CLI flag and environment variable (e.g., log level), CLI flags override environment variables.
- **Validation & Error Reporting:** Missing or invalid configurations must result in clear, actionable error messages at startup, guiding the user to the problematic setting.
- **Security of Sensitive Configuration:** Documentation will remind users about secure handling of `FABRIC_API_KEY`.

### 2.4. User-Facing Documentation Structure (Conceptual)

- **Existing Documentation:** Acknowledges the user's existing documentation in their GitHub repository, with `README.md` as the primary entry point.
- **Key Emphasis Points for User Documentation:**
  - **Discoverability:** Easy navigation from the main project page (`README.md`).
  - **Clarity for All Personas:** Sections or guides catering to General Developers, MCP Client Developers, and Server Administrators.
  - **Practical Examples:** Crucial for CLI commands and MCP tool usage.
  - **Comprehensive Configuration Details:** Covering all environment variables and CLI options.
- **In-Context Documentation:** The CLI's `--help` output and the MCP `list_tools()` response are vital sources of in-context documentation.

## 3. User Flows

(Summaries of the collaboratively defined user flows)

### User Flow 1 (Revised): General Developer (End User) - Configure and use `fabric-mcp` in stdio mode with a managing client tool

- **Persona:** General Developer (End User).
- **Goal:** Easily configure a local MCP-compatible tool to automatically launch and use `fabric-mcp` in `stdio` mode.
- **Key Steps:** Install `fabric-mcp`; ensure Fabric prerequisites and env vars are set; configure client tool with `fabric-mcp` command (e.g., in JSON settings specifying `type: "stdio"`, `command: "fabric-mcp"`, `args: ["--transport", "stdio"]`); client tool manages server lifecycle and connection; utilize Fabric via client.
- **Feedback:** Clear success/failure from installation and client tool connection; `fabric-mcp` provides meaningful exit codes/stderr for startup failures when managed as a subprocess.

### User Flow 2 (Revised): MCP Client Developer - Discover, Understand, and Test Available Fabric Tools using MCP Inspector

- **Persona:** MCP Client Developer.
- **Goal:** Interactively discover, understand contracts of, and test `fabric-mcp` tools using the MCP Inspector.
- **Key Steps:** Run `make dev`; access Inspector in browser; connect to server; explore `list_tools()` output; select tools to view detailed definitions; interactively execute tools and observe requests/responses.
- **Feedback:** Terminal output for `make dev`; Inspector UI shows connection status, tool lists, definitions, and real-time execution results.

### User Flow 3: MCP Client Developer - Execute a Fabric Pattern with Input and Streaming

- **Persona:** MCP Client Developer.
- **Goal:** Programmatically execute a Fabric pattern with input, requesting and receiving a real-time streamed output.
- **Key Steps:** Construct MCP request to `fabric_run_pattern` (with `pattern_name`, `input_text`, `stream=true`, etc.); send request; server processes and initiates streaming from Fabric API (SSE); server relays stream chunks via MCP; client handles streamed data; stream terminates (success or error with MCP error object).
- **Feedback:** Client receives streamed data chunks incrementally; final MCP error if stream aborts.

### User Flow 4 (Revised): Server Administrator/Operator - Configure Fabric API Connection and Log Level (with startup check)

- **Persona:** Server Administrator/Operator (often the Developer End User).
- **Goal:** Correctly configure `fabric-mcp` for Fabric API connection, verify connection at startup, and set log level.
- **Key Steps:** Set `FABRIC_BASE_URL`, `FABRIC_API_KEY`, `FABRIC_MCP_LOG_LEVEL` env vars; start/restart `fabric-mcp`; server performs startup connectivity check to Fabric API (e.g., `/config` or `/version`); monitor logs.
- **Feedback:** Clear startup log messages indicating success or specific failure reasons for Fabric API connection; ongoing logs reflect chosen log level.

### User Flow 5: General Developer (End User) - Launch server in Streamable HTTP mode

- **Persona:** General Developer (End User).
- **Goal:** Launch `fabric-mcp` in Streamable HTTP mode and connect an MCP client using this transport.
- **Key Steps:** Run `fabric-mcp --transport http --host <h> --port <p> --path <pa>`; server starts and logs listening address; configure client tool with server address; client connects; utilize Fabric via client.
- **Feedback:** Server logs listening endpoint; client tool confirms connection. Clear error if port is in use.

### User Flow 6: MCP Client Developer - Get Fabric configuration securely

- **Persona:** MCP Client Developer.
- **Goal:** Retrieve current Fabric operational configuration with sensitive values redacted.
- **Key Steps:** Client sends MCP request to `fabric_get_configuration`; server calls Fabric API `/config`; server redacts sensitive keys (e.g., `*_API_KEY` becomes `"[REDACTED_BY_MCP_SERVER]"`); server returns redacted configuration object.
- **Feedback:** Client receives configuration object with sensitive data protected.

### User Flow 7: Server Administrator/Operator - Troubleshoot Fabric API Connection Issue

- **Persona:** Server Administrator/Operator (often the Developer End User).
- **Goal:** Diagnose and resolve issues preventing `fabric-mcp` from connecting to `fabric --serve`.
- **Key Steps:** Observe symptoms; increase log verbosity (`FABRIC_MCP_LOG_LEVEL=DEBUG`); inspect detailed error logs (connection refused, auth errors, timeouts); formulate hypothesis and take corrective action (check URL, key, Fabric server status); restart and re-verify with startup check and/or client test.
- **Feedback:** Detailed and actionable error messages in logs; successful connection message upon resolution.

## 4. Interaction Patterns & Conventions

### 4.1. CLI Interaction Conventions

- **Output Formatting (Leveraging `click` and `rich`):**
  - **Help Text (`--help`):** Standard `click` structure with clear usage, description, options list (grouped if numerous), arguments, choices, and default values explicitly stated.
  - **Informational Messages:** Clear, direct, potentially prefixed (e.g., `[INFO]`), and can use sparse, meaningful color (e.g., green for success) via `rich`.
  - **Error Message Standards:** Clearly prefixed (e.g., `[ERROR]`), styled (e.g., red via `rich`), contextual, and actionable, suggesting causes or fixes where possible.

### 4.2. MCP Tool Interaction Conventions

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

### 4.3. Language, Tone, and Terminology

- **Tone:** Professional, clear, concise, helpful, neutral, and accurate. Avoid overly casual or unhelpful error messages.
- **Terminology:** Consistent use of key terms like "Pattern," "Strategy," "Model," "Transport," "MCP Tool" across CLI, logs, MCP definitions, and documentation.
- **Capitalization:** Consistent capitalization for "Fabric," "MCP," transport names (e.g., "Streamable HTTP"), environment variables (`UPPER_SNAKE_CASE`), CLI flags (`kebab-case`), and MCP tool/parameter names (`snake_case`).
- **Action-Oriented Language:** Use clear verbs where appropriate.

## 5. Accessibility (AX) Requirements (for CLI & MCP Tool DX)

- **Clarity and Simplicity of Language:** All CLI messages, log outputs, MCP tool descriptions, and error messages MUST use clear, simple, and unambiguous language.
- **Structured and Predictable Output:** CLI output (help, errors) and MCP tool responses (`list_tools()`, errors) MUST follow defined consistent structures.
- **Avoid Sole Reliance on Non-Textual Cues:** If color is used in CLI output (via `rich`), it MUST be supplementary; textual cues (e.g., "Error:") MUST always be present.
- **Machine Readability of MCP Interface:** MCP tool definitions and error responses MUST be structured for easy machine parsing to support client integrations.
- **Sufficient Detail in Descriptions and Errors:** All user-facing text MUST provide enough detail for understanding purpose, usage, or problems without requiring guesswork.

## Change Log

| Version | Date       | Author        | Description of Changes                                                                              |
| :------ | :--------- | :------------ | :-------------------------------------------------------------------------------------------------- |
| 1.0.1   | 2025-05-27 | Kayvan Sylvan | Format. Table of Contents. |
| 1.0.0   | 2025-05-27 | BMad (as Jane)| Initial DX/Interaction Specification draft created collaboratively, covering key personas and interactions. |
