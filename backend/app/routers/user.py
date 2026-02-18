"""
用户认证与管理路由模块

本模块负责：
1. 用户注册、登录（JWT 令牌签发）
2. 获取/修改当前用户信息、修改密码
3. 提供 get_current_user / get_current_admin 依赖注入（供其他路由模块使用）

安全说明：
- JWT 密钥 (SECRET_KEY) 从 .env 环境变量中读取，避免硬编码
- 密码使用 bcrypt 算法单向哈希存储，数据库中不保存明文密码
- 所有敏感配置通过 python-dotenv 加载，确保代码仓库中不含任何密钥
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from ..database import get_db
from ..models import models
from .. import schemas

# ============================================
# 环境变量加载与安全配置
# ============================================

# 加载 .env 文件中的环境变量
# 这确保即使本模块被独立导入，环境变量也能正确加载
load_dotenv()

# 从环境变量中读取 JWT 相关配置
# SECRET_KEY: JWT 签名密钥，用于令牌的签发与验证，必须保密
# ALGORITHM: JWT 加密算法，默认使用 HS256（HMAC-SHA256）
# ACCESS_TOKEN_EXPIRE_MINUTES: 令牌过期时间（分钟），默认 30 分钟
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")  # 生产环境务必在 .env 中设置强密钥
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# 密码哈希上下文配置
# 使用 bcrypt 算法对用户密码进行单向哈希加密
# deprecated="auto" 表示自动处理旧算法的迁移
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码承载令牌方案
# tokenUrl 指定获取令牌的接口地址，供 Swagger 文档自动生成登录表单
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# 创建用户路由实例
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# ============================================
# 辅助函数：密码与令牌处理
# ============================================


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配。

    :param plain_password: 用户输入的明文密码
    :param hashed_password: 数据库中存储的哈希密码
    :return: 密码匹配返回 True，否则返回 False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    将明文密码转换为 bcrypt 哈希值。

    :param password: 明文密码
    :return: 哈希后的密码字符串
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    创建 JWT 访问令牌。

    :param data: 需要编码到令牌中的数据（如用户名、角色等）
    :param expires_delta: 令牌过期时间间隔，如果不指定则默认 15 分钟
    :return: 编码后的 JWT 字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    # 将过期时间写入令牌的 payload
    to_encode.update({"exp": expire})
    # 使用环境变量中的 SECRET_KEY 和 ALGORITHM 对令牌进行签名
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ============================================
# 依赖注入函数：获取当前用户/管理员
# ============================================


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    """
    获取当前登录用户的依赖注入函数。

    从请求头的 Authorization 字段中提取 Bearer Token，
    解码 JWT 令牌并从数据库中查找对应用户。

    :param token: 从请求头自动提取的 JWT 令牌
    :param db: 数据库会话
    :return: 当前登录的用户对象
    :raises HTTPException: 令牌无效、用户不存在或账号被封禁时抛出
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 使用 SECRET_KEY 和 ALGORITHM 解码 JWT 令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # 根据令牌中的用户名查询数据库
    user = (
        db.query(models.User)
        .filter(models.User.username == token_data.username)
        .first()
    )
    if user is None:
        raise credentials_exception

    # 检查账号是否被管理员封禁
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已被封禁"
        )

    return user


async def get_current_admin(
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    """
    获取当前管理员用户的依赖注入函数。

    在 get_current_user 的基础上进一步检查用户是否具有管理员权限。

    :param current_user: 当前登录用户（由 get_current_user 注入）
    :return: 具有管理员权限的用户对象
    :raises HTTPException: 权限不足时抛出 403 错误
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="权限不足"
        )
    return current_user


# ============================================
# API 路由：用户注册与登录
# ============================================


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口：
    1. 检查用户名是否已存在
    2. 检查邮箱是否已存在（如果提供了邮箱）
    3. 对密码进行 bcrypt 哈希加密
    4. 创建新用户并存入数据库
    """
    # 检查用户名是否已被注册
    db_user = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已被注册")

    # 检查邮箱是否已被注册（邮箱为可选字段）
    if user.email:
        db_user_email = (
            db.query(models.User).filter(models.User.email == user.email).first()
        )
        if db_user_email:
            raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 对密码进行哈希加密后创建新用户对象
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        is_admin=(user.role == schemas.UserRole.ADMIN),
    )

    # 保存到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=schemas.Token, summary="用户登录")
def login_for_access_token(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口：
    1. 根据用户名在数据库中查找用户
    2. 验证密码是否正确
    3. 生成并返回 JWT 访问令牌
    """
    # 根据用户名查找用户
    user = (
        db.query(models.User)
        .filter(models.User.username == user_login.username)
        .first()
    )

    # 验证用户是否存在以及密码是否正确
    if not user or not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成 JWT 访问令牌，将用户名、角色、管理员标志编码到令牌中
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
            "is_admin": user.is_admin,
        },
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "is_admin": user.is_admin,
    }


# ============================================
# API 路由：用户信息管理
# ============================================


@router.get("/me", response_model=schemas.UserResponse, summary="获取当前用户信息")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    获取当前登录用户的详细信息
    """
    return current_user


@router.put("/me/info", response_model=schemas.UserResponse, summary="修改个人信息")
def update_user_info(
    user_input: schemas.UserUpdateInfo,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    修改个人基本信息（如邮箱）
    """
    if user_input.email is not None:
        # 检查新邮箱是否已被其他用户使用
        if user_input.email != current_user.email:
            existing_user = (
                db.query(models.User)
                .filter(models.User.email == user_input.email)
                .first()
            )
            if existing_user:
                raise HTTPException(status_code=400, detail="该邮箱已被注册")
            current_user.email = user_input.email

    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/password", summary="修改密码")
def update_password(
    user_input: schemas.UserUpdatePassword,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    用户修改登录密码
    """
    # 验证旧密码是否正确
    if not verify_password(user_input.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码错误")

    # 将新密码哈希后更新到数据库
    current_user.password_hash = get_password_hash(user_input.new_password)
    db.commit()
    return {"message": "密码修改成功"}
