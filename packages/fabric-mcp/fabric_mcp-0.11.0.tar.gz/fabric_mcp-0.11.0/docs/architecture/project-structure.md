# Project Structure

The Fabric MCP Server will adhere to the following project structure. This structure is designed for clarity, maintainability, and to support standard Python packaging and development practices.

```plaintext
fabric-mcp/
├── .github/                    # GitHub specific configurations
│   ├── pull_request_template.md # Template for pull requests
│   └── workflows/              # CI/CD workflows (GitHub Actions)
│       ├── get-version.yml     # Workflow to get project version
│       ├── publish.yml         # Workflow for publishing the package
│       └── tests.yml           # Workflow for running tests and linters
├── .vscode/                    # VSCode specific settings
│   ├── settings.json           # Workspace settings for VSCode
│   └── tasks.json              # Task configurations for VSCode
├── docs/                       # Project documentation
│   ├── contributing-cheatsheet.md # Contributor micro-summary
│   ├── contributing-detailed.md   # Detailed contribution guidelines
│   ├── contributing.md            # Main contribution guidelines
│   ├── design.md                  # High-Level Design Document (existing)
│   ├── design-architecture/index.md  # Developer/Operational Experience Spec (existing)
│   ├── logo.png                   # Project logo
│   ├── PM-checklist.md            # Product Manager checklist (existing)
│   ├── PRD.md                     # Product Requirements Document (existing)
│   ├── architecture/index.md      # The index file with all the architecture documents
│   ├── api-reference.md           # Generated: Details of Fabric API consumed & MCP tools provided
│   ├── data-models.md             # Generated: Data schemas for MCP tools and Fabric API
│   ├── environment-vars.md        # Generated: Detailed list of environment variables
│   ├── operational-guidelines.md  # Generated: Coding standards, testing, error handling
│   ├── project-structure.md       # Generated: This section, as a standalone file
│   ├── tech-stack.md              # Generated: Definitive technology stack
│   └── index.md                   # Generated: Central catalog of all documentation
├── src/                        # Application source code
│   └── fabric_mcp/             # Main Python package for the server
│       ├── __about__.py        # Stores package version and metadata
│       ├── __init__.py         # Package initializer
│       ├── api_client.py       # Fabric API Client component
│       ├── cli.py              # CLI Handler component (using Click)
│       ├── core.py             # MCP Tool Implementations (core logic)
│       ├── server_hooks.py     # (New) Callbacks or hooks for FastMCP (if needed)
│       ├── server_stdio.py     # Existing entry point for `make dev` / MCP Inspector
│       ├── server_transports.py # (New) Specific configurations for stdio, HTTP, SSE transports (used by cli.py)
│       └── utils.py            # Utility functions shared within the application
├── tests/                      # Automated tests
│   ├── __init__.py
│   ├── integration/            # Integration tests
│   │   ├── __init__.py
│   │   └── test_mcp_integration.py # Example: E2E tests for MCP tools with live Fabric
│   └── unit/                   # Unit tests (mirroring src/fabric_mcp structure)
│       ├── __init__.py
│       ├── test_api_client.py
│       ├── test_cli.py         # Renamed from test_cli_additional.py for consistency
│       ├── test_core.py
│       ├── test_server_transports.py # (New) Tests for transport configurations
│       └── test_utils.py
├── .env.example                # Example environment variables file
├── .gitignore                  # Git ignore rules
├── .pylintrc                   # Pylint configuration file
├── .ruff.toml                  # Ruff linter and formatter configuration file
├── cspell.json                 # Spell checking configuration (existing)
├── LICENSE                     # Project license file
├── Makefile                    # Make commands for development tasks
├── pyproject.toml              # Python project configuration (PEP 518/621)
├── README.md                   # Project overview and setup instructions
└── uv.lock                     # uv lock file for reproducible dependencies
```

## Key Directory Descriptions

* **`.github/`**: Contains GitHub-specific files, including `pull_request_template.md` and workflow configurations for CI/CD in the `workflows/` subdirectory (e.g., `tests.yml`, `publish.yml`, `get-version.yml`).
* **`.vscode/`**: Holds VSCode editor-specific settings (`settings.json`) and task configurations (`tasks.json`).
* **`docs/`**: Houses all project documentation, including the PRD, this architecture document, user guides, and other specifications. The `index.md` within will serve as a catalog.
* **`src/fabric_mcp/`**: The primary Python package containing all the server's operational code.
  * `api_client.py`: Dedicated module for interacting with the Fabric REST API.
  * `cli.py`: Implements the command-line interface using `click`; serves as the main user entry point for all transport modes.
  * `core.py`: Contains the logic for MCP tool implementations.
  * `server_hooks.py` (New): Intended for any callback functions or hooks that FastMCP might require for specific events or customizations during the MCP communication lifecycle.
  * `server_stdio.py`: Existing file, maintained as the specific entry point for `make dev` which uses `uv run fastmcp dev src/fabric_mcp/server_stdio.py` for the MCP Inspector.
  * `server_transports.py` (New): Will contain helper functions or classes for setting up and configuring the different MCP transports (stdio, Streamable HTTP, SSE) to be used by `cli.py` when launching FastMCP for general use.
* **`tests/`**: Contains all automated tests.
  * `tests/unit/`: Unit tests for individual modules and functions, mirroring the `src/fabric_mcp/` structure.
  * `tests/integration/`: Integration tests that verify interactions between components or with a mocked/live Fabric API instance.
* **Root directory files**: Standard project files including:
  * Linters and formatter configurations: `.ruff.toml`, `.pylintrc`.
  * Project build and dependency management: `pyproject.toml` (which also configures `pyright` for strict type checking), `uv.lock`.
  * Development utilities: `Makefile`.
  * Informational: `README.md`, `LICENSE`, `.env.example`.
  * Other tooling: `cspell.json`, `.gitignore`.

## Notes

* The `src/fabric_mcp/server_stdio.py` is understood to be a specific entry point for development and debugging with the MCP Inspector via `make dev`.
* The main `cli.py` will handle the operational launch of the server in stdio mode for end-users, as well as for HTTP and SSE transports, likely utilizing helpers from the new `server_transports.py` for configuring FastMCP.
* I've suggested renaming `test_cli_additional.py` to `test_cli.py` for more direct correspondence if it's the primary test file for `cli.py`.
* New files like `server_hooks.py` and `server_transports.py` are proposed to better organize the server's operational aspects and cleanly integrate with FastMCP via the main `cli.py`.
