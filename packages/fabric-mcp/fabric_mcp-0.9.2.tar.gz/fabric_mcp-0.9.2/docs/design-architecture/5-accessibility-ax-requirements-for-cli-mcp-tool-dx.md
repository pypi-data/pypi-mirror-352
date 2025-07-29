# 5. Accessibility (AX) Requirements (for CLI & MCP Tool DX)

- **Clarity and Simplicity of Language:** All CLI messages, log outputs, MCP tool descriptions, and error messages MUST use clear, simple, and unambiguous language.
- **Structured and Predictable Output:** CLI output (help, errors) and MCP tool responses (`list_tools()`, errors) MUST follow defined consistent structures.
- **Avoid Sole Reliance on Non-Textual Cues:** If color is used in CLI output (via `rich`), it MUST be supplementary; textual cues (e.g., "Error:") MUST always be present.
- **Machine Readability of MCP Interface:** MCP tool definitions and error responses MUST be structured for easy machine parsing to support client integrations.
- **Sufficient Detail in Descriptions and Errors:** All user-facing text MUST provide enough detail for understanding purpose, usage, or problems without requiring guesswork.
