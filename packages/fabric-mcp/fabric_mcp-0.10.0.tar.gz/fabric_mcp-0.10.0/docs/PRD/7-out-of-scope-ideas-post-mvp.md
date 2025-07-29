# 7. Out of Scope Ideas Post MVP

- **Write/Update Operations for Fabric Configuration via MCP:** The current `fabric_get_configuration` tool is read-only. An MCP tool to modify Fabric's configuration (potentially using Fabric API's POST `/config/update` endpoint) is out of scope for MVP.
- **Direct MCP Tools for Specialized Fabric Features:** Fabric's CLI offers many specific functionalities (e.g., YouTube processing, Jina AI scraping, detailed context/session management beyond simple naming). Direct MCP tool mappings for these specialized features are out of scope for this MVP, which focuses on core pattern interaction and information retrieval.
- **Advanced `fabric_run_pattern` Variable Types:** While the MVP supports string-to-string variables for patterns, future enhancements could explore richer structured data types if Fabric's capabilities evolve in that direction.
- **More Advanced MCP Features from FastMCP:** Capabilities like client-side LLM sampling initiated by the server or richer resource interactions are not planned for this MVP.
- **Enhanced Filtering/Searching for List Tools:** Adding server-side filtering or searching capabilities to `fabric_list_patterns` and `fabric_list_strategies` is deferred; current implementation relies on clients to handle large lists.
