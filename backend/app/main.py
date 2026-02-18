from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from .database import engine
from .models import models
from .routers import user, recognition, admin, feedback, dictionary, article

# 创建数据库表
# 注意：在生产环境中通常使用 Alembic 进行迁移，这里为了简化直接创建
models.Base.metadata.create_all(bind=engine)

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("应用正在启动...")
    logger.info("应用正在启动...")
    yield
    # 关闭时执行
    print("应用正在关闭...")
    logger.info("应用正在关闭...")

# 配置日志
import logging
import sys

# 创建 logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# 设置格式
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加处理器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 初始化 FastAPI 应用
app = FastAPI(
    title="垃圾分类系统后端 API",
    description="基于 Qwen 大模型的垃圾分类系统后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS (跨域资源共享)
# 允许前端 (通常是 localhost:5173 或其他端口) 访问后端接口
origins = [
    "http://localhost",
    "http://localhost:5173", # Vite 默认端口
    "http://127.0.0.1:5173",
    "*", # 允许所有来源 (开发阶段方便调试，生产环境建议限制)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # 允许所有 HTTP 方法 (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # 允许所有 HTTP 头
)

# 注册路由
app.include_router(user.router)
app.include_router(recognition.router)
app.include_router(admin.router)
app.include_router(feedback.router)
app.include_router(dictionary.router)
app.include_router(article.router)

# 根路径测试
@app.get("/", tags=["root"])
async def root():
    return {"message": "欢迎使用垃圾分类系统后端 API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
