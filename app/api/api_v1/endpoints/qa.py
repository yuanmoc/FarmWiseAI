from typing import Dict, List
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.services.qa import QAService
from app.schemas.qa import QuestionCreate

router = APIRouter()
qa_service = QAService()

@router.get("/history")
async def get_chat_history(
    request: Request,
) -> List[Dict[str, str]]:
    """
    获取聊天历史记录
    """
    try:
        user_id = request.state.user_id
        print("request.state.user_id", request.state.user_id)
        return qa_service.get_chat_history(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ask")
async def ask_question(
    *,
    request: Request,
    question_in: QuestionCreate
) -> StreamingResponse:
    """
    提问并获取流式回答
    """
    try:
        user_id = request.state.user_id
        print("request.state.user_id", request.state.user_id)
        return StreamingResponse(
            qa_service.get_answer_stream(
                question=question_in.question,
                user_id=user_id
            ),
            media_type='text/event-stream'
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/clear-context")
async def clear_conversation_context(
    request: Request,
) -> Dict[str, str]:
    """
    清除对话上下文
    """
    try:
        user_id = request.state.user_id
        print("request.state.user_id", request.state.user_id)
        qa_service.clear_memory(user_id=user_id)
        return {"message": "对话上下文已清除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
