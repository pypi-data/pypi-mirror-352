from enum import Enum


class InvokeType(str, Enum):
    """模型调用类型枚举"""
    RESPONSES = "responses"
    CHAT_COMPLETIONS = "chat-completions"

    # 默认的
    GENERATION = "generation"
