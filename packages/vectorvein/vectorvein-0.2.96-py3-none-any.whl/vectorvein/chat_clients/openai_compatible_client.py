# @Author: Bi Ying
# @Date:   2024-07-26 14:48:55
import re
import json
from functools import cached_property
from typing import (
    Any,
    Dict,
    List,
    TYPE_CHECKING,
    overload,
    Generator,
    AsyncGenerator,
    Union,
    Literal,
    Iterable,
    Optional,
)

import httpx
from openai import OpenAI, AsyncOpenAI, AzureOpenAI, AsyncAzureOpenAI
from openai._types import Headers, Query, Body
from openai.types.shared_params.metadata import Metadata
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.chat.chat_completion_modality import ChatCompletionModality
from openai.types.chat.chat_completion_audio_param import ChatCompletionAudioParam
from openai.types.chat.chat_completion_reasoning_effort import ChatCompletionReasoningEffort
from openai.types.chat.chat_completion_stream_options_param import ChatCompletionStreamOptionsParam
from openai.types.chat.chat_completion_prediction_content_param import ChatCompletionPredictionContentParam
from anthropic.types.thinking_config_param import ThinkingConfigParam

from .base_client import BaseChatClient, BaseAsyncChatClient
from .utils import (
    cutoff_messages,
    get_message_token_counts,
    ToolCallContentProcessor,
    generate_tool_use_system_prompt,
)
from ..types import defaults as defs
from ..types.enums import ContextLengthControlType, BackendType
from ..types.llm_parameters import (
    NotGiven,
    NOT_GIVEN,
    OPENAI_NOT_GIVEN,
    ToolParam,
    ToolChoice,
    OpenAINotGiven,
    AnthropicNotGiven,
    Usage,
    ChatCompletionMessage,
    ChatCompletionDeltaMessage,
)

if TYPE_CHECKING:
    from ..settings import Settings
    from ..types.settings import SettingsDict


class OpenAICompatibleChatClient(BaseChatClient):
    DEFAULT_MODEL: str = ""
    BACKEND_NAME: BackendType

    def __init__(
        self,
        model: str = "",
        stream: bool = True,
        temperature: float | None | NotGiven = NOT_GIVEN,
        context_length_control: ContextLengthControlType = defs.CONTEXT_LENGTH_CONTROL,
        random_endpoint: bool = True,
        endpoint_id: str = "",
        http_client: httpx.Client | None = None,
        backend_name: str | None = None,
        settings: "Settings | SettingsDict | None" = None,  # Use default settings if not provided
    ):
        super().__init__(
            model,
            stream,
            temperature,
            context_length_control,
            random_endpoint,
            endpoint_id,
            http_client,
            backend_name,
            settings,
        )
        self.model_id = None
        self.endpoint = None

    @cached_property
    def raw_client(self) -> OpenAI | AzureOpenAI:
        self.endpoint, self.model_id = self._set_endpoint()

        if self.endpoint.proxy and self.http_client is None:
            self.http_client = httpx.Client(proxy=self.endpoint.proxy)

        if self.endpoint.is_azure or self.endpoint.endpoint_type == "openai_azure":
            if self.endpoint.api_base is None:
                raise ValueError("Azure endpoint is not set")
            return AzureOpenAI(
                azure_endpoint=self.endpoint.api_base,
                api_key=self.endpoint.api_key,
                api_version="2025-04-01-preview",
                http_client=self.http_client,
            )
        else:
            return OpenAI(
                api_key=self.endpoint.api_key,
                base_url=self.endpoint.api_base,
                http_client=self.http_client,
            )

    @overload
    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None | OpenAINotGiven = NOT_GIVEN,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        user: str | OpenAINotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = NOT_GIVEN,
    ) -> ChatCompletionMessage:
        pass

    @overload
    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[True],
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None | OpenAINotGiven = NOT_GIVEN,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        user: str | OpenAINotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = NOT_GIVEN,
    ) -> Generator[ChatCompletionDeltaMessage, None, None]:
        pass

    @overload
    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: bool,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None | OpenAINotGiven = NOT_GIVEN,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        user: str | OpenAINotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = NOT_GIVEN,
    ) -> ChatCompletionMessage | Generator[ChatCompletionDeltaMessage, Any, None]:
        pass

    def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] | Literal[True] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None | OpenAINotGiven = NOT_GIVEN,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        user: str | OpenAINotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = NOT_GIVEN,
    ):
        if model is not None:
            self.model = model
        if stream is not None:
            self.stream = stream
        if isinstance(temperature, AnthropicNotGiven):
            temperature = NOT_GIVEN
        if temperature is not None:
            self.temperature = temperature
        if isinstance(top_p, AnthropicNotGiven):
            top_p = NOT_GIVEN
        if isinstance(max_tokens, AnthropicNotGiven):
            max_tokens = NOT_GIVEN

        raw_client = self.raw_client  # 调用完 self.raw_client 后，self.model_id 会被赋值
        self.model_setting = self.backend_settings.models[self.model]
        if self.model_id is None:
            self.model_id = self.model_setting.id

        if not skip_cutoff and self.context_length_control == ContextLengthControlType.Latest:
            messages = cutoff_messages(
                messages,
                max_count=self.model_setting.context_length,
                backend=self.BACKEND_NAME,
                model=self.model,
            )

        if tools:
            if self.model_setting.function_call_available:
                _tools = tools
                if self.BACKEND_NAME.value == BackendType.MiniMax.value:  # MiniMax 就非要搞特殊
                    _tools = []
                    for tool in tools:
                        _tools.append(
                            {
                                "type": "function",
                                "function": {
                                    "name": tool["function"]["name"],
                                    "description": tool["function"].get("description", ""),
                                    "parameters": json.dumps(tool["function"].get("parameters", {})),
                                },
                            }
                        )
                tools_params = dict(tools=_tools, tool_choice=tool_choice)
            else:
                tools_str = json.dumps(tools, ensure_ascii=False, indent=None)
                additional_system_prompt = generate_tool_use_system_prompt(tools=tools_str)
                if messages and messages[0].get("role") == "system":
                    messages[0]["content"] += "\n\n" + additional_system_prompt
                else:
                    messages.insert(0, {"role": "system", "content": additional_system_prompt})
                tools_params = {}
        else:
            tools_params = {}

        if not max_tokens and not max_completion_tokens:
            max_output_tokens = self.model_setting.max_output_tokens
            native_multimodal = self.model_setting.native_multimodal
            token_counts = get_message_token_counts(messages=messages, tools=tools, model=self.model, native_multimodal=native_multimodal)
            if max_output_tokens is not None:
                max_tokens = self.model_setting.context_length - token_counts - 64
                max_tokens = min(max(max_tokens, 1), max_output_tokens)
            else:
                max_tokens = self.model_setting.context_length - token_counts - 64

        if "o3-mini" in self.model_id or "o4-mini" in self.model_id:
            max_completion_tokens = max_tokens
            max_tokens = NOT_GIVEN

        self._acquire_rate_limit(self.endpoint, self.model, messages)

        if self.stream:
            stream_response = raw_client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                stream=True,
                temperature=self.temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                audio=audio,
                frequency_penalty=frequency_penalty,
                logit_bias=logit_bias,
                logprobs=logprobs,
                max_completion_tokens=max_completion_tokens,
                metadata=metadata,
                modalities=modalities,
                n=n,
                parallel_tool_calls=parallel_tool_calls,
                prediction=prediction,
                presence_penalty=presence_penalty,
                reasoning_effort=reasoning_effort,
                seed=seed,
                service_tier=service_tier,
                stop=stop,
                store=store,
                top_logprobs=top_logprobs,
                user=user,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                stream_options=stream_options,
                response_format=response_format if response_format and self.model_setting.response_format_available else OPENAI_NOT_GIVEN,
                **tools_params,  # type: ignore
            )

            def generator():
                full_content = ""
                result = {}
                usage = None
                buffer = ""
                in_reasoning = False
                current_reasoning = []
                current_content = []

                for chunk in stream_response:
                    if chunk.usage and chunk.usage.total_tokens:
                        usage = Usage(
                            completion_tokens=chunk.usage.completion_tokens or 0,
                            prompt_tokens=chunk.usage.prompt_tokens or 0,
                            total_tokens=chunk.usage.total_tokens or 0,
                            prompt_tokens_details=chunk.usage.prompt_tokens_details,
                            completion_tokens_details=chunk.usage.completion_tokens_details,
                        )

                    if not chunk.choices or len(chunk.choices) == 0 or not chunk.choices[0].delta:
                        if usage:
                            yield ChatCompletionDeltaMessage(usage=usage)
                        continue

                    if self.model_setting.function_call_available:
                        if chunk.choices[0].delta.tool_calls:
                            for index, tool_call in enumerate(chunk.choices[0].delta.tool_calls):
                                tool_call.index = index
                                tool_call.type = "function"  # 也是 MiniMax 的不规范导致的问题
                        yield ChatCompletionDeltaMessage(**chunk.choices[0].delta.model_dump(), usage=usage)
                    else:
                        message = chunk.choices[0].delta.model_dump()
                        delta_content = message.get("content", "")
                        buffer += delta_content or ""

                        while True:
                            if not in_reasoning:
                                start_pos = buffer.find("<think>")
                                if start_pos != -1:
                                    current_content.append(buffer[:start_pos])
                                    buffer = buffer[start_pos + 7 :]
                                    in_reasoning = True
                                else:
                                    current_content.append(buffer)
                                    buffer = ""
                                    break
                            else:
                                end_pos = buffer.find("</think>")
                                if end_pos != -1:
                                    current_reasoning.append(buffer[:end_pos])
                                    buffer = buffer[end_pos + 8 :]
                                    in_reasoning = False
                                else:
                                    current_reasoning.append(buffer)
                                    buffer = ""
                                    break

                        message["content"] = "".join(current_content)
                        if current_reasoning:
                            message["reasoning_content"] = "".join(current_reasoning)
                        current_content.clear()
                        current_reasoning.clear()

                        if tools:
                            full_content += message["content"]
                            tool_call_data = ToolCallContentProcessor(full_content).tool_calls
                            if tool_call_data:
                                message["tool_calls"] = tool_call_data["tool_calls"]

                        if full_content in ("<", "<|", "<|▶", "<|▶|") or full_content.startswith("<|▶|>"):
                            message["content"] = ""
                            result = message
                            continue

                        yield ChatCompletionDeltaMessage(**message, usage=usage)

                if buffer:
                    if in_reasoning:
                        current_reasoning.append(buffer)
                    else:
                        current_content.append(buffer)
                    final_message = {
                        "content": "".join(current_content),
                        "reasoning_content": "".join(current_reasoning) if current_reasoning else None,
                    }
                    yield ChatCompletionDeltaMessage(**final_message, usage=usage)

                if result:
                    yield ChatCompletionDeltaMessage(**result, usage=usage)

            return generator()
        else:
            response = raw_client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                stream=False,
                temperature=self.temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                audio=audio,
                frequency_penalty=frequency_penalty,
                logit_bias=logit_bias,
                logprobs=logprobs,
                max_completion_tokens=max_completion_tokens,
                metadata=metadata,
                modalities=modalities,
                n=n,
                parallel_tool_calls=parallel_tool_calls,
                prediction=prediction,
                presence_penalty=presence_penalty,
                reasoning_effort=reasoning_effort,
                seed=seed,
                service_tier=service_tier,
                stop=stop,
                store=store,
                top_logprobs=top_logprobs,
                user=user,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                stream_options=stream_options,
                response_format=response_format if response_format and self.model_setting.response_format_available else OPENAI_NOT_GIVEN,
                **tools_params,  # type: ignore
            )

            if not response.choices:
                raise ValueError(f"No response choices: {response}")

            result = {
                "content": response.choices[0].message.content,
                "reasoning_content": getattr(response.choices[0].message, "reasoning_content", None),
                "usage": response.usage.model_dump() if response.usage else None,
            }

            if not result["reasoning_content"] and result["content"]:
                think_match = re.search(r"<think>(.*?)</think>", result["content"], re.DOTALL)
                if think_match:
                    result["reasoning_content"] = think_match.group(1)
                    result["content"] = result["content"].replace(think_match.group(0), "", 1)

            if tools:
                if self.model_setting.function_call_available:
                    if response.choices[0].message.tool_calls:
                        result["tool_calls"] = [{**tool_call.model_dump(), "type": "function"} for tool_call in response.choices[0].message.tool_calls]
                else:
                    tool_call_content_processor = ToolCallContentProcessor(result["content"])
                    tool_call_data = tool_call_content_processor.tool_calls
                    if tool_call_data:
                        result["tool_calls"] = tool_call_data["tool_calls"]
                        result["content"] = tool_call_content_processor.non_tool_content

            return ChatCompletionMessage(**result)


class AsyncOpenAICompatibleChatClient(BaseAsyncChatClient):
    DEFAULT_MODEL: str = ""
    BACKEND_NAME: BackendType

    def __init__(
        self,
        model: str = "",
        stream: bool = True,
        temperature: float | None | NotGiven = NOT_GIVEN,
        context_length_control: ContextLengthControlType = defs.CONTEXT_LENGTH_CONTROL,
        random_endpoint: bool = True,
        endpoint_id: str = "",
        http_client: httpx.AsyncClient | None = None,
        backend_name: str | None = None,
        settings: "Settings | SettingsDict | None" = None,  # Use default settings if not provided
    ):
        super().__init__(
            model,
            stream,
            temperature,
            context_length_control,
            random_endpoint,
            endpoint_id,
            http_client,
            backend_name,
            settings,
        )
        self.model_id = None
        self.endpoint = None

    @cached_property
    def raw_client(self):
        self.endpoint, self.model_id = self._set_endpoint()

        if self.endpoint.proxy and self.http_client is None:
            self.http_client = httpx.AsyncClient(proxy=self.endpoint.proxy)

        if self.endpoint.is_azure or self.endpoint.endpoint_type == "openai_azure":
            if self.endpoint.api_base is None:
                raise ValueError("Azure endpoint is not set")
            return AsyncAzureOpenAI(
                azure_endpoint=self.endpoint.api_base,
                api_key=self.endpoint.api_key,
                api_version="2025-04-01-preview",
                http_client=self.http_client,
            )
        else:
            return AsyncOpenAI(
                api_key=self.endpoint.api_key,
                base_url=self.endpoint.api_base,
                http_client=self.http_client,
            )

    @overload
    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None | OpenAINotGiven = NOT_GIVEN,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        user: str | OpenAINotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = NOT_GIVEN,
    ) -> ChatCompletionMessage:
        pass

    @overload
    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[True],
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None | OpenAINotGiven = NOT_GIVEN,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        user: str | OpenAINotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = NOT_GIVEN,
    ) -> AsyncGenerator[ChatCompletionDeltaMessage, Any]:
        pass

    @overload
    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: bool,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None | OpenAINotGiven = NOT_GIVEN,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        user: str | OpenAINotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = NOT_GIVEN,
    ) -> ChatCompletionMessage | AsyncGenerator[ChatCompletionDeltaMessage, Any]:
        pass

    async def create_completion(
        self,
        *,
        messages: list,
        model: str | None = None,
        stream: Literal[False] | Literal[True] = False,
        temperature: float | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        tool_choice: ToolChoice | NotGiven = NOT_GIVEN,
        response_format: ResponseFormat | NotGiven = NOT_GIVEN,
        stream_options: ChatCompletionStreamOptionsParam | None | OpenAINotGiven = NOT_GIVEN,
        top_p: float | NotGiven | None = NOT_GIVEN,
        skip_cutoff: bool = False,
        audio: Optional[ChatCompletionAudioParam] | OpenAINotGiven = NOT_GIVEN,
        frequency_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | OpenAINotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | OpenAINotGiven = NOT_GIVEN,
        modalities: Optional[List[ChatCompletionModality]] | OpenAINotGiven = NOT_GIVEN,
        n: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | OpenAINotGiven = NOT_GIVEN,
        prediction: Optional[ChatCompletionPredictionContentParam] | OpenAINotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | OpenAINotGiven = NOT_GIVEN,
        reasoning_effort: Optional[ChatCompletionReasoningEffort] | OpenAINotGiven = NOT_GIVEN,
        thinking: ThinkingConfigParam | None | NotGiven = NOT_GIVEN,
        seed: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        service_tier: Optional[Literal["auto", "default"]] | OpenAINotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | OpenAINotGiven = NOT_GIVEN,
        store: Optional[bool] | OpenAINotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | OpenAINotGiven = NOT_GIVEN,
        user: str | OpenAINotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | OpenAINotGiven = NOT_GIVEN,
    ):
        if model is not None:
            self.model = model
        if stream is not None:
            self.stream = stream
        if isinstance(temperature, AnthropicNotGiven):
            temperature = NOT_GIVEN
        if temperature is not None:
            self.temperature = temperature
        if isinstance(top_p, AnthropicNotGiven):
            top_p = NOT_GIVEN
        if isinstance(max_tokens, AnthropicNotGiven):
            max_tokens = NOT_GIVEN

        raw_client = self.raw_client  # 调用完 self.raw_client 后，self.model_id 会被赋值
        self.model_setting = self.backend_settings.models[self.model]
        if self.model_id is None:
            self.model_id = self.model_setting.id

        if not skip_cutoff and self.context_length_control == ContextLengthControlType.Latest:
            messages = cutoff_messages(
                messages,
                max_count=self.model_setting.context_length,
                backend=self.BACKEND_NAME,
                model=self.model,
            )

        if tools:
            if self.model_setting.function_call_available:
                _tools = tools
                if self.BACKEND_NAME.value == BackendType.MiniMax.value:
                    _tools = []
                    for tool in tools:
                        _tools.append(
                            {
                                "type": "function",
                                "function": {
                                    "name": tool["function"]["name"],
                                    "description": tool["function"].get("description", ""),
                                    "parameters": json.dumps(tool["function"].get("parameters", {})),
                                },
                            }
                        )
                tools_params = dict(tools=_tools, tool_choice=tool_choice)
            else:
                tools_str = json.dumps(tools, ensure_ascii=False, indent=None)
                additional_system_prompt = generate_tool_use_system_prompt(tools=tools_str)
                if messages and messages[0].get("role") == "system":
                    messages[0]["content"] += "\n\n" + additional_system_prompt
                else:
                    messages.insert(0, {"role": "system", "content": additional_system_prompt})
                tools_params = {}
        else:
            tools_params = {}

        if not max_tokens and not max_completion_tokens:
            max_output_tokens = self.model_setting.max_output_tokens
            native_multimodal = self.model_setting.native_multimodal
            token_counts = get_message_token_counts(messages=messages, tools=tools, model=self.model, native_multimodal=native_multimodal)
            if max_output_tokens is not None:
                max_tokens = self.model_setting.context_length - token_counts - 64
                max_tokens = min(max(max_tokens, 1), max_output_tokens)
            else:
                max_tokens = self.model_setting.context_length - token_counts - 64

        if "o3-mini" in self.model_id or "o4-mini" in self.model_id:
            max_completion_tokens = max_tokens
            max_tokens = NOT_GIVEN

        await self._acquire_rate_limit(self.endpoint, self.model, messages)

        if self.stream:
            stream_response = await raw_client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                stream=self.stream,
                temperature=self.temperature,
                max_tokens=max_tokens,  # Azure 的 OpenAI 怎么 stream 模式不支持 max_completion_tokens
                top_p=top_p,
                audio=audio,
                frequency_penalty=frequency_penalty,
                logit_bias=logit_bias,
                logprobs=logprobs,
                max_completion_tokens=max_completion_tokens,
                metadata=metadata,
                modalities=modalities,
                n=n,
                parallel_tool_calls=parallel_tool_calls,
                prediction=prediction,
                presence_penalty=presence_penalty,
                reasoning_effort=reasoning_effort,
                seed=seed,
                service_tier=service_tier,
                stop=stop,
                store=store,
                top_logprobs=top_logprobs,
                user=user,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                stream_options=stream_options,
                response_format=response_format if response_format and self.model_setting.response_format_available else OPENAI_NOT_GIVEN,
                **tools_params,  # type: ignore
            )

            async def generator():
                full_content = ""
                result = {}
                usage = None
                buffer = ""
                in_reasoning = False
                current_reasoning = []
                current_content = []

                async for chunk in stream_response:
                    if chunk.usage and chunk.usage.total_tokens:
                        usage = Usage(
                            completion_tokens=chunk.usage.completion_tokens or 0,
                            prompt_tokens=chunk.usage.prompt_tokens or 0,
                            total_tokens=chunk.usage.total_tokens or 0,
                            completion_tokens_details=chunk.usage.completion_tokens_details,
                            prompt_tokens_details=chunk.usage.prompt_tokens_details,
                        )

                    if not chunk.choices or len(chunk.choices) == 0 or not chunk.choices[0].delta:
                        if usage:
                            yield ChatCompletionDeltaMessage(usage=usage)
                        continue

                    if self.model_setting.function_call_available:
                        if chunk.choices[0].delta.tool_calls:
                            for index, tool_call in enumerate(chunk.choices[0].delta.tool_calls):
                                tool_call.index = index
                                tool_call.type = "function"
                        yield ChatCompletionDeltaMessage(**chunk.choices[0].delta.model_dump(), usage=usage)
                    else:
                        message = chunk.choices[0].delta.model_dump()
                        delta_content = message.get("content", "")
                        buffer += delta_content or ""

                        while True:
                            if not in_reasoning:
                                start_pos = buffer.find("<think>")
                                if start_pos != -1:
                                    current_content.append(buffer[:start_pos])
                                    buffer = buffer[start_pos + 7 :]
                                    in_reasoning = True
                                else:
                                    current_content.append(buffer)
                                    buffer = ""
                                    break
                            else:
                                end_pos = buffer.find("</think>")
                                if end_pos != -1:
                                    current_reasoning.append(buffer[:end_pos])
                                    buffer = buffer[end_pos + 8 :]
                                    in_reasoning = False
                                else:
                                    current_reasoning.append(buffer)
                                    buffer = ""
                                    break

                        message["content"] = "".join(current_content)
                        if current_reasoning:
                            message["reasoning_content"] = "".join(current_reasoning)
                        current_content.clear()
                        current_reasoning.clear()

                        if tools:
                            full_content += message["content"]
                            tool_call_data = ToolCallContentProcessor(full_content).tool_calls
                            if tool_call_data:
                                message["tool_calls"] = tool_call_data["tool_calls"]

                        if full_content in ("<", "<|", "<|▶", "<|▶|") or full_content.startswith("<|▶|>"):
                            message["content"] = ""
                            result = message
                            continue

                        yield ChatCompletionDeltaMessage(**message, usage=usage)

                if buffer:
                    if in_reasoning:
                        current_reasoning.append(buffer)
                    else:
                        current_content.append(buffer)
                    final_message = {
                        "content": "".join(current_content),
                        "reasoning_content": "".join(current_reasoning) if current_reasoning else None,
                    }
                    yield ChatCompletionDeltaMessage(**final_message, usage=usage)

                if result:
                    yield ChatCompletionDeltaMessage(**result, usage=usage)

            return generator()
        else:
            response = await raw_client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                stream=self.stream,
                temperature=self.temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                audio=audio,
                frequency_penalty=frequency_penalty,
                logit_bias=logit_bias,
                logprobs=logprobs,
                max_completion_tokens=max_completion_tokens,
                metadata=metadata,
                modalities=modalities,
                n=n,
                parallel_tool_calls=parallel_tool_calls,
                prediction=prediction,
                presence_penalty=presence_penalty,
                reasoning_effort=reasoning_effort,
                seed=seed,
                service_tier=service_tier,
                stop=stop,
                store=store,
                top_logprobs=top_logprobs,
                user=user,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                stream_options=stream_options,
                response_format=response_format if response_format and self.model_setting.response_format_available else OPENAI_NOT_GIVEN,
                **tools_params,  # type: ignore
            )

            if not response.choices:
                raise ValueError(f"No response choices: {response}")

            result = {
                "content": response.choices[0].message.content,
                "reasoning_content": getattr(response.choices[0].message, "reasoning_content", None),
                "usage": response.usage.model_dump() if response.usage else None,
            }

            if not result["reasoning_content"] and result["content"]:
                think_match = re.search(r"<think>(.*?)</think>", result["content"], re.DOTALL)
                if think_match:
                    result["reasoning_content"] = think_match.group(1)
                    result["content"] = result["content"].replace(think_match.group(0), "", 1)

            if tools:
                if self.model_setting.function_call_available:
                    if response.choices[0].message.tool_calls:
                        result["tool_calls"] = [{**tool_call.model_dump(), "type": "function"} for tool_call in response.choices[0].message.tool_calls]
                else:
                    tool_call_content_processor = ToolCallContentProcessor(result["content"])
                    tool_call_data = tool_call_content_processor.tool_calls
                    if tool_call_data:
                        result["tool_calls"] = tool_call_data["tool_calls"]
                        result["content"] = tool_call_content_processor.non_tool_content
            return ChatCompletionMessage(**result)
