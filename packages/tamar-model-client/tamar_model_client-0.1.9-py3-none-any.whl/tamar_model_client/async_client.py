import asyncio
import atexit
import base64
import json
import logging
import os

import grpc
from typing import Optional, AsyncIterator, Union, Iterable

from openai import NOT_GIVEN
from pydantic import BaseModel

from .auth import JWTAuthHandler
from .enums import ProviderType, InvokeType
from .exceptions import ConnectionError, ValidationError
from .schemas import ModelRequest, ModelResponse, BatchModelRequest, BatchModelResponse
from .generated import model_service_pb2, model_service_pb2_grpc
from .schemas.inputs import GoogleGenAiInput, OpenAIResponsesInput, OpenAIChatCompletionsInput, \
    GoogleVertexAIImagesInput, OpenAIImagesInput

if not logging.getLogger().hasHandlers():
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 2 ** 31 - 1  # 对于32位系统


def is_effective_value(value) -> bool:
    """
    递归判断value是否是有意义的有效值
    """
    if value is None or value is NOT_GIVEN:
        return False

    if isinstance(value, str):
        return value.strip() != ""

    if isinstance(value, bytes):
        return len(value) > 0

    if isinstance(value, dict):
        for v in value.values():
            if is_effective_value(v):
                return True
        return False

    if isinstance(value, list):
        for item in value:
            if is_effective_value(item):
                return True
        return False

    return True  # 其他类型（int/float/bool）只要不是None就算有效


def serialize_value(value):
    """递归处理单个值，处理BaseModel, dict, list, bytes"""
    if not is_effective_value(value):
        return None
    if isinstance(value, BaseModel):
        return serialize_value(value.model_dump())
    if hasattr(value, "dict") and callable(value.dict):
        return serialize_value(value.dict())
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    if isinstance(value, list) or (isinstance(value, Iterable) and not isinstance(value, (str, bytes))):
        return [serialize_value(v) for v in value]
    if isinstance(value, bytes):
        return f"bytes:{base64.b64encode(value).decode('utf-8')}"
    return value


from typing import Any


def remove_none_from_dict(data: Any) -> Any:
    """
    遍历 dict/list，递归删除 value 为 None 的字段
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            if value is None:
                continue
            cleaned_value = remove_none_from_dict(value)
            new_dict[key] = cleaned_value
        return new_dict
    elif isinstance(data, list):
        return [remove_none_from_dict(item) for item in data]
    else:
        return data


class AsyncTamarModelClient:
    def __init__(
            self,
            server_address: Optional[str] = None,
            jwt_secret_key: Optional[str] = None,
            jwt_token: Optional[str] = None,
            default_payload: Optional[dict] = None,
            token_expires_in: int = 3600,
            max_retries: int = 3,  # 最大重试次数
            retry_delay: float = 1.0,  # 初始重试延迟（秒）
    ):
        # 服务端地址
        self.server_address = server_address or os.getenv("MODEL_MANAGER_SERVER_ADDRESS")
        if not self.server_address:
            raise ValueError("Server address must be provided via argument or environment variable.")
        self.default_invoke_timeout = float(os.getenv("MODEL_MANAGER_SERVER_INVOKE_TIMEOUT", 30.0))

        # JWT 配置
        self.jwt_secret_key = jwt_secret_key or os.getenv("MODEL_MANAGER_SERVER_JWT_SECRET_KEY")
        self.jwt_handler = JWTAuthHandler(self.jwt_secret_key)
        self.jwt_token = jwt_token  # 用户传入的 Token（可选）
        self.default_payload = default_payload
        self.token_expires_in = token_expires_in

        # === TLS/Authority 配置 ===
        self.use_tls = os.getenv("MODEL_MANAGER_SERVER_GRPC_USE_TLS", "true").lower() == "true"
        self.default_authority = os.getenv("MODEL_MANAGER_SERVER_GRPC_DEFAULT_AUTHORITY")

        # === 重试配置 ===
        self.max_retries = max_retries if max_retries is not None else int(
            os.getenv("MODEL_MANAGER_SERVER_GRPC_MAX_RETRIES", 3))
        self.retry_delay = retry_delay if retry_delay is not None else float(
            os.getenv("MODEL_MANAGER_SERVER_GRPC_RETRY_DELAY", 1.0))

        # === gRPC 通道相关 ===
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[model_service_pb2_grpc.ModelServiceStub] = None
        self._closed = False
        atexit.register(self._safe_sync_close)  # 注册进程退出自动关闭

    def _build_auth_metadata(self) -> list:
        # if not self.jwt_token and self.jwt_handler:
        # 更改为每次请求都生成一次token
        if self.jwt_handler:
            self.jwt_token = self.jwt_handler.encode_token(self.default_payload, expires_in=self.token_expires_in)
        return [("authorization", f"Bearer {self.jwt_token}")] if self.jwt_token else []

    async def _ensure_initialized(self):
        """初始化 gRPC 通道，支持 TLS 与重试机制"""
        if self.channel and self.stub:
            return

        retry_count = 0
        options = [
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
        ]
        if self.default_authority:
            options.append(("grpc.default_authority", self.default_authority))

        while retry_count <= self.max_retries:
            try:
                if self.use_tls:
                    credentials = grpc.ssl_channel_credentials()
                    self.channel = grpc.aio.secure_channel(
                        self.server_address,
                        credentials,
                        options=options
                    )
                    logger.info("🔐 Using secure gRPC channel (TLS enabled)")
                else:
                    self.channel = grpc.aio.insecure_channel(
                        self.server_address,
                        options=options
                    )
                    logger.info("🔓 Using insecure gRPC channel (TLS disabled)")
                await self.channel.channel_ready()
                self.stub = model_service_pb2_grpc.ModelServiceStub(self.channel)
                logger.info(f"✅ gRPC channel initialized to {self.server_address}")
                return
            except grpc.FutureTimeoutError as e:
                logger.warning(f"❌ gRPC channel initialization timed out: {str(e)}")
            except grpc.RpcError as e:
                logger.warning(f"❌ gRPC channel initialization failed: {str(e)}")
            except Exception as e:
                logger.warning(f"❌ Unexpected error during channel initialization: {str(e)}")

            retry_count += 1
            if retry_count > self.max_retries:
                raise ConnectionError(f"❌ Failed to initialize gRPC channel after {self.max_retries} retries.")

            # 指数退避：延迟时间 = retry_delay * (2 ^ (retry_count - 1))
            delay = self.retry_delay * (2 ** (retry_count - 1))
            logger.info(f"🚀 Retrying connection (attempt {retry_count}/{self.max_retries}) after {delay:.2f}s delay...")
            await asyncio.sleep(delay)

    async def _stream(self, model_request, metadata, invoke_timeout) -> AsyncIterator[ModelResponse]:
        try:
            async for response in self.stub.Invoke(model_request, metadata=metadata, timeout=invoke_timeout):
                yield ModelResponse(
                    content=response.content,
                    usage=json.loads(response.usage) if response.usage else None,
                    raw_response=json.loads(response.raw_response) if response.raw_response else None,
                    error=response.error or None,
                )
        except grpc.RpcError as e:
            raise ConnectionError(f"gRPC call failed: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Invalid input: {str(e)}")

    async def invoke(self, model_request: ModelRequest, timeout: Optional[float] = None) -> Union[
        ModelResponse, AsyncIterator[ModelResponse]]:
        """
       通用调用模型方法。

        Args:
            model_request: ModelRequest 对象，包含请求参数。

        Yields:
            ModelResponse: 支持流式或非流式的模型响应

        Raises:
            ValidationError: 输入验证失败。
            ConnectionError: 连接服务端失败。
        """
        await self._ensure_initialized()

        if not self.default_payload:
            self.default_payload = {
                "org_id": model_request.user_context.org_id or "",
                "user_id": model_request.user_context.user_id or ""
            }

        # 动态根据 provider/invoke_type 决定使用哪个 input 字段
        try:
            # 选择需要校验的字段集合
            # 动态分支逻辑
            match (model_request.provider, model_request.invoke_type):
                case (ProviderType.GOOGLE, InvokeType.GENERATION):
                    allowed_fields = GoogleGenAiInput.model_fields.keys()
                case (ProviderType.GOOGLE, InvokeType.IMAGE_GENERATION):
                    allowed_fields = GoogleVertexAIImagesInput.model_fields.keys()
                case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.RESPONSES | InvokeType.GENERATION):
                    allowed_fields = OpenAIResponsesInput.model_fields.keys()
                case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.CHAT_COMPLETIONS):
                    allowed_fields = OpenAIChatCompletionsInput.model_fields.keys()
                case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_GENERATION):
                    allowed_fields = OpenAIImagesInput.model_fields.keys()
                case _:
                    raise ValueError(
                        f"Unsupported provider/invoke_type combination: {model_request.provider} + {model_request.invoke_type}")

            # 将 ModelRequest 转 dict，过滤只保留 base + allowed 的字段
            model_request_dict = model_request.model_dump(exclude_unset=True)

            grpc_request_kwargs = {}
            for field in allowed_fields:
                if field in model_request_dict:
                    value = model_request_dict[field]

                    # 跳过无效的值
                    if not is_effective_value(value):
                        continue

                    # 序列化grpc不支持的类型
                    grpc_request_kwargs[field] = serialize_value(value)

                    # 清理 serialize后的 grpc_request_kwargs
                    grpc_request_kwargs = remove_none_from_dict(grpc_request_kwargs)

            request = model_service_pb2.ModelRequestItem(
                provider=model_request.provider.value,
                channel=model_request.channel.value,
                invoke_type=model_request.invoke_type.value,
                stream=model_request.stream or False,
                org_id=model_request.user_context.org_id or "",
                user_id=model_request.user_context.user_id or "",
                client_type=model_request.user_context.client_type or "",
                extra=grpc_request_kwargs
            )

        except Exception as e:
            raise ValueError(f"构建请求失败: {str(e)}") from e

        metadata = self._build_auth_metadata()

        invoke_timeout = timeout or self.default_invoke_timeout
        if model_request.stream:
            return self._stream(request, metadata, invoke_timeout)
        else:
            async for response in self.stub.Invoke(request, metadata=metadata, timeout=invoke_timeout):
                return ModelResponse(
                    content=response.content,
                    usage=json.loads(response.usage) if response.usage else None,
                    raw_response=json.loads(response.raw_response) if response.raw_response else None,
                    error=response.error or None,
                    custom_id=None,
                    request_id=response.request_id if response.request_id else None,
                )

    async def invoke_batch(self, batch_request_model: BatchModelRequest, timeout: Optional[float] = None) -> \
            BatchModelResponse:
        """
        批量模型调用接口

        Args:
            batch_request_model: 多条 BatchModelRequest 输入
            timeout: 调用超时，单位秒

        Returns:
            BatchModelResponse: 批量请求的结果
        """
        await self._ensure_initialized()

        if not self.default_payload:
            self.default_payload = {
                "org_id": batch_request_model.user_context.org_id or "",
                "user_id": batch_request_model.user_context.user_id or ""
            }

        metadata = self._build_auth_metadata()

        # 构造批量请求
        items = []
        for model_request_item in batch_request_model.items:
            # 动态根据 provider/invoke_type 决定使用哪个 input 字段
            try:
                match (model_request_item.provider, model_request_item.invoke_type):
                    case (ProviderType.GOOGLE, InvokeType.GENERATION):
                        allowed_fields = GoogleGenAiInput.model_fields.keys()
                    case (ProviderType.GOOGLE, InvokeType.IMAGE_GENERATION):
                        allowed_fields = GoogleVertexAIImagesInput.model_fields.keys()
                    case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.RESPONSES | InvokeType.GENERATION):
                        allowed_fields = OpenAIResponsesInput.model_fields.keys()
                    case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.CHAT_COMPLETIONS):
                        allowed_fields = OpenAIChatCompletionsInput.model_fields.keys()
                    case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_GENERATION):
                        allowed_fields = OpenAIImagesInput.model_fields.keys()
                    case _:
                        raise ValueError(
                            f"Unsupported provider/invoke_type combination: {model_request_item.provider} + {model_request_item.invoke_type}")

                # 将 ModelRequest 转 dict，过滤只保留 base + allowed 的字段
                model_request_dict = model_request_item.model_dump(exclude_unset=True)

                grpc_request_kwargs = {}
                for field in allowed_fields:
                    if field in model_request_dict:
                        value = model_request_dict[field]

                        # 跳过无效的值
                        if not is_effective_value(value):
                            continue

                        # 序列化grpc不支持的类型
                        grpc_request_kwargs[field] = serialize_value(value)

                        # 清理 serialize后的 grpc_request_kwargs
                        grpc_request_kwargs = remove_none_from_dict(grpc_request_kwargs)

                items.append(model_service_pb2.ModelRequestItem(
                    provider=model_request_item.provider.value,
                    channel=model_request_item.channel.value,
                    invoke_type=model_request_item.invoke_type.value,
                    stream=model_request_item.stream or False,
                    custom_id=model_request_item.custom_id or "",
                    priority=model_request_item.priority or 1,
                    org_id=batch_request_model.user_context.org_id or "",
                    user_id=batch_request_model.user_context.user_id or "",
                    client_type=batch_request_model.user_context.client_type or "",
                    extra=grpc_request_kwargs,
                ))

            except Exception as e:
                raise ValueError(f"构建请求失败: {str(e)}，item={model_request_item.custom_id}") from e

        try:
            # 超时处理逻辑
            invoke_timeout = timeout or self.default_invoke_timeout

            # 调用 gRPC 接口
            response = await self.stub.BatchInvoke(
                model_service_pb2.ModelRequest(items=items),
                timeout=invoke_timeout,
                metadata=metadata
            )

            result = []
            for res_item in response.items:
                result.append(ModelResponse(
                    content=res_item.content,
                    usage=json.loads(res_item.usage) if res_item.usage else None,
                    raw_response=json.loads(res_item.raw_response) if res_item.raw_response else None,
                    error=res_item.error or None,
                    custom_id=res_item.custom_id if res_item.custom_id else None
                ))
            return BatchModelResponse(
                request_id=response.request_id if response.request_id else None,
                responses=result
            )
        except grpc.RpcError as e:
            raise ConnectionError(f"BatchInvoke failed: {str(e)}")

    async def close(self):
        """关闭 gRPC 通道"""
        if self.channel and not self._closed:
            await self.channel.close()
            self._closed = True
            await self.channel.close()
            logger.info("✅ gRPC channel closed")

    def _safe_sync_close(self):
        """进程退出时自动关闭 channel（事件循环处理兼容）"""
        if self.channel and not self._closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except Exception as e:
                logger.warning(f"❌ gRPC channel close failed at exit: {e}")

    async def __aenter__(self):
        """支持 async with 自动初始化连接"""
        await self._ensure_initialized()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """支持 async with 自动关闭连接"""
        await self.close()
