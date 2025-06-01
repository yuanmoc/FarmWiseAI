from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.api_v1.deps import verify_and_refresh_token
from app.core.config import settings
from app.api.api_v1.api import api_router
from app.db.init_db import init_db
import os



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    print("正在初始化数据库...")
    init_db()
    print("数据库初始化完成！")

    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    yield
    # 关闭时执行
    print("应用正在关闭...")

app = FastAPI(
    title=settings.APP_NAME,
    description="智慧农业咨询系统API",
    version="1.0.0",
    lifespan=lifespan,
    dependencies=[Depends(verify_and_refresh_token)]
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 配置静态文件服务
# 获取当前项目根目录（假设是包含main.py的目录）
upload_dir = settings.UPLOAD_DIR
project_root = Path(__file__).parent.resolve()
upload_path = Path(upload_dir).resolve()
# 确保目录存在
os.makedirs(upload_path, exist_ok=True)

# 挂载路径
common_prefix = Path(os.path.commonpath([str(project_root), str(upload_path)]))
mount_dir = "/" + str(upload_path.relative_to(common_prefix))

app.mount(mount_dir, StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 包含 API 路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "欢迎使用智慧农业咨询系统API"}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        # reload=True,  # 启用热重载
        reload_dirs=["app"],  # 监视app目录的变化
        workers=1  # 限制为单个工作进程
    )
