# Infrastructure and Deployment Overview

The Fabric MCP Server is designed as a standalone Python application, intended to be flexible in its deployment to suit various user environments.

* **Deployment Model:** The server is deployed as a single, self-contained process. It does not require a complex distributed infrastructure for its own operation. Users will typically run it as a background service or a command-line application on a machine that has network access to the target `fabric --serve` instance.
* **Installation:**
  * The primary distribution method is via PyPI (Python Package Index). Users can install it using `pip install fabric-mcp` or `uv pip install fabric-mcp`.
  * For development, it can be run directly from the source code within a virtual environment managed by `uv`.
* **Runtime Environment:**
  * Requires a Python runtime (>=3.11, as specified in the tech stack).
  * Necessary environment variables (`FABRIC_BASE_URL`, `FABRIC_API_KEY`, `FABRIC_MCP_LOG_LEVEL`) must be configured in the execution environment.
* **Execution:**
  * The server is launched via its command-line interface (`fabric-mcp`), which is built using `click`.
  * The CLI allows users to specify the MCP transport mode (`stdio`, `sse`, `http-streamable`) and associated parameters like host, port, and path for HTTP-based transports.
  * **Standard I/O Transport (`--stdio`)**: Default mode for direct integration with MCP clients that communicate via stdin/stdout.
  * **Server-Sent Events Transport (`--sse`)**: HTTP-based transport using Server-Sent Events for real-time communication.
  * **Streamable HTTP Transport (`--http-streamable`)**: Full HTTP-based transport that enables MCP clients to connect over HTTP with support for streaming operations. This transport runs a complete HTTP server that can handle multiple concurrent client connections.

## Transport Configuration

### Streamable HTTP Transport

The Streamable HTTP transport provides a complete HTTP server implementation for MCP communication:

**Basic Usage:**

```bash
# Start server with default settings (127.0.0.1:8000/mcp)
fabric-mcp --http-streamable

# Customize host, port, and endpoint path
fabric-mcp --http-streamable --host 0.0.0.0 --port 3000 --mcp-path /api/mcp
```

**Configuration Options:**

* `--host`: Server bind address (default: 127.0.0.1)
* `--port`: Server port (default: 8000)
* `--mcp-path`: MCP endpoint path (default: /mcp)

**Features:**

* Full HTTP server with concurrent client support
* Streaming operations for large responses
* Standard HTTP status codes and error handling
* Compatible with FastMCP's streamable-http transport
* Non-MCP HTTP requests receive 406 Not Acceptable responses

**Client Connection:**

MCP clients can connect using the streamable HTTP transport:

```python
from fastmcp.client.transports import StreamableHttpTransport

transport = StreamableHttpTransport("http://127.0.0.1:8000/mcp")
```

* **Cloud Agnostic:** The server itself is cloud-agnostic. It can be run on any system that supports Python, whether it's a local machine, a virtual machine in any cloud (AWS, Azure, GCP), or a containerized environment. No specific cloud services are mandated for its core operation.
* **Infrastructure as Code (IaC):** Not directly applicable for the server application itself, as it's a process rather than managed infrastructure. If users deploy it within a larger system managed by IaC (e.g., as part of an EC2 instance setup or a Kubernetes pod definition), that would be external to this project's direct scope.
* **CI/CD:**
  * GitHub Actions are used for continuous integration (running tests, linters) on code pushes/pull requests.
  * GitHub Actions are also configured for publishing the package to PyPI (e.g., via `publish.yml` in `.github/workflows/`).
* **Environments:**
  * **Development:** Local machine with `uv` managing dependencies.
  * **Production/User Deployment:** Any system meeting the Python runtime requirements, where the user installs the package and runs the `fabric-mcp` command.
* **Rollback Strategy:** For the application itself, rollback would typically involve deploying a previous version of the `fabric-mcp` package from PyPI if an issue is found with a new release.
* **Future Considerations (Post-MVP):** Dockerization could be considered in the future to simplify deployment further, similar to the main Fabric project. This would involve creating a `Dockerfile` and publishing container images.
