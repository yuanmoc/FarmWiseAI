from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from app.api.api_v1.deps import get_engine


class SessionManager:
    """会话管理器"""

    def get_session_id(self, user_id: str) -> str:
        """
        获取会话ID
        目前直接使用用户ID作为会话ID，后续可以扩展为支持多会话
        """
        return str(f"user_{user_id}")

    def get_message_history(self, session_id: str) -> BaseChatMessageHistory:
        """获取用户的消息历史存储"""
        return SQLChatMessageHistory(
            session_id=session_id,
            connection=get_engine()
        )

    def clear_history(self, user_id: str) -> None:
        """清除用户的对话历史"""
        session_id = self.get_session_id(user_id)
        message_history = self.get_message_history(session_id)
        message_history.clear()
