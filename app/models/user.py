from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 用户类型（农民、科研人员、推广人员）
    user_type = Column(String)
    # 地理位置
    location = Column(String)
    # 主要种植作物
    main_crops = Column(String) 