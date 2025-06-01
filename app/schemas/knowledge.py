from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')

class DocumentBase(BaseModel):
    title: str
    category: str

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    """文档更新模型"""
    pass

class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    file_type: str
    created_at: datetime
    updated_at: datetime
    vector_id: Optional[str] = None

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    """创建分类请求模型"""
    parent_id: Optional[int] = None

class Category(CategoryBase):
    """分类响应模型"""
    id: int
    parent_id: Optional[int] = None
    children: Optional[List['Category']] = None

    class Config:
        from_attributes = True

# 解决循环引用
Category.model_rebuild()

class CategoryTree(BaseModel):
    """分类树响应模型"""
    categories: List[Category]

# 添加分页响应模型
class PageResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int 