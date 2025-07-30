# Shared Types

```python
from arcadepy.types import AuthorizationContext, AuthorizationResponse, Error
```

# Auth

Types:

```python
from arcadepy.types import AuthRequest
```

Methods:

- <code title="post /v1/auth/authorize">client.auth.<a href="./src/arcadepy/resources/auth.py">authorize</a>(\*\*<a href="src/arcadepy/types/auth_authorize_params.py">params</a>) -> <a href="./src/arcadepy/types/shared/auth_authorization_response.py">AuthorizationResponse</a></code>
- <code title="get /v1/auth/status">client.auth.<a href="./src/arcadepy/resources/auth.py">status</a>(\*\*<a href="src/arcadepy/types/auth_status_params.py">params</a>) -> <a href="./src/arcadepy/types/shared/auth_authorization_response.py">AuthorizationResponse</a></code>

# Health

Types:

```python
from arcadepy.types import HealthSchema
```

Methods:

- <code title="get /v1/health">client.health.<a href="./src/arcadepy/resources/health.py">check</a>() -> <a href="./src/arcadepy/types/health_schema.py">HealthSchema</a></code>

# Chat

Types:

```python
from arcadepy.types import ChatMessage, ChatRequest, ChatResponse, Choice, Usage
```

## Completions

Methods:

- <code title="post /v1/chat/completions">client.chat.completions.<a href="./src/arcadepy/resources/chat/completions.py">create</a>(\*\*<a href="src/arcadepy/types/chat/completion_create_params.py">params</a>) -> <a href="./src/arcadepy/types/chat_response.py">ChatResponse</a></code>

# Tools

Types:

```python
from arcadepy.types import (
    AuthorizeToolRequest,
    ExecuteToolRequest,
    ExecuteToolResponse,
    ToolDefinition,
    ToolExecution,
    ToolExecutionAttempt,
    ValueSchema,
)
```

Methods:

- <code title="get /v1/tools">client.tools.<a href="./src/arcadepy/resources/tools/tools.py">list</a>(\*\*<a href="src/arcadepy/types/tool_list_params.py">params</a>) -> <a href="./src/arcadepy/types/tool_definition.py">SyncOffsetPage[ToolDefinition]</a></code>
- <code title="post /v1/tools/authorize">client.tools.<a href="./src/arcadepy/resources/tools/tools.py">authorize</a>(\*\*<a href="src/arcadepy/types/tool_authorize_params.py">params</a>) -> <a href="./src/arcadepy/types/shared/authorization_response.py">AuthorizationResponse</a></code>
- <code title="post /v1/tools/execute">client.tools.<a href="./src/arcadepy/resources/tools/tools.py">execute</a>(\*\*<a href="src/arcadepy/types/tool_execute_params.py">params</a>) -> <a href="./src/arcadepy/types/execute_tool_response.py">ExecuteToolResponse</a></code>
- <code title="get /v1/tools/{name}">client.tools.<a href="./src/arcadepy/resources/tools/tools.py">get</a>(name, \*\*<a href="src/arcadepy/types/tool_get_params.py">params</a>) -> <a href="./src/arcadepy/types/tool_definition.py">ToolDefinition</a></code>

## Scheduled

Types:

```python
from arcadepy.types.tools import ScheduledGetResponse
```

Methods:

- <code title="get /v1/scheduled_tools">client.tools.scheduled.<a href="./src/arcadepy/resources/tools/scheduled.py">list</a>(\*\*<a href="src/arcadepy/types/tools/scheduled_list_params.py">params</a>) -> <a href="./src/arcadepy/types/tool_execution.py">SyncOffsetPage[ToolExecution]</a></code>
- <code title="get /v1/scheduled_tools/{id}">client.tools.scheduled.<a href="./src/arcadepy/resources/tools/scheduled.py">get</a>(id) -> <a href="./src/arcadepy/types/tools/scheduled_get_response.py">ScheduledGetResponse</a></code>

## Formatted

Methods:

- <code title="get /v1/formatted_tools">client.tools.formatted.<a href="./src/arcadepy/resources/tools/formatted.py">list</a>(\*\*<a href="src/arcadepy/types/tools/formatted_list_params.py">params</a>) -> SyncOffsetPage[object]</code>
- <code title="get /v1/formatted_tools/{name}">client.tools.formatted.<a href="./src/arcadepy/resources/tools/formatted.py">get</a>(name, \*\*<a href="src/arcadepy/types/tools/formatted_get_params.py">params</a>) -> object</code>

# Workers

Types:

```python
from arcadepy.types import (
    CreateWorkerRequest,
    UpdateWorkerRequest,
    WorkerHealthResponse,
    WorkerResponse,
)
```

Methods:

- <code title="post /v1/workers">client.workers.<a href="./src/arcadepy/resources/workers.py">create</a>(\*\*<a href="src/arcadepy/types/worker_create_params.py">params</a>) -> <a href="./src/arcadepy/types/worker_response.py">WorkerResponse</a></code>
- <code title="patch /v1/workers/{id}">client.workers.<a href="./src/arcadepy/resources/workers.py">update</a>(id, \*\*<a href="src/arcadepy/types/worker_update_params.py">params</a>) -> <a href="./src/arcadepy/types/worker_response.py">WorkerResponse</a></code>
- <code title="get /v1/workers">client.workers.<a href="./src/arcadepy/resources/workers.py">list</a>(\*\*<a href="src/arcadepy/types/worker_list_params.py">params</a>) -> <a href="./src/arcadepy/types/worker_response.py">SyncOffsetPage[WorkerResponse]</a></code>
- <code title="delete /v1/workers/{id}">client.workers.<a href="./src/arcadepy/resources/workers.py">delete</a>(id) -> None</code>
- <code title="get /v1/workers/{id}">client.workers.<a href="./src/arcadepy/resources/workers.py">get</a>(id) -> <a href="./src/arcadepy/types/worker_response.py">WorkerResponse</a></code>
- <code title="get /v1/workers/{id}/health">client.workers.<a href="./src/arcadepy/resources/workers.py">health</a>(id) -> <a href="./src/arcadepy/types/worker_health_response.py">WorkerHealthResponse</a></code>
- <code title="get /v1/workers/{id}/tools">client.workers.<a href="./src/arcadepy/resources/workers.py">tools</a>(id, \*\*<a href="src/arcadepy/types/worker_tools_params.py">params</a>) -> <a href="./src/arcadepy/types/tool_definition.py">SyncOffsetPage[ToolDefinition]</a></code>
