from typing import List, Dict, AsyncGenerator
import json

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory

from app.services.knowledge import KnowledgeService
from app.services.session import SessionManager


class QAService:
    def __init__(self):
        self.knowledge_service = KnowledgeService()
        self.llm = self.knowledge_service.model
        self.session_manager = SessionManager()

        # 创建检索链
        self.retriever = self.knowledge_service.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        # 创建提示模板
        self.system_template = """你是一个智慧农业咨询助手。"""

    def get_chat_history(self, user_id: str) -> List[Dict[str, str]]:
        """获取用户的聊天历史记录"""
        try:
            session_id = self.session_manager.get_session_id(user_id)
            message_history = self.session_manager.get_message_history(session_id)
            messages = []
            
            # 将消息历史转换为前端需要的格式
            for message in message_history.messages:
                if isinstance(message, HumanMessage):
                    messages.append({
                        "type": "user",
                        "content": message.content
                    })
                elif isinstance(message, AIMessage):
                    messages.append({
                        "type": "assistant",
                        "content": message.content
                    })
            
            return messages
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []

    def get_answer_stream(self, question: str, user_id: str) -> AsyncGenerator[str, None]:
        """生成流式回答"""
        try:
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.system_template),
                    MessagesPlaceholder(variable_name='chat_history'),
                    ("user", """{question}""")
                ]
            )

            # 创建基础链
            base_chain = prompt | self.llm | StrOutputParser()

            # 创建带消息历史的链
            chain_with_history = RunnableWithMessageHistory(
                base_chain,
                get_session_history=self.session_manager.get_message_history,
                input_messages_key="question",
                history_messages_key="chat_history"
            )

            session_id = self.session_manager.get_session_id(user_id)
            # 生成流式回答
            for chunk in chain_with_history.stream(
                input={"question": question},
                config={"configurable": {"session_id": session_id}}
            ):
                # 构建SSE消息
                yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"

        except Exception as e:
            print(f"Error getting response: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    def clear_memory(self, user_id: str):
        """清除指定用户的对话历史"""
        self.session_manager.clear_history(user_id)
