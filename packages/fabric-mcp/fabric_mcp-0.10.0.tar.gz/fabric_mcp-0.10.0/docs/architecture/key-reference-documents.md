# Key Reference Documents

The following documents provide essential context, requirements, and background information for the Fabric MCP Server architecture:

1. **Product Requirements Document (PRD):**
      * Location: `docs/PRD/index.md` (or the user-provided PRD file)
      * Description: Defines the project goals, objectives, functional and non-functional requirements, user interaction goals, technical assumptions, and MVP scope for the Fabric MCP Server. This is the foundational document driving the architecture.
2. **Developer Experience (DX) and Operational Experience (OpX) Interaction Specification:**
      * Location: `docs/design-architecture/index.md` (or the user-provided file)
      * Description: Details the command-line interface (CLI) design, Model Context Protocol (MCP) tool interaction conventions, target user personas, and overall usability goals for technical users of the server.
3. **Fabric AI Framework (Daniel Miessler):**
      * Location: [https://github.com/danielmiessler/fabric](https://github.com/danielmiessler/fabric)
      * Description: The official GitHub repository for the open-source Fabric AI framework. This is the system the Fabric MCP Server integrates with. Its documentation and source code (especially the `restapi` package) are key references for understanding the behavior and API of `fabric --serve`.
4. **Model Context Protocol (MCP) Specification:**
      * Location: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
      * Description: The official specification for the Model Context Protocol. This defines the communication standard that the Fabric MCP Server implements for interacting with MCP clients. The version referenced in `design.md` (which is `docs/design.md` in the provided file structure) is 2025-03-26.
5. **Project README:**
      * Location: `README.md`
      * Description: Provides a high-level overview of the Fabric MCP Server project, setup instructions, configuration details, and links to other important resources.
6. **Contribution Guidelines:**
      * Location: `docs/contributing.md`, `docs/contributing-detailed.md`, `docs/contributing-cheatsheet.md`
      * Description: Outline the development workflow, code style, testing practices, and commit guidelines for contributors to the project.
