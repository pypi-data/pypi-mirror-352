from __future__ import annotations
from contextlib import AbstractContextManager
from typing import Iterator, Iterable

from ._http import _HTTP
from ._models import CompletionRequest, CompletionResponse, Message, ToolSpec, ToolChoice

# Models that support tool calling
SUPPORTED_TOOL_MODELS = {
    "gpt-4.1",
    "gpt-4.1-mini", 
    "gpt-4.1-nano",
    "astar-gpt-4.1",
}


class CompletionEndpoint:
    """
    Completion endpoint that handles chat completions with optional tool calling.
    """

    def __init__(self, http: _HTTP):
        self._http = http

    def __call__(
        self,
        *,
        messages: Iterable[dict | Message],
        model: str,
        stream: bool = False,
        tools: Iterable[dict | ToolSpec] | None = None,
        tool_choice: str | dict | ToolChoice | None = None,
        **model_kwargs,
    ) -> CompletionResponse | Iterator[CompletionResponse]:
        # Capability gate for tool calling
        if tools and model not in SUPPORTED_TOOL_MODELS:
            raise ValueError(
                f"Model '{model}' cannot accept tools. "
                f"Valid tool models: {', '.join(sorted(SUPPORTED_TOOL_MODELS))}"
            )

        # Allow plain dicts or pydantic Message instances
        msgs = [
            m if isinstance(m, Message) else Message(**m)
            for m in messages
        ]
        
        # Convert tools to ToolSpec instances if provided
        tool_specs = None
        if tools:
            tool_specs = [t if isinstance(t, ToolSpec) else ToolSpec(**t) for t in tools]
        
        req = CompletionRequest(
            model=model,
            messages=msgs,
            stream=stream,
            tools=tool_specs,
            tool_choice=tool_choice,
            **model_kwargs,
        )

        payload = req.model_dump(exclude_none=True)

        if stream:
            return self._streaming_post(payload)

        return CompletionResponse.model_validate(
            self._http.post("/v1/chat/completions", payload)
        )

    def _streaming_post(
        self, payload: dict
    ) -> Iterator[CompletionResponse]:
        # Server-Sent Events loop for the new endpoint
        url = self._http.BASE_URL + "/v1/chat/completions"
        with self._http._client.stream("POST", url, json=payload) as r:
            for line in r.iter_lines():
                if line == b"data: [DONE]":
                    break
                if line.startswith(b"data: "):
                    yield CompletionResponse.model_validate_json(line[6:])


class CreateNamespace:
    """
    Namespace for creation endpoints (e.g., client.create.completion)
    """
    
    def __init__(self, http: _HTTP):
        self.completion = CompletionEndpoint(http)


class AstarClient(AbstractContextManager):
    """
    >>> from AstarCloud import AstarClient
    >>> client = AstarClient(api_key="sk-...")
    >>> resp = client.create.completion(
    ...     messages=[{"role": "user", "content": "Hello"}],
    ...     model="gpt-4.1"
    ... )
    """

    def __init__(self, api_key: str, *, timeout: float = 30.0):
        self._http = _HTTP(api_key, timeout=timeout)
        self.create = CreateNamespace(self._http)

    def bind_tools(
        self,
        tools: Iterable[dict | ToolSpec],
        tool_choice: str | dict | ToolChoice = "auto",
    ) -> "AstarClient":
        """
        Create a new client instance with bound tools that will be used
        automatically for all completion requests.
        """
        return _BoundToolClient(self, tools=list(tools), tool_choice=tool_choice)

    def __exit__(self, exc_type, exc, tb):
        self._http.close()


class _BoundToolClient(AstarClient):
    """
    A client instance that has tools bound to it, automatically adding
    them to completion requests.
    """
    
    def __init__(self, parent, *, tools, tool_choice):
        super().__init__(
            api_key=parent._http._headers["Authorization"].split(" ")[1], 
            timeout=parent._http._timeout
        )
        self._http = parent._http  # share connection pool
        self._tools = tools
        self._tool_choice = tool_choice
        # Override the create namespace to inject tools
        self.create = _BoundCreateNamespace(self._http, self._tools, self._tool_choice)


class _BoundCreateNamespace(CreateNamespace):
    """
    Create namespace that automatically injects bound tools.
    """
    
    def __init__(self, http: _HTTP, tools, tool_choice):
        super().__init__(http)
        self._bound_tools = tools
        self._bound_tool_choice = tool_choice
        # Override the completion endpoint to inject tools
        self.completion = _BoundCompletionEndpoint(
            http, self._bound_tools, self._bound_tool_choice
        )


class _BoundCompletionEndpoint(CompletionEndpoint):
    """
    Completion endpoint that automatically injects bound tools.
    """
    
    def __init__(self, http: _HTTP, tools, tool_choice):
        super().__init__(http)
        self._bound_tools = tools
        self._bound_tool_choice = tool_choice
    
    def __call__(self, *args, **kwargs):
        # Inject bound tools if not already provided
        kwargs.setdefault("tools", self._bound_tools)
        kwargs.setdefault("tool_choice", self._bound_tool_choice)
        return super().__call__(*args, **kwargs)
