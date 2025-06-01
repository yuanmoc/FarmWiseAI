from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, knowledge, qa

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["知识库"])
api_router.include_router(qa.router, prefix="/qa", tags=["智能问答"])