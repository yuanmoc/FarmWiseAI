from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import logging
import time
from app.core.config import settings

# 配置 SQLAlchemy 日志
logging.basicConfig()
logger = logging.getLogger("sqlalchemy.engine")

# 根据配置设置日志级别
log_level = getattr(logging, settings.SQL_LOG_LEVEL.upper(), logging.INFO)
logger.setLevel(log_level)

Base = declarative_base()

# 创建引擎时启用回显
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.SQL_ECHO  # 使用配置中的设置
)


# 添加查询时间统计
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if settings.SQL_ECHO:  # 只在启用日志时记录时间
        conn.info.setdefault('query_start_time', []).append(time.time())
        # 打印 SQL 语句和参数
        logger.info(f"执行 SQL: {statement}")
        if parameters:
            logger.info(f"参数: {parameters}")


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if settings.SQL_ECHO and conn.info.get('query_start_time'):
        total = time.time() - conn.info['query_start_time'].pop()
        # 打印执行时间
        logger.info(f"SQL执行时间: {total:.3f}s")
        logger.info("-" * 50)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 