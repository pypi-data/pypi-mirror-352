# Definitive Tech Stack Selections

This section outlines the definitive technology choices for the project. These selections are based on the project's requirements as detailed in the PRD. This table is the **single source of truth** for all technology selections.

| Category                   | Technology                               | Version / Details         | Description / Purpose                                       | Justification (Optional)                                     |
| :------------------------- | :--------------------------------------- | :------------------------ | :---------------------------------------------------------- | :----------------------------------------------------------- |
| **Languages** | Python                                   | >=3.11                    | Primary language for the server                             | Modern Python features, community support, available libraries. |
| **Runtime** | CPython                                  | Matches Python >=3.11     | Standard Python runtime                                     |                                                              |
| **Frameworks** | FastMCP                                  | >=2.5.1                   | Core Model Context Protocol implementation                  | Chosen for MCP adherence.                         |
|                            | Click                                    | >=8.1.8                   | CLI framework for user-friendly command-line interactions   | Specified in PRD for CLI.                         |
| **Libraries** | httpx                                    | >=0.28.1                  | HTTP client for Fabric API communication                    | Supports async, HTTP/2, chosen for REST API calls.  |
|                            | httpx-retries                            | >=0.4.0                   | Retry mechanisms for httpx                                  | Enhances resilience of Fabric API calls.        |
|                            | httpx-sse                                | Specific version TBD (latest) | Client for consuming Server-Sent Events from Fabric API     | Required for streaming from Fabric API.           |
|                            | Rich                                     | >=14.0.0                  | Enhanced terminal output for logging and CLI messages     | Improves CLI usability and log readability.     |
| **Development Tooling** | uv                                       | Latest stable             | Python package and environment manager                      | Speed and modern dependency management. |
|                            | pre-commit                               | Latest stable             | Framework for managing pre-commit hooks                     | Enforces code quality and standards before commit. |
|                            | Ruff                                     | Latest stable             | Linter and formatter                                        | Speed and comprehensive checks.                 |
|                            | isort                                    | Latest stable             | Import sorter (often integrated via Ruff)                 | Code style consistency.                       |
|                            | Pylint                                   | Latest stable             | Additional linter for deeper static analysis                | Complements Ruff for thorough linting.          |
|                            | Pyright                                  | Latest stable             | Static type checker (configured for strict mode)          | Ensures type safety and code reliability.      |
| **Testing** | Pytest                                   | Latest stable             | Testing framework                                           | Powerful and flexible for unit/integration tests. |
|                            | pytest-cov                               | Latest stable             | Pytest plugin for code coverage measurement               | Ensures test coverage targets are met.          |
| **CI/CD** | GitHub Actions                           | N/A                       | Continuous Integration/Deployment platform                  | Based on existing `.github/workflows`.       |
| **Version Control** | Git                                      | N/A                       | Distributed version control system                          | Standard for source code management.                       |

**Notes on Versions:**

* For libraries like `httpx-sse`, `uv`, `pre-commit`, `Ruff`, `isort`, `Pylint`, `Pyright`, `Pytest`, and `pytest-cov`, "Latest stable" implies using the most recent stable version at the time of development or dependency updates. For more predictable AI agent behavior during implementation, we should aim to pin these to specific versions (e.g., `httpx-sse==X.Y.Z`) in `pyproject.toml` once established.

This project is a standalone server application. Categories like "Databases," "Cloud Platform," or specific "Cloud Services" are not directly applicable to the `fabric-mcp` server itself, as it's designed to be deployed as a process and does not have its own persistent storage, relying on the Fabric API for data.
