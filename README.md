# 智慧农业咨询系统

## 项目设置

1. 安装依赖：

```bash
pip install -r requirements.txt

# 导入依赖
pip freeze | sed 's/@.*//' > requirements-clean.txt
# 删除依赖
pip uninstall -r requirements-clean.txt -y
```

2. 初始化数据库：

方法：启动应用时会自动初始化
```bash
python app/main.py
```

3. 前端项目启动
```bash
npm intall
npm run dev 
```

## 数据库结构

系统使用 SQLite 数据库，包含以下表：

1. users - 用户表
   - id: 主键
   - email: 邮箱（唯一）
   - hashed_password: 加密后的密码
   - full_name: 用户全名
   - is_active: 是否激活
   - user_type: 用户类型（农民、科研人员、推广人员）
   - location: 地理位置
   - main_crops: 主要种植作物

2. documents - 文档表
   - id: 主键
   - title: 文档标题
   - content: 文档内容
   - file_path: 文件路径
   - file_type: 文件类型
   - category: 分类
   - summary: 文档摘要
   - vector_id: 向量ID
   - tags: 文档标签

3. categories - 分类表
   - id: 主键
   - name: 分类名称
   - parent_id: 父分类ID
   - description: 分类描述

## API 文档

启动应用后，访问 http://localhost:8000/docs 查看完整的 API 文档。