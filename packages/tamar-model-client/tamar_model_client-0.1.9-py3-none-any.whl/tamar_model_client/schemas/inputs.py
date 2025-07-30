import httpx
from google.genai import types
from openai import NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body
from openai.types import ChatModel, Metadata, ReasoningEffort, ResponsesModel, Reasoning, ImageModel
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionAudioParam, completion_create_params, \
    ChatCompletionPredictionContentParam, ChatCompletionStreamOptionsParam, ChatCompletionToolChoiceOptionParam, \
    ChatCompletionToolParam
from openai.types.responses import ResponseInputParam, ResponseIncludable, ResponseTextConfigParam, \
    response_create_params, ToolParam
from pydantic import BaseModel, model_validator
from typing import List, Optional, Union, Iterable, Dict, Literal

from tamar_model_client.enums import ProviderType, InvokeType
from tamar_model_client.enums.channel import Channel


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


class GoogleVertexAIImagesInput(BaseModel):
    model: str
    prompt: str
    negative_prompt: Optional[str] = None
    number_of_images: int = 1
    aspect_ratio: Optional[Literal["1:1", "9:16", "16:9", "4:3", "3:4"]] = None
    guidance_scale: Optional[float] = None
    language: Optional[str] = None
    seed: Optional[int] = None
    output_gcs_uri: Optional[str] = None
    add_watermark: Optional[bool] = True
    safety_filter_level: Optional[
        Literal["block_most", "block_some", "block_few", "block_fewest"]
    ] = None
    person_generation: Optional[
        Literal["dont_allow", "allow_adult", "allow_all"]
    ] = None

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


class OpenAIImagesInput(BaseModel):
    prompt: str
    model: Union[str, ImageModel, None] | NotGiven = NOT_GIVEN
    n: Optional[int] | NotGiven = NOT_GIVEN
    quality: Literal["standard", "hd"] | NotGiven = NOT_GIVEN
    response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN
    size: Optional[Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]] | NotGiven = NOT_GIVEN
    style: Optional[Literal["vivid", "natural"]] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
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
    invoke_type: InvokeType = InvokeType.GENERATION  # 模型调用类型：generation-生成模型调用


class ModelRequestInput(BaseRequest):
    # 合并 model 字段
    model: Optional[Union[str, ResponsesModel, ChatModel, ImageModel]] = None

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
        Union[response_create_params.ToolChoice, ChatCompletionToolChoiceOptionParam, NotGiven]
    ] = NOT_GIVEN
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
    response_format: Optional[
        Union[Literal["url", "b64_json"], completion_create_params.ResponseFormat, NotGiven]] = NOT_GIVEN
    seed: Optional[Union[int, NotGiven]] = NOT_GIVEN
    service_tier: Optional[Union[Literal["auto", "default"], NotGiven]] = NOT_GIVEN
    stop: Optional[Union[Optional[str], List[str], None, NotGiven]] = NOT_GIVEN
    top_logprobs: Optional[Union[int, NotGiven]] = NOT_GIVEN
    web_search_options: Optional[Union[completion_create_params.WebSearchOptions, NotGiven]] = NOT_GIVEN
    stream_options: Optional[Union[ChatCompletionStreamOptionsParam, NotGiven]] = NOT_GIVEN

    # Google GenAI Input
    contents: Optional[Union[types.ContentListUnion, types.ContentListUnionDict]] = None
    config: Optional[types.GenerateContentConfigOrDict] = None

    # OpenAIImagesInput + GoogleVertexAIImagesInput 合并字段
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    aspect_ratio: Optional[Literal["1:1", "9:16", "16:9", "4:3", "3:4"]] = None
    guidance_scale: Optional[float] = None
    language: Optional[str] = None
    output_gcs_uri: Optional[str] = None
    add_watermark: Optional[bool] = None
    safety_filter_level: Optional[Literal["block_most", "block_some", "block_few", "block_fewest"]] = None
    person_generation: Optional[Literal["dont_allow", "allow_adult", "allow_all"]] = None
    quality: Optional[Literal["standard", "hd"]] | NotGiven = NOT_GIVEN
    size: Optional[Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]] | NotGiven = NOT_GIVEN
    style: Optional[Literal["vivid", "natural"]] | NotGiven = NOT_GIVEN
    number_of_images: Optional[int] = None  # Google 用法

    model_config = {
        "arbitrary_types_allowed": True
    }


class ModelRequest(ModelRequestInput):
    user_context: UserContext  # 用户信息

    @model_validator(mode="after")
    def validate_by_provider_and_invoke_type(self) -> "ModelRequest":
        """根据 provider 和 invoke_type 动态校验具体输入模型字段。"""
        # 动态获取 allowed fields
        base_allowed = {"provider", "channel", "invoke_type", "user_context"}
        google_allowed = base_allowed | set(GoogleGenAiInput.model_fields.keys())
        openai_responses_allowed = base_allowed | set(OpenAIResponsesInput.model_fields.keys())
        openai_chat_allowed = base_allowed | set(OpenAIChatCompletionsInput.model_fields.keys())
        openai_images_allowed = base_allowed | set(OpenAIImagesInput.model_fields.keys())
        google_vertexai_images_allowed = base_allowed | set(GoogleVertexAIImagesInput.model_fields.keys())

        # 各模型类型必填字段
        google_required_fields = {"model", "contents"}
        google_vertexai_image_required_fields = {"model", "prompt"}

        openai_responses_required_fields = {"input", "model"}
        openai_chat_required_fields = {"messages", "model"}
        openai_image_required_fields = {"prompt"}

        # 选择需要校验的字段集合
        # 动态分支逻辑
        match (self.provider, self.invoke_type):
            case (ProviderType.GOOGLE, InvokeType.GENERATION):
                allowed_fields = google_allowed
                expected_fields = google_required_fields
            case (ProviderType.GOOGLE, InvokeType.IMAGE_GENERATION):
                allowed_fields = google_vertexai_images_allowed
                expected_fields = google_vertexai_image_required_fields
            case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.RESPONSES | InvokeType.GENERATION):
                allowed_fields = openai_responses_allowed
                expected_fields = openai_responses_required_fields
            case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.CHAT_COMPLETIONS):
                allowed_fields = openai_chat_allowed
                expected_fields = openai_chat_required_fields
            case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_GENERATION):
                allowed_fields = openai_images_allowed
                expected_fields = openai_image_required_fields
            case _:
                raise ValueError(f"Unsupported provider/invoke_type combination: {self.provider} + {self.invoke_type}")

        # 校验必填字段是否缺失
        missing = [field for field in expected_fields if getattr(self, field, None) is None]
        if missing:
            raise ValueError(
                f"Missing required fields for provider={self.provider} and invoke_type={self.invoke_type}: {missing}")

        # 检查是否有非法字段
        illegal_fields = []
        valid_fields = {"provider", "channel", "invoke_type"} if self.invoke_type == InvokeType.IMAGE_GENERATION else {
            "provider", "channel", "invoke_type", "stream"}
        for name, value in self.__dict__.items():
            if name in valid_fields:
                continue
            if name not in allowed_fields and value is not None and not isinstance(value, NotGiven):
                illegal_fields.append(name)

        if illegal_fields:
            raise ValueError(
                f"Unsupported fields for provider={self.provider} and invoke_type={self.invoke_type}: {illegal_fields}")

        return self


class BatchModelRequestItem(ModelRequestInput):
    custom_id: Optional[str] = None
    priority: Optional[int] = None  # （可选、预留字段）批量调用时执行的优先级

    @model_validator(mode="after")
    def validate_by_provider_and_invoke_type(self) -> "BatchModelRequestItem":
        """根据 provider 和 invoke_type 动态校验具体输入模型字段。"""
        # 动态获取 allowed fields
        base_allowed = {"provider", "channel", "invoke_type", "user_context"}
        google_allowed = base_allowed | set(GoogleGenAiInput.model_fields.keys())
        openai_responses_allowed = base_allowed | set(OpenAIResponsesInput.model_fields.keys())
        openai_chat_allowed = base_allowed | set(OpenAIChatCompletionsInput.model_fields.keys())
        openai_images_allowed = base_allowed | set(OpenAIImagesInput.model_fields.keys())
        google_vertexai_images_allowed = base_allowed | set(GoogleVertexAIImagesInput.model_fields.keys())

        # 各模型类型必填字段
        google_required_fields = {"model", "contents"}
        google_vertexai_image_required_fields = {"model", "prompt"}

        openai_responses_required_fields = {"input", "model"}
        openai_chat_required_fields = {"messages", "model"}
        openai_image_required_fields = {"prompt"}

        # 选择需要校验的字段集合
        # 动态分支逻辑
        match (self.provider, self.invoke_type):
            case (ProviderType.GOOGLE, InvokeType.GENERATION):
                allowed_fields = google_allowed
                expected_fields = google_required_fields
            case (ProviderType.GOOGLE, InvokeType.IMAGE_GENERATION):
                allowed_fields = google_vertexai_images_allowed
                expected_fields = google_vertexai_image_required_fields
            case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.RESPONSES | InvokeType.GENERATION):
                allowed_fields = openai_responses_allowed
                expected_fields = openai_responses_required_fields
            case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.CHAT_COMPLETIONS):
                allowed_fields = openai_chat_allowed
                expected_fields = openai_chat_required_fields
            case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_GENERATION):
                allowed_fields = openai_images_allowed
                expected_fields = openai_image_required_fields
            case _:
                raise ValueError(f"Unsupported provider/invoke_type combination: {self.provider} + {self.invoke_type}")

        # 校验必填字段是否缺失
        missing = [field for field in expected_fields if getattr(self, field, None) is None]
        if missing:
            raise ValueError(
                f"Missing required fields for provider={self.provider} and invoke_type={self.invoke_type}: {missing}")

        # 检查是否有非法字段
        illegal_fields = []
        valid_fields = {"provider", "channel", "invoke_type"} if self.invoke_type == InvokeType.IMAGE_GENERATION else {
            "provider", "channel", "invoke_type", "stream"}
        for name, value in self.__dict__.items():
            if name in valid_fields:
                continue
            if name not in allowed_fields and value is not None and not isinstance(value, NotGiven):
                illegal_fields.append(name)

        if illegal_fields:
            raise ValueError(
                f"Unsupported fields for provider={self.provider} and invoke_type={self.invoke_type}: {illegal_fields}")

        return self


class BatchModelRequest(BaseModel):
    user_context: UserContext  # 用户信息
    items: List[BatchModelRequestItem]  # 批量请求项列表
