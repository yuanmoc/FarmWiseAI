from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "智慧农业咨询系统"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///app.db"
    SQL_ECHO: bool = True  # 是否打印SQL语句
    SQL_LOG_LEVEL: str = "ERROR"  # SQL日志级别：DEBUG, INFO, WARNING, ERROR
    
    # Milvus配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_URI: str = "./milvus.db"
    MILVUS_COLLECTION: str = "agricultural_knowledge"
    

    # Xinference 配置
    OPENAI_BASE_URL: str = "http://localhost:9997/v1"
    OPENAI_MODEL: str = "qwen3"  # 或其他您想使用的模型
    OPENAI_EMBEDDINGS: str = "jina-embeddings-v3"
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 文件上传配置
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        case_sensitive = True

settings = Settings() 