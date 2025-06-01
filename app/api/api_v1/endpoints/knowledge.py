from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from app.api.api_v1.deps import get_db
from app.services.knowledge import KnowledgeService
from app.schemas.knowledge import (
    DocumentResponse, 
    CategoryCreate, 
    Category, 
    CategoryTree,
    PageResponse,
    DocumentUpdate
)
import os
from app.core.config import settings

router = APIRouter()
knowledge_service = KnowledgeService()

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(...)
) -> Any:
    """
    上传文档到知识库
    """
    try:
        doc = await knowledge_service.process_document(db, file, title, category)
        return doc
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/documents/search")
async def search_documents(
    query: str,
    top_k: int = 5,
    db: Session = Depends(get_db)
) -> Any:
    """
    搜索知识库文档
    """
    try:
        results = await knowledge_service.search_documents(query, top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/categories", response_model=Category)
async def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate
) -> Any:
    """
    创建文档分类
    """
    try:
        category = await knowledge_service.create_category(
            db,
            name=category_in.name,
            description=category_in.description,
            parent_id=category_in.parent_id
        )
        return category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/categories", response_model=CategoryTree)
async def get_categories(
    db: Session = Depends(get_db)
) -> Any:
    """
    获取分类树
    """
    try:
        categories = await knowledge_service.get_category_tree(db)
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/documents", response_model=PageResponse[DocumentResponse])
async def get_documents(
    category: str = Query(None, description="按分类筛选文档"),
    page: int = Query(1, description="页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取文档列表，支持分页
    """
    try:
        documents, total = await knowledge_service.get_documents(
            db, 
            category=category,
            page=page,
            size=size
        )
        return {
            "items": documents,
            "total": total,
            "page": page,
            "size": size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    删除文档
    """
    try:
        success = await knowledge_service.delete_document(db, doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/documents/{doc_id}/reprocess", response_model=DocumentResponse)
async def reprocess_document(
    doc_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    重新处理文档的向量数据
    """
    try:
        doc = await knowledge_service.reprocess_document(db, doc_id)
        return doc
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/documents/{doc_id}/vectors", response_model=PageResponse[dict])
async def get_document_vectors(
    doc_id: int,
    page: int = Query(1, description="页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取文档的向量数据列表，支持分页
    """
    try:
        vectors, total = await knowledge_service.get_document_vectors(
            db, 
            doc_id,
            page=page,
            size=size
        )
        return {
            "items": vectors,
            "total": total,
            "page": page,
            "size": size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/documents/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: int,
    *,
    db: Session = Depends(get_db),
    doc_in: DocumentUpdate
) -> Any:
    """
    更新文档信息
    """
    try:
        doc = await knowledge_service.update_document(db, doc_id, doc_in)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 