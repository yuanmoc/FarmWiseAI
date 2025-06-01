from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.schemas.user import UserLogin
from app.services.auth import authenticate_user, create_access_token
from app.api.api_v1.deps import get_db
from app.schemas.token import Token
import logging

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: UserLogin = None
) -> Any:
    """
    表单登录（用于 Swagger UI 测试）
    
    参数:
    - username: 用户邮箱
    - password: 用户密码
    """
    try:
        logger.info(f"尝试登录用户: {form_data.email}")
        user = authenticate_user(db, form_data.email, form_data.password)
        if not user:
            logger.warning(f"登录失败: 用户名或密码错误 - {form_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"Authorization": "Bearer"},
            )

        if not user.is_active:
            logger.warning(f"登录失败: 用户已被停用 - {form_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户已被停用"
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"email": user.email, "user_id": user.id}, expires_delta=access_token_expires
        )

        logger.info(f"用户登录成功: {user.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"登录过程中发生错误: {str(e)}")
        raise
