# Fabric MCP Server Documentation Index

This document serves as the central catalog for all key documentation related to the Fabric MCP Server project.

## Core Project Documents

### [Product Requirements Document (PRD)](./PRD/index.md)

Defines the project goals, objectives, functional and non-functional requirements, user interaction goals, technical assumptions, and MVP scope.

### [Architecture Document](./architecture/index.md)

Outlines the overall project architecture, including components, patterns, technology stack, and key design decisions. *(This is the main source document before sharding)*

### [Developer Experience (DX) and Operational Experience (OpX) Interaction Specification](./design-architecture/index.md)

Details the command-line interface (CLI) design, Model Context Protocol (MCP) tool interaction conventions, target user personas, and overall usability goals.

## Project Epics

### [Epic 1: Foundational Server Setup & Basic Operations](./PRD/epic-overview/epic-1-foundational-server-setup-basic-operations.md)

Details the work to establish a runnable Fabric MCP server with essential CLI capabilities, basic MCP communication, connectivity to Fabric, configuration handling, packaging, and support for all transport layers.

### [Epic 2: Fabric Pattern Discovery & Introspection](./PRD/epic-overview/epic-2-fabric-pattern-discovery-introspection.md)

Covers enabling MCP clients to dynamically discover available Fabric patterns and retrieve detailed information like system prompts and metadata.

### [Epic 3: Core Fabric Pattern Execution with Strategy & Parameter Control](./PRD/epic-overview/epic-3-core-fabric-pattern-execution-with-strategy-parameter-control.md)

Focuses on allowing MCP clients to execute Fabric patterns, apply strategies, control execution parameters (model, temperature, variables, attachments), and receive output, including streaming.

### [Epic 4: Fabric Environment & Configuration Insights](./PRD/epic-overview/epic-4-fabric-environment-configuration-insights.md)

Describes providing MCP clients with the ability to list available Fabric models and securely retrieve the current Fabric operational configuration.

## Architectural Granules (Sharded from Architecture Document)

### [API Reference](./architecture/api-reference.md)

Details the external APIs consumed by the server (primarily Fabric REST API) and the internal MCP tools provided by the server, including their endpoints, parameters, and schemas.

### [Component View](./architecture/component-view.md)

Describes the major logical components of the system, their responsibilities, interactions, and the architectural design patterns adopted. Includes component diagrams.

### [Core Workflows & Sequence Diagrams](./architecture/core-workflow-sequence-diagrams.md)

Illustrates key operational and interaction flows within the system using sequence diagrams, such as tool discovery, pattern execution (streaming and non-streaming), and server startup.

### [Data Models](./architecture/data-models.md)

Explains that the server is stateless and data models are primarily defined by the MCP tool schemas and Fabric API schemas, referencing the API Reference document for details.

### [Infrastructure and Deployment Overview](./architecture/infrastructure-and-deployment-overview.md)

Details how the Fabric MCP Server is intended to be deployed, installed, and operated, including runtime environments and CI/CD.

### [Key Reference Documents (from Architecture)](./PRD/6-key-reference-documents.md)

Lists the primary documents that informed the architecture and are critical for understanding its context. *(Note: This refers to the sharded version of this section from the main architecture document).*

### Operational Guidelines

Consolidates coding standards, the overall testing strategy, error handling strategy, and security best practices for the project.

- [Coding Standards](./architecture/coding-standards.md)
- [Testing Strategy](./architecture/overall-testing-strategy.md)
- [Error Handling Strategy](./architecture/error-handling-strategy.md)
- [Security Best Practices](./architecture/security-best-practices.md)

### [Project Structure (from Architecture)](./architecture/project-structure.md)

Defines the project's folder and file structure, including key directories for source code, tests, and documentation.

### [Technology Stack](./architecture/definitive-tech-stack-selections.md)

Provides the definitive list of technology choices for the project, including languages, frameworks, libraries, and development tooling, along with their versions.

## Contribution & Development Setup

These guides summarize the project setup, including Python version, key development tools (`uv`, `ruff`, `pytest`, `hatch`, `pre-commit`, `pnpm` for MCP Inspector), and essential `make` commands.

### [Main Contribution Guidelines](./contributing.md)

Outlines the primary guidelines for contributing to the project, including development workflow and code style.

### [Detailed Contribution Guide](./contributing-detailed.md)

Provides an in-depth guide to contributing, covering advanced topics, tool configurations, and best practices.

### [Contributing Cheatsheet](./contributing-cheatsheet.md)

A micro-summary of the development workflow for quick reference.

## Other

### [Original Documents](./source/index.md)

The initial design document that informed the PRD and subsequent planning, amd the original PRD. Architecture and Design Architecture documents.

### [PM, PO, and Architect Checklists](./checklists/index.md)

The various checklists for the MVP development.
