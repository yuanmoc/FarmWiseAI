from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    file_path = Column(String)
    file_type = Column(String)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 文档摘要
    summary = Column(Text)
    # 文档向量ID（存储在Milvus中的ID）
    vector_id = Column(String)
    # 文档标签
    tags = Column(String)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    children = relationship("Category") 