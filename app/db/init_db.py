from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.models.knowledge import Document, Category
from app.services.auth import get_password_hash

def init_db() -> None:
    """初始化数据库"""
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}  # SQLite特定配置
    )
    
    # 创建会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    inspector = inspect(engine)

    try:
        # 按顺序创建表
        print("开始创建数据库表...")
        
        # 1. 创建用户表
        print("正在创建用户表...")
        if not inspector.has_table(User.__tablename__):
            User.__table__.create(bind=engine)
            print("用户表创建成功！")
        else:
            print("用户表已存在，跳过创建。")

        # 2. 创建分类表
        print("正在创建分类表...")
        if not inspector.has_table(Category.__tablename__):
            Category.__table__.create(bind=engine)
            print("分类表创建成功！")
        else:
            print("分类表已存在，跳过创建。")

        # 3. 创建文档表
        print("正在创建文档表...")
        if not inspector.has_table(Document.__tablename__):
            Document.__table__.create(bind=engine)
            print("文档表创建成功！")
        else:
            print("文档表已存在，跳过创建。")

        # 创建初始管理员账号
        print("正在检查管理员账号...")
        admin_email = "123@qq.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("admin123"),  # 默认密码
                full_name="系统管理员",
                is_active=True,
                user_type="admin",
                location="总部",
                main_crops="所有"
            )
            db.add(admin_user)
            db.commit()
            print(f"管理员账号创建成功！")
            print(f"邮箱: {admin_email}")
            print(f"密码: admin123")
        else:
            print("管理员账号已存在，跳过创建。")

        # 创建基础分类
        print("正在创建基础分类...")
        base_categories = [
            {"name": "种植技术", "description": "农作物种植相关的技术文档"},
            {"name": "病虫害防治", "description": "病虫害识别与防治方案"},
            {"name": "市场信息", "description": "农产品市场价格和趋势分析"},
            {"name": "政策法规", "description": "农业相关政策法规文件"},
            {"name": "科研成果", "description": "最新农业科研成果和技术创新"}
        ]
        
        for cat_data in base_categories:
            category = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not category:
                category = Category(**cat_data)
                db.add(category)
                print(f"创建分类：{cat_data['name']}")
        
        db.commit()
        print("基础分类创建完成！")

        print("数据库初始化完成！")

    except Exception as e:
        print(f"初始化过程中出错：{str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# if __name__ == "__main__":
#     print("开始初始化数据库...")
#     init_db()
#     print("初始化完成！")