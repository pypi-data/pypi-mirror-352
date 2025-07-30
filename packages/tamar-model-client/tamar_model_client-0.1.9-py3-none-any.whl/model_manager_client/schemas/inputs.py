import httpx
from google.genai import types
from openai import NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body
from openai.types import ChatModel, Metadata, ReasoningEffort, ResponsesModel, Reasoning
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionAudioParam, completion_create_params, \
    ChatCompletionPredictionContentParam, ChatCompletionStreamOptionsParam, ChatCompletionToolChoiceOptionParam, \
    ChatCompletionToolParam
from openai.types.responses import ResponseInputParam, ResponseIncludable, ResponseTextConfigParam, \
    response_create_params, ToolParam
from pydantic import BaseModel, model_validator
from typing import List, Optional, Union, Iterable, Dict, Literal

from model_manager_client.enums import ProviderType, InvokeType
from model_manager_client.enums.channel import Channel


class UserContext(BaseModel):
    org_id: str  # 组织id
    user_id: str  # 用户id
    client_type: str  # 客户端类型，这里记录的是哪个服务请求过来的


class GoogleGenAiInput(BaseModel):
    model: str
    contents: Union[types.ContentListUnion, types.ContentListUnionDict]
    config: Optional[types.GenerateContentConfigOrDict] = None

    model_config = {
        "arbitrary_types_allowed": True
    }


class OpenAIResponsesInput(BaseModel):
    input: Union[str, ResponseInputParam]
    model: ResponsesModel
    include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN
    instructions: Optional[str] | NotGiven = NOT_GIVEN
    max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN
    metadata: Optional[Metadata] | NotGiven = NOT_GIVEN
    parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN
    previous_response_id: Optional[str] | NotGiven = NOT_GIVEN
    reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN
    store: Optional[bool] | NotGiven = NOT_GIVEN
    stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN
    temperature: Optional[float] | NotGiven = NOT_GIVEN
    text: ResponseTextConfigParam | NotGiven = NOT_GIVEN
    tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN
    tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN
    top_p: Optional[float] | NotGiven = NOT_GIVEN
    truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN

    model_config = {
        "arbitrary_types_allowed": True
    }


class OpenAIChatCompletionsInput(BaseModel):
    messages: Iterable[ChatCompletionMessageParam]
    model: Union[str, ChatModel]
    audio: Optional[ChatCompletionAudioParam] | NotGiven = NOT_GIVEN
    frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN
    function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN
    functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN
    logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN
    logprobs: Optional[bool] | NotGiven = NOT_GIVEN
    max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN
    max_tokens: Optional[int] | NotGiven = NOT_GIVEN
    metadata: Optional[Metadata] | NotGiven = NOT_GIVEN
    modalities: Optional[List[Literal["text", "audio"]]] | NotGiven = NOT_GIVEN
    n: Optional[int] | NotGiven = NOT_GIVEN
    parallel_tool_calls: bool | NotGiven = NOT_GIVEN
    prediction: Optional[ChatCompletionPredictionContentParam] | NotGiven = NOT_GIVEN
    presence_penalty: Optional[float] | NotGiven = NOT_GIVEN
    reasoning_effort: Optional[ReasoningEffort] | NotGiven = NOT_GIVEN
    response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN
    seed: Optional[int] | NotGiven = NOT_GIVEN
    service_tier: Optional[Literal["auto", "default"]] | NotGiven = NOT_GIVEN
    stop: Union[Optional[str], List[str], None] | NotGiven = NOT_GIVEN
    store: Optional[bool] | NotGiven = NOT_GIVEN
    stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN
    stream_options: Optional[ChatCompletionStreamOptionsParam] | NotGiven = NOT_GIVEN
    temperature: Optional[float] | NotGiven = NOT_GIVEN
    tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN
    tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN
    top_logprobs: Optional[int] | NotGiven = NOT_GIVEN
    top_p: Optional[float] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    web_search_options: completion_create_params.WebSearchOptions | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN

    model_config = {
        "arbitrary_types_allowed": True
    }


class BaseRequest(BaseModel):
    provider: ProviderType  # 供应商，如 "openai", "google" 等
    channel: Channel = Channel.NORMAL  # 渠道：不同服务商之前有不同的调用SDK，这里指定是调用哪个SDK
    invoke_type: InvokeType = InvokeType.TEXT_GENERATION  # 模型调用类型：generation-生成模型调用


class ModelRequestInput(BaseRequest):
    # 合并model字段
    model: Optional[Union[str, ResponsesModel, ChatModel]] = None

    # OpenAI Responses Input
    input: Optional[Union[str, ResponseInputParam]] = None
    include: Optional[Union[List[ResponseIncludable], NotGiven]] = NOT_GIVEN
    instructions: Optional[Union[str, NotGiven]] = NOT_GIVEN
    max_output_tokens: Optional[Union[int, NotGiven]] = NOT_GIVEN
    metadata: Optional[Union[Metadata, NotGiven]] = NOT_GIVEN
    parallel_tool_calls: Optional[Union[bool, NotGiven]] = NOT_GIVEN
    previous_response_id: Optional[Union[str, NotGiven]] = NOT_GIVEN
    reasoning: Optional[Union[Reasoning, NotGiven]] = NOT_GIVEN
    store: Optional[Union[bool, NotGiven]] = NOT_GIVEN
    stream: Optional[Union[Literal[False], Literal[True], NotGiven]] = NOT_GIVEN
    temperature: Optional[Union[float, NotGiven]] = NOT_GIVEN
    text: Optional[Union[ResponseTextConfigParam, NotGiven]] = NOT_GIVEN
    tool_choice: Optional[
        Union[response_create_params.ToolChoice, ChatCompletionToolChoiceOptionParam, NotGiven]] = NOT_GIVEN
    tools: Optional[Union[Iterable[ToolParam], Iterable[ChatCompletionToolParam], NotGiven]] = NOT_GIVEN
    top_p: Optional[Union[float, NotGiven]] = NOT_GIVEN
    truncation: Optional[Union[Literal["auto", "disabled"], NotGiven]] = NOT_GIVEN
    user: Optional[Union[str, NotGiven]] = NOT_GIVEN

    extra_headers: Optional[Union[Headers, None]] = None
    extra_query: Optional[Union[Query, None]] = None
    extra_body: Optional[Union[Body, None]] = None
    timeout: Optional[Union[float, httpx.Timeout, None, NotGiven]] = NOT_GIVEN

    # OpenAI Chat Completions Input
    messages: Optional[Iterable[ChatCompletionMessageParam]] = None
    audio: Optional[Union[ChatCompletionAudioParam, NotGiven]] = NOT_GIVEN
    frequency_penalty: Optional[Union[float, NotGiven]] = NOT_GIVEN
    function_call: Optional[Union[completion_create_params.FunctionCall, NotGiven]] = NOT_GIVEN
    functions: Optional[Union[Iterable[completion_create_params.Function], NotGiven]] = NOT_GIVEN
    logit_bias: Optional[Union[Dict[str, int], NotGiven]] = NOT_GIVEN
    logprobs: Optional[Union[bool, NotGiven]] = NOT_GIVEN
    max_completion_tokens: Optional[Union[int, NotGiven]] = NOT_GIVEN
    modalities: Optional[Union[List[Literal["text", "audio"]], NotGiven]] = NOT_GIVEN
    n: Optional[Union[int, NotGiven]] = NOT_GIVEN
    prediction: Optional[Union[ChatCompletionPredictionContentParam, NotGiven]] = NOT_GIVEN
    presence_penalty: Optional[Union[float, NotGiven]] = NOT_GIVEN
    reasoning_effort: Optional[Union[ReasoningEffort, NotGiven]] = NOT_GIVEN
    response_format: Optional[Union[completion_create_params.ResponseFormat, NotGiven]] = NOT_GIVEN
    seed: Optional[Union[int, NotGiven]] = NOT_GIVEN
    service_tier: Optional[Union[Literal["auto", "default"], NotGiven]] = NOT_GIVEN
    stop: Optional[Union[Optional[str], List[str], None, NotGiven]] = NOT_GIVEN
    top_logprobs: Optional[Union[int, NotGiven]] = NOT_GIVEN
    web_search_options: Optional[Union[completion_create_params.WebSearchOptions, NotGiven]] = NOT_GIVEN
    stream_options: Optional[Union[ChatCompletionStreamOptionsParam, NotGiven]] = NOT_GIVEN

    # Google GenAI Input
    contents: Optional[Union[types.ContentListUnion, types.ContentListUnionDict]] = None
    config: Optional[types.GenerateContentConfigOrDict] = None

    model_config = {
        "arbitrary_types_allowed": True
    }


class ModelRequest(ModelRequestInput):
    user_context: UserContext  # 用户信息

    @model_validator(mode="after")
    def validate_by_provider_and_invoke_type(self) -> "ModelRequest":
        """根据 provider 和 invoke_type 动态校验具体输入模型字段。"""
        # 动态获取 allowed fields
        base_allowed = ["provider", "channel", "invoke_type", "user_context"]
        google_allowed = set(base_allowed) | set(GoogleGenAiInput.model_fields.keys())
        openai_responses_allowed = set(base_allowed) | set(OpenAIResponsesInput.model_fields.keys())
        openai_chat_allowed = set(base_allowed) | set(OpenAIChatCompletionsInput.model_fields.keys())

        # 导入或定义你的原始输入模型
        google_required_fields = {"model", "contents"}
        openai_responses_required_fields = {"input", "model"}
        openai_chat_required_fields = {"messages", "model"}

        # 选择需要校验的字段集合
        if self.provider == ProviderType.GOOGLE:
            expected_fields = google_required_fields
            allowed_fields = google_allowed
        elif self.provider == ProviderType.OPENAI or self.provider == ProviderType.AZURE:
            if self.invoke_type == InvokeType.RESPONSES or self.invoke_type == InvokeType.TEXT_GENERATION:
                expected_fields = openai_responses_required_fields
                allowed_fields = openai_responses_allowed
            elif self.invoke_type == InvokeType.CHAT_COMPLETIONS:
                expected_fields = openai_chat_required_fields
                allowed_fields = openai_chat_allowed
            else:
                raise ValueError(f"暂不支持的调用类型: {self.invoke_type}")
        else:
            raise ValueError(f"暂不支持的提供商: {self.provider}")

        # 检查是否缺失关键字段
        missing = []
        for field in expected_fields:
            if getattr(self, field, None) is None:
                missing.append(field)

        if missing:
            raise ValueError(
                f"{self.provider}（{self.invoke_type}）请求缺少必填字段: {missing}"
            )

        # 检查是否有非法字段
        illegal_fields = []
        for name, value in self.__dict__.items():
            if name in {"provider", "channel", "invoke_type", "stream"}:
                continue
            if name not in allowed_fields and value is not None and not isinstance(value, NotGiven):
                illegal_fields.append(name)

        if illegal_fields:
            raise ValueError(
                f"{self.provider}（{self.invoke_type}）存在不支持的字段: {illegal_fields}"
            )

        return self


class BatchModelRequestItem(ModelRequestInput):
    custom_id: Optional[str] = None
    priority: Optional[int] = None  # （可选、预留字段）批量调用时执行的优先级

    @model_validator(mode="after")
    def validate_by_provider_and_invoke_type(self) -> "BatchModelRequestItem":
        """根据 provider 和 invoke_type 动态校验具体输入模型字段。"""
        # 动态获取 allowed fields
        base_allowed = ["provider", "channel", "invoke_type", "custom_id", "priority"]
        google_allowed = set(base_allowed) | set(GoogleGenAiInput.model_fields.keys())
        openai_responses_allowed = set(base_allowed) | set(OpenAIResponsesInput.model_fields.keys())
        openai_chat_allowed = set(base_allowed) | set(OpenAIChatCompletionsInput.model_fields.keys())

        # 导入或定义你的原始输入模型
        google_required_fields = {"model", "contents"}
        openai_responses_required_fields = {"input", "model"}
        openai_chat_required_fields = {"messages", "model"}

        # 选择需要校验的字段集合
        if self.provider == ProviderType.GOOGLE:
            expected_fields = google_required_fields
            allowed_fields = google_allowed
        elif self.provider == ProviderType.OPENAI or self.provider == ProviderType.AZURE:
            if self.invoke_type == InvokeType.RESPONSES or self.invoke_type == InvokeType.TEXT_GENERATION:
                expected_fields = openai_responses_required_fields
                allowed_fields = openai_responses_allowed
            elif self.invoke_type == InvokeType.CHAT_COMPLETIONS:
                expected_fields = openai_chat_required_fields
                allowed_fields = openai_chat_allowed
            else:
                raise ValueError(f"暂不支持的调用类型: {self.invoke_type}")
        else:
            raise ValueError(f"暂不支持的提供商: {self.provider}")

        # 检查是否缺失关键字段
        missing = []
        for field in expected_fields:
            if getattr(self, field, None) is None:
                missing.append(field)

        if missing:
            raise ValueError(
                f"{self.provider}（{self.invoke_type}）请求缺少必填字段: {missing}"
            )

        # 检查是否有非法字段
        illegal_fields = []
        for name, value in self.__dict__.items():
            if name in {"provider", "channel", "invoke_type", "stream"}:
                continue
            if name not in allowed_fields and value is not None and not isinstance(value, NotGiven):
                illegal_fields.append(name)

        if illegal_fields:
            raise ValueError(
                f"{self.provider}（{self.invoke_type}）存在不支持的字段: {illegal_fields}"
            )

        return self


class BatchModelRequest(BaseModel):
    user_context: UserContext  # 用户信息
    items: List[BatchModelRequestItem]  # 批量请求项列表
