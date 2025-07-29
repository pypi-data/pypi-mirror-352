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

from astarcloud import AstarClient, AstarAsyncClient


def _to_dict(msg: BaseMessage) -> dict:
    """LangChain ➜ AstarCloud wire format"""
    if isinstance(msg, AIMessage) and msg.tool_calls:
        return {
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": msg.tool_calls,
        }
    return {"role": msg.type, "content": msg.content}


def _from_dict(d: Mapping[str, Any]) -> AIMessage:
    """AstarCloud ➜ LangChain"""
    return AIMessage(
        content=d.get("content", ""),
        additional_kwargs={"tool_calls": d.get("tool_calls")},
    )


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

    def __init__(
        self,
        *,
        model: str,
        api_key: Optional[str] = None,
        api_base: str = "https://api.astarcloud.no",
        timeout: float = 30.0,
        **default_params,
    ):
        super().__init__()
        self.model = model
        self._client = AstarClient(api_key=api_key or "", timeout=timeout)
        self._client_async = AstarAsyncClient(
            api_key=api_key or "", timeout=timeout
        )
        self.api_base = api_base
        self.default_params = default_params

    # -------- LangChain required hooks ---------------------------------- #

    @property
    def _llm_type(self) -> str:  # for telemetry
        return "astarcloud"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model, **self.default_params}

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
        raw = self._client.create(
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
        for chunk in self._client.create(
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
        raw = await self._client_async.create(
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
        async for chunk in self._client_async.create(
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