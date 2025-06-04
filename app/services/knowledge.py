import uuid
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.knowledge import Document, Category
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_milvus import Milvus
from app.core.config import settings
import os
from datetime import datetime

from app.schemas.knowledge import DocumentUpdate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

class KnowledgeService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            base_url=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_EMBEDDINGS
        )

        self.model = ChatOpenAI(
            base_url=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_MODEL,
            temperature=0.7
        )
        # 默认使用uri
        connection_args = {"uri": settings.MILVUS_URI}
        if settings.MILVUS_URI is None or settings.MILVUS_URI == '':
            connection_args = {
                "host": settings.MILVUS_HOST,
                "port": settings.MILVUS_PORT,
            }

        # 使用缓存的向量存储实例
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            collection_name=settings.MILVUS_COLLECTION,
            connection_args=connection_args,
            auto_id=True
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    async def process_document(self, db: Session, file: UploadFile, title: str, category: str) -> Document:
        """处理文档并存储到知识库"""
        file_path = ''
        try:
            # 文件名称
            file_type = os.path.splitext(file.filename)[1]
            source_file_name = os.path.splitext(file.filename)[0]
            file_name = str(uuid.uuid4()).replace("-", "") + file_type

            # 保存文件
            file_path = os.path.join(settings.UPLOAD_DIR, file_name)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            # 注意：需要将二进制内容解码为字符串
            decoded_content = content.decode('utf-8')

            # 分割文本
            texts = self.text_splitter.split_text(decoded_content)

            # 为每个文本块添加元数据
            metadatas = [{"title": source_file_name, "category": category, "chunk_index": i} for i, _ in
                         enumerate(texts)]

            vector_ids = self.vector_store.add_texts(
                texts=texts,
                metadatas=metadatas
            )
            print(vector_ids)

            # 创建文档记录
            doc = Document(
                title=source_file_name,
                content=decoded_content,
                file_path=file_path,
                file_type=file_type,
                category=category,
                vector_id=','.join(map(str, vector_ids)) if vector_ids else None  # 转换为字符串
            )

            db.add(doc)
            db.commit()
            db.refresh(doc)
            return doc

        except Exception as e:
            print(f"Error processing document: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)  # 清理上传的文件
            raise e

    async def reprocess_document(self, db: Session, doc_id: int) -> Document:
        """重新处理文档的向量数据"""
        doc = await self.get_document_by_id(db, doc_id)
        if not doc:
            raise ValueError("Document not found")

        try:
            # 删除旧的向量数据
            if doc.vector_id:
                vector_ids = [int(vid) for vid in doc.vector_id.split(",")]  # 转换回整数
                self.vector_store.delete(expr=f"pk in {vector_ids}")

            # 重新分割文本
            texts = self.text_splitter.split_text(doc.content)

            # 为每个文本块添加元数据
            metadatas = [{"title": doc.title, "category": doc.category, "chunk_index": i} for i, _ in enumerate(texts)]

            # 重新生成向量并存储
            vector_ids = self.vector_store.add_texts(
                texts=texts,
                metadatas=metadatas
            )

            # 更新文档记录
            doc.vector_id = ','.join(map(str, vector_ids)) if vector_ids else None  # 转换为字符串
            db.commit()

            return doc
        except Exception as e:
            print(f"Error reprocessing document: {e}")
            raise e

    async def search_documents(self, query: str, top_k: int = 5) -> List[dict]:
        """搜索相关文档"""
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        return [
            {
                "content": doc.page_content,
                "score": score,
                "metadata": doc.metadata
            }
            for doc, score in results
        ]

    async def get_document_by_id(self, db: Session, doc_id: int) -> Optional[Document]:
        """根据ID获取文档"""
        return db.query(Document).filter(Document.id == doc_id).first()

    async def get_documents(
            self,
            db: Session,
            category: Optional[str] = None,
            page: int = 1,
            size: int = 10
    ) -> tuple[List[Document], int]:
        """获取文档列表
        
        Args:
            db: 数据库会话
            category: 可选的分类过滤
            page: 页码
            size: 每页数量
            
        Returns:
            tuple[List[Document], int]: 文档列表和总数
        """
        # 构建基础查询
        query = db.query(Document)
        if category:
            query = query.filter(Document.category == category)

        # 获取总数
        total = query.count()

        # 添加排序和分页
        documents = query.order_by(Document.created_at.desc()) \
            .offset((page - 1) * size) \
            .limit(size) \
            .all()

        return documents, total

    async def delete_document(self, db: Session, doc_id: int) -> bool:
        """删除文档及其向量数据"""
        doc = await self.get_document_by_id(db, doc_id)
        if not doc:
            return False

        try:
            # 删除向量数据
            if doc.vector_id:
                vector_ids = [int(vid) for vid in doc.vector_id.split(",")]  # 转换回整数
                print("Deleting vector IDs:", vector_ids)
                # 使用表达式删除
                expr = f'pk in {vector_ids}'
                self.vector_store.delete(expr=expr)

            # 删除文件
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)

            # 从数据库中删除记录
            db.delete(doc)
            db.commit()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            db.rollback()
            return False

    async def create_category(self, db: Session, name: str, description: str,
                              parent_id: Optional[int] = None) -> Category:
        """创建分类"""
        category = Category(
            name=name,
            description=description,
            parent_id=parent_id
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    async def get_category_tree(self, db: Session) -> List[Category]:
        """获取分类树"""
        return db.query(Category).filter(Category.parent_id.is_(None)).all()

    async def get_document_vectors(
            self,
            db: Session,
            doc_id: int,
            page: int = 1,
            size: int = 10
    ) -> tuple[List[dict], int]:
        """获取文档的向量数据列表
        
        Args:
            db: Session: 数据库会话
            doc_id: int: 文档ID
            page: int: 页码
            size: int: 每页数量
            
        Returns:
            tuple[List[dict], int]: 向量数据列表和总数
        """
        doc = await self.get_document_by_id(db, doc_id)
        if not doc or not doc.vector_id:
            return [], 0

        try:
            vector_ids = [int(vid) for vid in doc.vector_id.split(",")]  # 转换回整数

            # 计算总数
            total = len(vector_ids)

            # 计算分页
            start_idx = (page - 1) * size
            end_idx = min(start_idx + size, total)

            # 获取当前页的向量ID
            page_vector_ids = vector_ids[start_idx:end_idx]

            # 查询向量数据
            results = []
            if page_vector_ids:
                # 使用表达式构建查询
                expr = f"pk in {page_vector_ids}"

                # 使用similarity_search_with_score方法获取数据
                docs_and_scores = self.vector_store.similarity_search(
                    query="",  # 空查询，只使用过滤条件
                    k=len(page_vector_ids),  # 限制返回结果数量
                    expr=expr  # 使用主键过滤
                )

                for doc in docs_and_scores:
                    results.append({
                        "id": doc.metadata.get("pk", ""),
                        "text": doc.page_content,
                        "metadata": doc.metadata,
                        "chunk_index": doc.metadata.get("chunk_index"),
                    })

                # 按照原始顺序排序
                pk_order = {pk: idx for idx, pk in enumerate(page_vector_ids)}
                results.sort(key=lambda x: pk_order.get(x["id"], float('inf')))

            return results, total

        except Exception as e:
            print(f"Error getting document vectors: {e}")
            return [], 0

    async def update_document(
            self,
            db: Session,
            doc_id: int,
            doc_in: DocumentUpdate
    ) -> Optional[Document]:
        """更新文档信息
        
        Args:
            db: 数据库会话
            doc_id: 文档ID
            doc_in: 更新数据
            
        Returns:
            Optional[Document]: 更新后的文档
        """
        doc = await self.get_document_by_id(db, doc_id)
        if not doc:
            return None

        try:
            # 更新文档信息
            doc.title = doc_in.title
            doc.category = doc_in.category
            doc.updated_at = datetime.now()
            db.commit()
            db.refresh(doc)
            return doc

        except Exception as e:
            print(f"Error updating document: {e}")
            db.rollback()
            raise e
