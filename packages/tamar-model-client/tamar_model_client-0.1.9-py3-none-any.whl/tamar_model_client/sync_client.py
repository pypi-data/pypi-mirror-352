import asyncio
import atexit
import logging
from typing import Optional, Union, Iterator

from .async_client import AsyncTamarModelClient
from .schemas import ModelRequest, BatchModelRequest, ModelResponse, BatchModelResponse

logger = logging.getLogger(__name__)


class TamarModelClient:
    """
    同步版本的模型管理客户端，用于非异步环境（如 Flask、Django、脚本）。
    内部封装 AsyncTamarModelClient 并处理事件循环兼容性。
    """
    _loop: Optional[asyncio.AbstractEventLoop] = None

    def __init__(
            self,
            server_address: Optional[str] = None,
            jwt_secret_key: Optional[str] = None,
            jwt_token: Optional[str] = None,
            default_payload: Optional[dict] = None,
            token_expires_in: int = 3600,
            max_retries: int = 3,
            retry_delay: float = 1.0,
    ):
        # 初始化全局事件循环，仅创建一次
        if not TamarModelClient._loop:
            try:
                TamarModelClient._loop = asyncio.get_running_loop()
            except RuntimeError:
                TamarModelClient._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(TamarModelClient._loop)

        self._loop = TamarModelClient._loop

        self._async_client = AsyncTamarModelClient(
            server_address=server_address,
            jwt_secret_key=jwt_secret_key,
            jwt_token=jwt_token,
            default_payload=default_payload,
            token_expires_in=token_expires_in,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )
        atexit.register(self._safe_sync_close)

    def invoke(self, model_request: ModelRequest, timeout: Optional[float] = None) -> Union[
        ModelResponse, Iterator[ModelResponse]]:
        """
        同步调用单个模型任务
        """
        if model_request.stream:
            async def stream():
                async for r in await self._async_client.invoke(model_request, timeout=timeout):
                    yield r

            return self._sync_wrap_async_generator(stream())
        return self._run_async(self._async_client.invoke(model_request, timeout=timeout))

    def invoke_batch(self, batch_model_request: BatchModelRequest,
                     timeout: Optional[float] = None) -> BatchModelResponse:
        """
        同步调用批量模型任务
        """
        return self._run_async(self._async_client.invoke_batch(batch_model_request, timeout=timeout))

    def close(self):
        """手动关闭 gRPC 通道"""
        self._run_async(self._async_client.close())

    def _safe_sync_close(self):
        """退出时自动关闭"""
        try:
            self._run_async(self._async_client.close())
            logger.info("✅ gRPC channel closed at exit")
        except Exception as e:
            logger.warning(f"❌ gRPC channel close failed at exit: {e}")

    def _run_async(self, coro):
        """统一运行协程，兼容已存在的事件循环"""
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        except RuntimeError:
            return self._loop.run_until_complete(coro)

    def _sync_wrap_async_generator(self, async_gen_func):
        """
        将 async generator 转换为同步 generator，逐条 yield。
        """
        loop = self._loop

        # 创建异步生成器对象
        agen = async_gen_func

        class SyncGenerator:
            def __iter__(self_inner):
                return self_inner

            def __next__(self_inner):
                try:
                    return loop.run_until_complete(agen.__anext__())
                except StopAsyncIteration:
                    raise StopIteration

        return SyncGenerator()
