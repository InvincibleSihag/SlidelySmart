"""Selective streaming helpers for graph agents.

LangChain contracts used:
- `model.stream(...)` yields `AIMessageChunk` values
- chunks are accumulated using `chunk_a + chunk_b`
- assistant text / reasoning can be read from `chunk.content_blocks`
- completed tool calls are available on the accumulated message (`response.tool_calls`)
"""

from __future__ import annotations

import re
from typing import Any, Callable, Iterable, Protocol, cast

from langchain_core.messages import AIMessageChunk

from app.core.logging import get_logger

logger = get_logger(__name__)

STAGE_PROCESSING = "processing"

TriggerFn = Callable[[str, str, dict[str, Any]], None]


class SupportsStream(Protocol):
    """Minimal protocol for LangChain chat models that implement `.stream()`."""

    def stream(
        self,
        input: list[Any],
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Iterable[Any]:
        ...


def _emit_processing(
    *,
    channel: str | None,
    trigger: TriggerFn,
    message: str,
    event: str = "agent_status",
) -> None:
    if channel and message:
        message = re.sub(r'\n{3,}', '\n\n', message)
        trigger(channel, event, {"stage": STAGE_PROCESSING, "message": message})


def _reasoning_texts(chunk: AIMessageChunk) -> list[str]:
    texts: list[str] = []
    seen: set[str] = set()

    def add(text: str) -> None:
        if text not in seen:
            seen.add(text)
            texts.append(text)

    for block in chunk.content_blocks:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "thinking":
            thinking = block.get("thinking")
            if isinstance(thinking, str) and thinking:
                add(thinking)
        elif block.get("type") == "reasoning":
            reasoning = block.get("reasoning")
            if isinstance(reasoning, str) and reasoning:
                add(reasoning)

    reasoning_content = chunk.additional_kwargs.get("reasoning_content")
    if isinstance(reasoning_content, str) and reasoning_content:
        add(reasoning_content)

    return texts


def _assistant_texts(chunk: AIMessageChunk) -> list[str]:
    texts: list[str] = []
    for block in chunk.content_blocks:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str) and text:
                texts.append(text)
    return texts


def _has_tool_call_signal(chunk: AIMessageChunk) -> bool:
    if chunk.tool_call_chunks:
        return True
    for block in chunk.content_blocks:
        if isinstance(block, dict) and block.get("type") in {"tool_call_chunk", "tool_call"}:
            return True
    return False


def stream_model_response(
    *,
    model: SupportsStream,
    messages: list[Any],
    channel: str | None,
    trigger: TriggerFn,
    config: dict[str, Any] | None = None,
) -> AIMessageChunk:
    """Stream model response, emit selected updates, and return accumulated chunk.

    Selection policy:
    - Stream internal thoughts/reasoning when present.
    - Stream assistant text only when the completed response contains tool calls.
    - Never stream tool-call payloads to client.
    """
    logger.info("stream_start", message_count=len(messages), channel=channel)
    stream = model.stream(messages, config=config)
    response: AIMessageChunk | None = None
    has_tool_call = False
    chunk_count = 0
    assistant_text_buffer: list[str] = []

    for raw_chunk in stream:
        chunk = cast(AIMessageChunk, raw_chunk)
        chunk_count += 1
        response = chunk if response is None else response + chunk

        for thought in _reasoning_texts(chunk):
            logger.debug("stream_thought", text=thought[:120])
            _emit_processing(channel=channel, trigger=trigger, message=thought)

        if not has_tool_call and _has_tool_call_signal(chunk):
            has_tool_call = True
            logger.info("stream_tool_call_detected")
            for text in assistant_text_buffer:
                _emit_processing(channel=channel, trigger=trigger, message=text)
            assistant_text_buffer.clear()

        for text in _assistant_texts(chunk):
            if has_tool_call:
                _emit_processing(channel=channel, trigger=trigger, message=text)
            else:
                assistant_text_buffer.append(text)

    if response is None:
        logger.error("stream_empty")
        raise RuntimeError("Model stream returned no chunks.")

    if not has_tool_call and response.tool_calls:
        for text in assistant_text_buffer:
            _emit_processing(channel=channel, trigger=trigger, message=text)

    tool_names = [tc["name"] for tc in response.tool_calls] if response.tool_calls else []
    logger.info(
        "stream_complete",
        chunks=chunk_count,
        has_tool_calls=bool(response.tool_calls),
        tool_names=tool_names,
    )
    return response
