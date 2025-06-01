from typing import Generator
from datetime import datetime, timedelta

from fastapi import HTTPException, Response, Request
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.exc import InvalidTokenError
from starlette import status

from app.core.config import settings
from app.models.base import SessionLocal, engine
from app.services.auth import create_access_token


def get_db() -> Generator:
    """获取数据库会话"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_engine():
    return engine


async def verify_and_refresh_token(
        request: Request = None,
        response: Response = None
):
    # 跳过不需要认证的路由
    token = request.headers.get("Authorization")
    if request.url.path in ["/api/v1/auth/login", "/docs", "/openapi.json"]:
        return
    """
    验证并刷新token
    返回: (user_id, is_refreshed)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"Authorization": "Bearer"},
    )

    try:
        if not token or not token.startswith("Bearer"):
            raise credentials_exception

        token = token.replace("Bearer", "").strip()
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        request.state.user_id = user_id

        # 检查token是否即将过期（比如还有30分钟过期）
        exp = payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp)
            now = datetime.utcnow()
            # 如果token将在30分钟内过期，生成新token
            if exp_datetime - now < timedelta(minutes=30):
                new_token = create_access_token(
                    data=payload,
                    expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                )
                if response:
                    # 在响应头中返回新token
                    response.headers["X-New-Token"] = new_token
                return user_id, True

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期",
            headers={"Authenticate": "Bearer"},
        )
    except (JWTError, InvalidTokenError):
        raise credentials_exception
