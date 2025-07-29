# Overall Testing Strategy

This section outlines the project's comprehensive testing strategy, which all AI-generated and human-written code must adhere to. It complements the testing tools listed in the "Definitive Tech Stack Selections."

* **Tools:**

  * **Primary Testing Framework:** `Pytest`.
  * **Code Coverage:** `pytest-cov`.
  * **Mocking:** Python's built-in `unittest.mock` library.

* **Unit Tests:**

  * **Scope:** Test individual functions, methods, and classes within the `fabric_mcp` package in isolation. Focus will be on business logic within MCP tool implementations (`core.py`), utility functions (`utils.py`), CLI argument parsing (`cli.py`), API response parsing in `api_client.py`, and transport configurations (`server_transports.py`).
  * **Location & Naming:** As defined in "Coding Standards": located in `tests/unit/`, mirroring the `src/fabric_mcp/` structure, with filenames `test_*.py` and test functions prefixed with `test_`.
  * **Mocking/Stubbing:** All external dependencies, such as calls made by `httpx` within the `Fabric API Client`, file system operations (if any), and system time (if relevant for specific logic), MUST be mocked using `unittest.mock`.
  * **AI Agent Responsibility:** The AI Agent tasked with developing or modifying code MUST generate comprehensive unit tests covering all public methods/functions, significant logic paths (including conditional branches), common edge cases, and expected error conditions for the code they produce.

* **Integration Tests:**

  * **Scope:**
        1. **Internal Component Interaction:** Test the interaction between major internal components, primarily focusing on the flow from `MCP Tool Implementations (core.py)` to the `Fabric API Client (api_client.py)`. This involves verifying that MCP tool logic correctly invokes the API client and processes its responses (both success and error), with the actual Fabric API HTTP calls being mocked.
        2. **Live Fabric API Interaction:** Validate the Fabric MCP Server's interaction with a live (locally running) `fabric --serve` instance. These tests will cover the successful execution of each defined MCP tool against the live Fabric backend, verifying correct request formation to Fabric and response parsing from Fabric, including SSE stream handling.
  * **Location:** `tests/integration/`.
  * **Environment:** For tests requiring a live Fabric API, clear instructions will be provided (e.g., in a test-specific README or a contributing guide) on how to run `fabric --serve` locally with any necessary patterns or configurations for the tests to pass.
  * **AI Agent Responsibility:** The AI Agent may be tasked with generating integration tests for key MCP tool functionalities, especially those validating the interaction with the (mocked or live) Fabric API.

* **End-to-End (E2E) Tests:**

  * **Scope:** Simulate an MCP client interacting with the Fabric MCP Server across all supported transports (stdio, Streamable HTTP, SSE). These tests will cover common user workflows for each defined MCP tool, ensuring the entire system works as expected from the client's perspective through to the Fabric API (which might be mocked at its boundary for some E2E scenarios to ensure deterministic behavior, or live for full-stack validation).
  * **Tools:** This may involve creating a lightweight test MCP client script using Python (e.g., leveraging the `modelcontextprotocol` library directly) or using existing MCP client development tools if suitable for test automation.
  * **AI Agent Responsibility:** The AI Agent may be tasked with generating E2E test stubs or scripts based on user stories or BDD scenarios, focusing on critical happy paths and key error scenarios for each transport.

* **Test Coverage:**

  * **Target:** A minimum of 90% code coverage (line and branch where applicable) for unit tests, as measured by `pytest-cov`. While this is a quantitative target, the qualitative aspect of tests (testing meaningful behavior and edge cases) is paramount.
  * **Measurement:** Coverage reports will be generated using `pytest-cov` and checked as part of the CI process.

* **Mocking/Stubbing Strategy (General):**

  * Prefer using `unittest.mock.patch` or `MagicMock` for replacing dependencies.
  * Strive for tests that are fast, reliable, and isolated. Test doubles (stubs, fakes, mocks) should be used judiciously to achieve this isolation without making tests overly brittle to implementation details of mocked components.

* **Test Data Management:**

  * Test data (e.g., sample pattern names, mock API request/response payloads, MCP message structures) will primarily be managed using Pytest fixtures or defined as constants within the respective test modules.
  * For more complex data structures, consider using helper functions or small, local data files (e.g., JSON files in a test assets directory) loaded by fixtures.
