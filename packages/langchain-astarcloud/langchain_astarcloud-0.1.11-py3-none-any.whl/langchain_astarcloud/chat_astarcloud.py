"""AstarCloud chat model implementation for LangChain."""

from __future__ import annotations

from typing import Any, List, Mapping, Optional, Iterator, AsyncIterator

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
)
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.tools import BaseTool

from AstarCloud import AstarClient


def _to_dict(msg: BaseMessage) -> dict:
    """LangChain ➜ AstarCloud wire format"""
    if isinstance(msg, AIMessage) and msg.tool_calls:
        return {
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": msg.tool_calls,
        }
    
    # Map LangChain message types to OpenAI API role names
    role_mapping = {
        "human": "user",
        "ai": "assistant", 
        "system": "system",
        "function": "function",
        "tool": "tool"
    }
    
    role = role_mapping.get(msg.type, msg.type)
    return {"role": role, "content": msg.content}


def _from_dict(d: Mapping[str, Any]) -> AIMessage:
    """AstarCloud ➜ LangChain"""
    return AIMessage(
        content=d.get("content", ""),
        additional_kwargs={"tool_calls": d.get("tool_calls")},
    )


def _convert_langchain_tools_to_astar_format(tools: List[Any]) -> List[dict]:
    """Convert LangChain tools to AstarCloud SDK format"""
    converted_tools = []
    for tool in tools:
        if isinstance(tool, BaseTool):
            # Convert LangChain StructuredTool to dict format
            tool_dict = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.args_schema.model_json_schema() if tool.args_schema else {}
                }
            }
            converted_tools.append(tool_dict)
        elif isinstance(tool, dict):
            # Already in dict format
            converted_tools.append(tool)
        else:
            # Try to convert to dict (fallback)
            converted_tools.append(dict(tool))
    return converted_tools


_SUPPORTED_TOOL_MODELS = {
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "astar-gpt-4.1",
}


class ChatAstarCloud(BaseChatModel):
    """
    Drop-in replacement for AzureChatOpenAI / ChatGroq.

    Examples
    --------
    >>> from langchain_astarcloud import ChatAstarCloud
    >>> llm = ChatAstarCloud(model="gpt-4.1").bind_tools([my_tool])
    >>> print(llm.invoke("Hello").content)
    """

    model: str
    api_key: Optional[str] = None
    api_base: str = "https://api.astarcloud.no/"
    timeout: float = 30.0
    default_params: dict = {}

    def __init__(
        self,
        *,
        model: str,
        api_key: Optional[str] = None,
        api_base: str = "https://api.astarcloud.no/",
        timeout: float = 30.0,
        **default_params,
    ):
        super().__init__(
            model=model,
            api_key=api_key,
            api_base=api_base,
            timeout=timeout,
            default_params=default_params,
        )
        self._client = AstarClient(api_key=api_key or "", timeout=timeout)

    # -------- LangChain required hooks ---------------------------------- #

    @property
    def _llm_type(self) -> str:  # for telemetry
        return "astarcloud"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model, **self.default_params}

    def bind_tools(
        self,
        tools: List[Any],
        **kwargs: Any,
    ) -> "ChatAstarCloud":
        """Bind tools to the model."""
        if self.model not in _SUPPORTED_TOOL_MODELS:
            raise ValueError(
                f"Model '{self.model}' does not support tool calling. "
                f"Valid models: {', '.join(_SUPPORTED_TOOL_MODELS)}"
            )
        
        return self.__class__(
            model=self.model,
            api_key=self.api_key,
            api_base=self.api_base,
            timeout=self.timeout,
            tools=tools,
            **self.default_params,
            **kwargs,
        )

    # -------- sync path -------------------------------------------------- #

    def _generate(
        self,
        messages: List[BaseMessage],
        *,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> ChatResult:
        payload = self._build_payload(messages, stop=stop, **kwargs)
        
        # Convert LangChain tools to AstarCloud format if present
        if "tools" in payload and payload["tools"]:
            payload["tools"] = _convert_langchain_tools_to_astar_format(payload["tools"])
        
        raw = self._client.create.completion(
            messages=[_to_dict(m) for m in messages],
            **payload,
        )
        first_choice = raw.choices[0]
        msg = _from_dict(first_choice.message.model_dump())
        gen = ChatGeneration(
            message=msg,
            generation_info={"finish_reason": first_choice.finish_reason},
        )
        return ChatResult(generations=[gen], llm_output={"usage": raw.usage})

    # -------- streaming (sync iterator) ---------------------------------- #

    def _stream(
        self,
        messages: List[BaseMessage],
        *,
        stop: Optional[List[str]] = None,
        **kwargs,
    ) -> Iterator[ChatResult]:
        payload = self._build_payload(
            messages, stop=stop, stream=True, **kwargs
        )
        
        # Convert LangChain tools to AstarCloud format if present
        if "tools" in payload and payload["tools"]:
            payload["tools"] = _convert_langchain_tools_to_astar_format(payload["tools"])
        
        for chunk in self._client.create.completion(
            messages=[_to_dict(m) for m in messages], **payload
        ):
            ai = _from_dict(chunk.choices[0].delta.model_dump())
            yield ChatResult(
                generations=[ChatGeneration(message=ai)],
                llm_output={"usage": chunk.usage},
            )

    # -------- async variants -------------------------------------------- #

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        *,
        stop: Optional[List[str]] = None,
        **kwargs,
    ) -> ChatResult:
        payload = self._build_payload(messages, stop=stop, **kwargs)
        
        # Convert LangChain tools to AstarCloud format if present
        if "tools" in payload and payload["tools"]:
            payload["tools"] = _convert_langchain_tools_to_astar_format(payload["tools"])
        
        # Note: Using sync client for now - async support depends on 
        # astarcloud implementation
        raw = self._client.create.completion(
            messages=[_to_dict(m) for m in messages], **payload
        )
        first_choice = raw.choices[0]
        msg = _from_dict(first_choice.message.model_dump())
        return ChatResult(
            generations=[ChatGeneration(message=msg)],
            llm_output={"usage": raw.usage},
        )

    async def _astream(
        self,
        messages: List[BaseMessage],
        *,
        stop: Optional[List[str]] = None,
        **kwargs,
    ) -> AsyncIterator[ChatResult]:
        payload = self._build_payload(
            messages, stop=stop, stream=True, **kwargs
        )
        
        # Convert LangChain tools to AstarCloud format if present
        if "tools" in payload and payload["tools"]:
            payload["tools"] = _convert_langchain_tools_to_astar_format(payload["tools"])
        
        # Note: Using sync client for now - async support depends on 
        # astarcloud implementation
        for chunk in self._client.create.completion(
            messages=[_to_dict(m) for m in messages], **payload
        ):
            yield ChatResult(
                generations=[
                    ChatGeneration(
                        message=_from_dict(chunk.choices[0].delta)
                    )
                ],
                llm_output={"usage": chunk.usage},
            )

    # -------- helpers ---------------------------------------------------- #

    def _build_payload(self, messages, *, stop=None, **overrides):
        tools = overrides.get("tools")
        if tools and self.model not in _SUPPORTED_TOOL_MODELS:
            raise ValueError(
                f"Model '{self.model}' does not support tool calling. "
                f"Valid models: {', '.join(_SUPPORTED_TOOL_MODELS)}"
            )
        payload = {
            "model": self.model,
            "stop": stop,
            **self.default_params,
            **{k: v for k, v in overrides.items() if v is not None},
        }
        return payload 