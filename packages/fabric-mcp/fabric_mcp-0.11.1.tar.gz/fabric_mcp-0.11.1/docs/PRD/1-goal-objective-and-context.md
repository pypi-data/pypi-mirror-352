# 1. Goal, Objective and Context

## Goal

The primary goal of the Fabric MCP Server project is to seamlessly integrate the open-source [Fabric AI framework by Daniel Miessler][fabricGithubLink] with any [Model Context Protocol (MCP)][MCP] compatible application. This will empower users to leverage Fabric's powerful patterns, models, and configurations directly within their existing MCP-enabled environments (like IDE extensions or chat interfaces) without context switching, leading to enhanced developer productivity and more sophisticated AI-assisted interactions.

## Objective

- To develop a standalone server application that acts as a bridge between Fabric's REST API (exposed by `fabric --serve`) and MCP clients.
- To translate MCP requests into corresponding Fabric API calls and relay Fabric's responses (including streaming) back to the MCP client.
- To expose core Fabric functionalities like listing patterns, getting pattern details, running patterns, listing models/strategies, and retrieving configuration through standardized MCP tools.
- To adhere to the open MCP standard for AI tool integration, fostering interoperability.

## Context

The Fabric MCP Server addresses the need for integrating Fabric's specialized prompt engineering capabilities and AI workflows into diverse LLM interaction environments. It aims to eliminate the current barrier of potentially needing a separate interface for Fabric, thereby streamlining workflows and directly enhancing user productivity and the quality of AI assistance within their preferred tools. This project leverages the existing Fabric CLI and its REST API without requiring modifications to the core Fabric codebase. It is important to note that this project refers to the [open-source Fabric AI framework by Daniel Miessler][fabricGithubLink], not other software products with similar names.
