from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserLogin(BaseModel):
    """用户登录请求模型"""
    email: EmailStr = Field(..., description="用户邮箱", example="123@qq.com")
    password: str = Field(..., description="用户密码", example="admin123")

class UserBase(BaseModel):
    """用户基础信息模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    full_name: Optional[str] = Field(None, description="用户全名")
    user_type: Optional[str] = Field(None, description="用户类型（农民、科研人员、推广人员）")
    location: Optional[str] = Field(None, description="地理位置")
    main_crops: Optional[str] = Field(None, description="主要种植作物")

class UserCreate(UserBase):
    """用户创建请求模型"""
    password: str = Field(..., min_length=6, description="用户密码")
    confirm_password: str = Field(..., description="确认密码")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword",
                "confirm_password": "strongpassword",
                "full_name": "张三",
                "user_type": "农民",
                "location": "江苏省南京市",
                "main_crops": "水稻,小麦"
            }
        }

class UserUpdate(BaseModel):
    """用户信息更新请求模型"""
    email: Optional[EmailStr] = Field(None, description="用户邮箱")
    full_name: Optional[str] = Field(None, description="用户全名")
    password: Optional[str] = Field(None, min_length=6, description="新密码")
    old_password: Optional[str] = Field(None, description="原密码")
    user_type: Optional[str] = Field(None, description="用户类型")
    location: Optional[str] = Field(None, description="地理位置")
    main_crops: Optional[str] = Field(None, description="主要种植作物")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "李四",
                "location": "浙江省杭州市",
                "main_crops": "茶叶,水果"
            }
        }

class UserInDBBase(UserBase):
    """数据库中的用户模型基类"""
    id: int
    is_active: bool = Field(True, description="是否激活")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserInDB(UserInDBBase):
    """数据库中的用户完整模型"""
    hashed_password: str

class User(UserInDBBase):
    """API响应中的用户模型"""
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "张三",
                "user_type": "农民",
                "location": "江苏省南京市",
                "main_crops": "水稻,小麦",
                "is_active": True,
                "created_at": "2024-03-20T10:00:00",
                "updated_at": "2024-03-20T10:00:00"
            }
        }

class UserList(BaseModel):
    """用户列表响应模型"""
    total: int
    items: list[User]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 1,
                "items": [
                    {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "张三",
                        "user_type": "农民",
                        "location": "江苏省南京市",
                        "main_crops": "水稻,小麦",
                        "is_active": True,
                        "created_at": "2024-03-20T10:00:00",
                        "updated_at": "2024-03-20T10:00:00"
                    }
                ]
            }
        } 