# Coding Standards

These standards are mandatory for all code generation by AI agents and human developers. Deviations are not permitted unless explicitly approved and documented as an exception in this section or a linked addendum.

* **Primary Language & Runtime:** Python >=3.11 with CPython (as per Definitive Tech Stack Selections).
* **Style Guide & Linter:**
  * **Tools:** `Ruff` for formatting and primary linting, `Pylint` for additional static analysis, `isort` for import sorting (often managed via Ruff). `Pyright` for static type checking in strict mode.
  * **Configuration:**
    * Ruff: Configured via `.ruff.toml` and/or `pyproject.toml`.
    * Pylint: Configured via `.pylintrc`.
    * isort: Configured in `pyproject.toml` (often via `[tool.ruff.lint.isort]`).
    * Pyright: Configured in `pyproject.toml` (under `[tool.pyright]`) for strict mode.
  * **Enforcement:** Linter rules are mandatory and must be enforced by `pre-commit` hooks and CI checks.
* **Naming Conventions:**
  * Variables: `snake_case`
  * Functions/Methods: `snake_case`
  * Classes/Types/Interfaces: `PascalCase` (e.g., `MyClass`, `FabricPatternDetail`)
  * Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
  * Files: `snake_case.py` (e.g., `api_client.py`)
  * Modules/Packages: `snake_case` (e.g., `fabric_mcp`)
* **File Structure:** Adhere strictly to the layout defined in the "[Project Structure](https://www.google.com/search?q=%23project-structure)" section of this document.
* **Unit Test File Organization:**
  * Location: Unit test files will be located in the `tests/unit/` directory, mirroring the `src/fabric_mcp/` package structure where appropriate.
  * Naming: Test files must be prefixed with `test_` (e.g., `test_api_client.py`, `test_core.py`). Test functions within these files must also be prefixed with `test_`.
* **Asynchronous Operations:**
  * Always use `async` and `await` for asynchronous I/O operations (e.g., `httpx` calls, FastMCP stream handling).
  * Ensure proper error handling for `async` operations, including `try...except` blocks for `async` calls.
* **Type Safety:**
  * **Type Hinting:** Comprehensive type hints are mandatory for all new functions, methods (including `self` and `cls` arguments), and variable declarations. Utilize Python's `typing` module extensively.
  * **Strict Mode:** `Pyright` (or MyPy if also used by linters) will be configured for strict type checking. All type errors reported must be resolved.
  * **Type Definitions:** Complex or shared type aliases and `TypedDict` definitions should be clearly defined, potentially in a dedicated `types.py` module within relevant packages if they are widely used, or co-located if specific to a module.
  * **Policy on `Any`:** Usage of `typing.Any` is strongly discouraged and requires explicit justification in comments if deemed absolutely necessary. Prefer more specific types like `object`, `Callable[..., T]`, or `TypeVar`.
* **Comments & Documentation:**
  * **Code Comments:** Explain *why*, not *what*, for complex or non-obvious logic. Avoid redundant comments. Use Python docstrings (Google or NumPy style preferred, to be consistent) for all public modules, classes, functions, and methods. Docstrings must describe purpose, arguments, return values, and any exceptions raised.
  * **READMEs:** Each significant module or component might have a brief README if its setup or usage is complex and not self-evident from its docstrings or the main project `README.md`.
* **Dependency Management:**
  * **Tool:** `uv` is used for package and environment management.
  * **Configuration:** Dependencies are defined in `pyproject.toml`. The `uv.lock` file ensures reproducible builds.
  * **Policy on Adding New Dependencies:** New dependencies should be carefully considered for their necessity, maintenance status, security, and license. They must be added to `pyproject.toml` with specific, pinned versions where possible, or using conservative version specifiers (e.g., `~=` for patch updates, `^=` for minor updates if strictly following SemVer and API stability is expected).
  * **Versioning Strategy:** Prefer pinned versions for all dependencies to ensure build reproducibility and avoid unexpected breaking changes, especially crucial for AI agent code generation.

## Detailed Language & Framework Conventions

### Python Specifics

* **Immutability:**
  * Prefer immutable data structures where practical (e.g., use tuples instead of lists for sequences that should not change).
  * Be cautious with mutable default arguments in functions/methods; use `None` as a default and initialize mutable objects inside the function body if needed.
* **Functional vs. OOP:**
  * Employ classes for representing entities (like MCP tool request/response models if complex), services (like `FabricApiClient`), and managing state if necessary.
  * Use functions for stateless operations and utility tasks.
  * Utilize list comprehensions and generator expressions for concise and readable data transformations over `map` and `filter` where appropriate.
* **Error Handling Specifics (Python Exceptions):**
  * Always raise specific, custom exceptions inheriting from a base `FabricMCPError` (which itself inherits from `Exception`) for application-specific error conditions. This allows for cleaner `try...except` blocks. Example: `class FabricApiError(FabricMCPError): pass`.
  * Use `try...except...else...finally` blocks appropriately for robust error handling and resource cleanup.
  * Avoid broad `except Exception:` or bare `except:` clauses. If used, they must re-raise the exception or log detailed information and handle the situation specifically.
* **Resource Management:**
  * Always use `with` statements (context managers) for resources that need to be reliably closed or released, such as file operations (if any) or network connections managed by `httpx` if not handled by its higher-level client context management.
* **Type Hinting (Reiteration & Emphasis):**
  * All new functions and methods *must* have full type hints for all arguments (including `self`/`cls`) and return values.
  * Run `Pyright` in strict mode as part of CI/linting to enforce this.
* **Logging Specifics (Python `logging` module with `RichHandler`):**
  * Use the standard Python `logging` module, configured with `RichHandler` for console output to leverage `rich` formatting capabilities.
  * Acquire loggers via `logging.getLogger(__name__)`.
  * Log messages should provide context as outlined in the "Error Handling Strategy." Do not log sensitive information like API keys.
* **Framework Idioms:**
  * **Click:** Utilize decorators (`@click.command()`, `@click.option()`, `@click.argument()`) for defining CLI commands and options. Structure CLI logic clearly within command functions.
  * **FastMCP:** Follow FastMCP's patterns for registering tools and handling request/response cycles. If FastMCP provides specific hooks or extension points, they should be used as intended (potentially in the proposed `server_hooks.py`).
  * **httpx:** Use an `httpx.AsyncClient` instance, potentially as a singleton or managed context, for making calls to the Fabric API, especially for connection pooling and consistent configuration (headers, timeouts).
* **Key Library Usage Conventions:**
  * When using `httpx`, explicitly set connect and read timeouts for all requests to the Fabric API.
  * Ensure proper handling of `httpx.Response.raise_for_status()` or manual status code checking for API responses.
* **Code Generation Anti-Patterns to Avoid (for AI Agent Guidance):**
  * Avoid overly nested conditional logic (aim for a maximum of 2-3 levels; refactor complex conditions into separate functions or use other control flow patterns).
  * Avoid single-letter variable names unless they are trivial loop counters (e.g., `i`, `j`, `k` in simple loops) or very common idioms in a small, obvious scope.
  * Do not write code that bypasses the intended use of chosen libraries (e.g., manually constructing multipart form data if `httpx` can handle it).
  * Ensure all string formatting for user-facing messages or logs uses f-strings or the `logging` module's deferred formatting; avoid manual string concatenation with `+` for building messages.
