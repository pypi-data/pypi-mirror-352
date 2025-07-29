# API Reference

## External APIs Consumed

This section details the external APIs that the Fabric MCP Server interacts with. The primary external dependency is the Fabric REST API.

### Fabric REST API

* **Purpose:** The Fabric MCP Server consumes this API to leverage the functionalities of a running `fabric --serve` instance, such as pattern execution, listing available patterns, models, strategies, and retrieving configuration.

* **Base URL(s):**

  * Configured via the `FABRIC_BASE_URL` environment variable.
  * Default: `http://127.0.0.1:8080`.

* **Authentication:**

  * Method: API Key in Header. Header Name: `X-API-Key`.
  * The key is provided via the `FABRIC_API_KEY` environment variable. If not set, authentication is not attempted by `fabric-mcp` (though `fabric --serve` might still require it if it was started with an API key).

* **Key Endpoints Used (Based on `fabric --serve` output and Go source code):**

    1. **Endpoint:** `POST /chat`

          * **Description:** Executes a Fabric pattern, potentially with streaming output. This is the primary endpoint for the `fabric_run_pattern` MCP tool.
          * **Request Body Schema (`ChatRequest` from `chat.go`):**

            ```json
            {
              "prompts": [
                {
                  "userInput": "string",
                  "vendor": "string", // Optional, for model selection
                  "model": "string", // Optional, specific model name
                  "contextName": "string", // Optional
                  "patternName": "string", // Name of the Fabric pattern to run
                  "strategyName": "string" // Optional strategy name
                }
              ],
              "language": "string", // Optional
              // Embedded common.ChatOptions from Fabric:
              "temperature": "float", // Optional
              "topP": "float", // Optional
              "frequencyPenalty": "float", // Optional
              "presencePenalty": "float", // Optional
            }
            ```

          * **Success Response (SSE Stream - `text/event-stream`):** Each event is a JSON object (`StreamResponse` from `chat.go`):

            ```json
            {
              "type": "string", // e.g., "content", "error", "complete"
              "format": "string", // e.g., "markdown", "mermaid", "plain"
              "content": "string" // The actual content chunk or error message
            }
            ```

          * **Non-Streaming Success Response:** If streaming is not used/supported by a specific call, a consolidated response would be expected (details to be confirmed, possibly a final "content" message or a different structure).
          * **Error Response Schema(s):** Errors during streaming are sent as a `StreamResponse` with `type: "error"`. Standard HTTP errors (4xx, 5xx) for request issues.

    2. **Endpoint:** `GET /patterns/names`

          * **Description:** Retrieves a list of available Fabric pattern names. Used by the `fabric_list_patterns` MCP tool.
          * **Request Parameters:** None.
          * **Success Response Schema (Code: `200 OK`):**

            ```json
            [
              "patternName1",
              "patternName2"
            ]
            ```

          * **Error Response Schema(s):** Standard HTTP errors.

    3. **Endpoint:** `GET /patterns/:name`

          * **Description:** Retrieves details for a specific Fabric pattern. Used by the `fabric_get_pattern_details` MCP tool.
          * **Request Parameters:**
              * `name` (path parameter): The name of the pattern.
          * **Success Response Schema (Code: `200 OK`):**

            ```json
            {
              "name": "string",
              "description": "string",
              "tags": ["string"],
              "system_prompt": "string",
              "user_prompt_template": "string"
            }
            ```

          * **Error Response Schema(s):** `404 Not Found` if pattern doesn't exist. Other standard HTTP errors.

    4. **Endpoint:** `GET /config`

          * **Description:** Retrieves the current Fabric operational configuration. Used by the `fabric_get_configuration` MCP tool.
          * **Request Parameters:** None.
          * **Success Response Schema (Code: `200 OK`) (`configuration.go` GetConfig response):**

            ```json
            {
              "openai": "string",
              "anthropic": "string",
              "groq": "string",
              "mistral": "string",
              "gemini": "string",
              "ollama": "string",
              "openrouter": "string",
              "silicon": "string",
              "deepseek": "string",
              "grokai": "string",
              "lmstudio": "string"
            }
            ```

          * **Error Response Schema(s):** Standard HTTP errors.

    5. **Endpoint:** `GET /models/names`

          * **Description:** Retrieves a list of configured Fabric models. Used by the `fabric_list_models` MCP tool.
          * **Request Parameters:** None.
          * **Success Response Schema (Code: `200 OK`) (`models.go` GetModelNames response):**

            ```json
            {
              "models": ["string"],
              "vendors": {
                "vendor_name": ["string"]
              }
            }
            ```

          * **Error Response Schema(s):** Standard HTTP errors.

    6. **Endpoint:** `GET /strategies`

          * **Description:** Retrieves a list of available Fabric strategies. Used by the `fabric_list_strategies` MCP tool.
          * **Request Parameters:** None.
          * **Success Response Schema (Code: `200 OK`) (JSON array of `StrategyMeta` from `strategies.go`):**

            ```json
            [
              {
                "name": "string",
                "description": "string",
                "prompt": "string"
              }
            ]
            ```

          * **Error Response Schema(s):** Standard HTTP errors.

* **Link to Official Docs:** The primary reference for Fabric is [Daniel Miessler's Fabric GitHub repository](https://github.com/danielmiessler/fabric).

A note on the `POST /chat` request: The PRD (Functional Requirements, 3. Run Pattern) mentions `variables` (map[string]string) and `attachments` (list of strings) as optional parameters for pattern execution. The `ChatRequest` struct from `chat.go` doesn't explicitly list these top-level fields.
For the architecture, we'll assume that:

1. Simple `variables` might be substituted into the `userInput` string before sending the request.
2. `attachments` might be handled by specific patterns within Fabric itself.
    Our `fabric_mcp` server will pass the `variables` and `attachments` as received in the MCP request to the `fabric_run_pattern` tool. The `api_client.py` will need a strategy to include these in the `POST /chat` request.

## Internal APIs Provided (MCP Tools)

The Fabric MCP Server provides the following tools to MCP clients. These tools adhere to the Model Context Protocol specification and allow clients to interact with the underlying Fabric instance. Error responses for these tools will follow the standard MCP error structure, providing a `type` (URN-style), `title`, and `detail` message.

1. **Tool: `fabric_list_patterns`**

      * **Description:** Retrieves a list of all available pattern names from the connected Fabric instance.
      * **Parameters:** None.
      * **Return Value:**
          * **Type:** `object`
          * **Description:** A JSON object containing a single key `patterns`.
          * **Schema:**

            ```json
            {
              "patterns": [
                "string"
              ]
            }
            ```

2. **Tool: `fabric_get_pattern_details`**

      * **Description:** Retrieves detailed information for a specific Fabric pattern by its name.
      * **Parameters:**
          * `name`: `pattern_name`
              * `type`: `string`
              * `required`: `true`
              * `description`: The exact name of the Fabric pattern.
      * **Return Value:**
          * **Type:** `object`
          * **Description:** A JSON object containing pattern details.
          * **Schema:**

            ```json
            {
              "name": "string",
              "description": "string",
              "system_prompt": "string",
              "user_prompt_template": "string",
              "tags": ["string"]
            }
            ```

      * **Errors:** Can return `urn:fabric-mcp:error:pattern-not-found`.

3. **Tool: `fabric_run_pattern`**

      * **Description:** Executes a Fabric pattern with options and optional streaming.
      * **Parameters:**
          * `name`: `pattern_name` (`string`, required)
          * `name`: `input_text` (`string`, optional)
          * `name`: `stream` (`boolean`, optional, default: `false`)
          * `name`: `model_name` (`string`, optional)
          * `name`: `strategy_name` (`string`, optional)
          * `name`: `variables` (`object` map[string]string, optional)
          * `name`: `attachments` (`array` of `string`, optional)
          * `name`: `temperature` (`number` float, optional)
          * `name`: `top_p` (`number` float, optional)
          * `name`: `presence_penalty` (`number` float, optional)
          * `name`: `frequency_penalty` (`number` float, optional)
      * **Return Value (Non-streaming, `stream: false`):**
          * **Type:** `object`
          * **Schema:**

            ```json
            {
              "output_format": "string",
              "output_text": "string"
            }
            ```

      * **Return Value (Streaming, `stream: true`):**
          * **Type:** MCP Stream. Each chunk is a JSON object:

            ```json
             {
               "type": "string", // "content", "error", "complete"
               "format": "string", // "markdown", "mermaid", "plain"
               "content": "string"
             }
            ```

          * Stream ends with MCP stream end or error (e.g., `urn:fabric-mcp:error:fabric-stream-interrupted`).

4. **Tool: `fabric_list_models`**

      * **Description:** Retrieves configured Fabric models.
      * **Parameters:** None.
      * **Return Value:**
          * **Type:** `object`
          * **Schema:**

            ```json
            {
              "all_models": ["string"],
              "models_by_vendor": {
                "vendor_name": ["string"]
              }
            }
            ```

5. **Tool: `fabric_list_strategies`**

      * **Description:** Retrieves available Fabric strategies.
      * **Parameters:** None.
      * **Return Value:**
          * **Type:** `object`
          * **Schema:**

            ```json
            {
              "strategies": [
                {
                  "name": "string",
                  "description": "string",
                  "prompt": "string"
                }
              ]
            }
            ```

6. **Tool: `fabric_get_configuration`**

      * **Description:** Retrieves Fabric's operational configuration, with sensitive values redacted.
      * **Parameters:** None.
      * **Return Value:**
          * **Type:** `object`
          * **Description:** Fabric configuration map. Sensitive keys replaced with `"[REDACTED_BY_MCP_SERVER]"`.
          * **Schema:** (Example based on Fabric's `/config` output)

            ```json
            {
              "openai_api_key": "string", // e.g., "[REDACTED_BY_MCP_SERVER]"
              "ollama_url": "string"    // e.g., "http://localhost:11434"
            }
            ```
