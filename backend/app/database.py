"""
数据库连接与会话管理模块

本模块负责：
1. 从 .env 文件中加载数据库连接配置（DATABASE_URL）
2. 创建 SQLAlchemy 数据库引擎
3. 提供数据库会话（Session）的依赖注入函数

安全说明：
- 数据库连接字符串包含用户名和密码，属于敏感信息
- 通过 python-dotenv 从 .env 文件读取，避免在代码中硬编码
- .env 文件已通过 .gitignore 排除，不会被提交到 Git 仓库
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
# load_dotenv() 会自动从当前工作目录或其父目录中查找 .env 文件
load_dotenv()

# 从环境变量中读取数据库连接 URL
# 格式示例: mysql+pymysql://用户名:密码@主机:端口/数据库名
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 安全校验：如果未配置数据库 URL，则直接抛出异常，防止应用以错误状态启动
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("环境变量 DATABASE_URL 未设置！请检查 backend/.env 文件是否存在并正确配置。")

# 创建数据库引擎
# pool_pre_ping=True: 每次从连接池取出连接前先 ping 一下，检测连接是否断开并自动重连
# pool_recycle=3600: 每隔 3600 秒（1 小时）回收连接，防止 MySQL 的 wait_timeout 导致连接失效
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 创建 SessionLocal 类（数据库会话工厂）
# autocommit=False: 禁止自动提交事务，需要手动调用 session.commit()
# autoflush=False: 禁止自动刷新，避免意外的数据库写入
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    获取数据库会话的依赖项函数（FastAPI 依赖注入）。

    使用方法：在路由函数参数中添加 db: Session = Depends(get_db)
    每个请求会创建一个独立的数据库会话，请求结束后自动关闭，
    确保数据库连接不会泄漏。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
