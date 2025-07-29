from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict


# -- Tool-calling models ----------------------------------
class ToolSpec(BaseModel):
    type: Literal["function"] = "function"
    function: Dict[str, Any]


class ToolChoice(BaseModel):
    type: Literal["function"] = "function"
    function: Dict[str, str]         # {"name": "my_tool"}


class ToolCall(BaseModel):
    id: str
    type: Literal["function"]
    function: Dict[str, str]         # {"name": "my_tool", "arguments": "..."}


# -- Updated Message model ----------------------------------
class Message(BaseModel):
    role: str
    content: Optional[str] = None  # Allow None when tool calls are present


# -- Updated request/response models -------------------------
class CompletionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")  # catch-all for extra kwargs
    
    model: str
    messages: List[Message]
    stream: bool = False
    # New fields for tool calling
    tools: Optional[List[ToolSpec]] = None
    tool_choice: Optional[Union[str, ToolChoice]] = None


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str]
    # New field for tool calls
    tool_calls: Optional[List[ToolCall]] = None


class Usage(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost_usd: Optional[float] = None  # Allow None for cost_usd


class CompletionResponse(BaseModel):
    id: str
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Usage] = None
