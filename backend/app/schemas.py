from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# 定义用户角色枚举，与 models.py 保持一致
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

# -------------------------------------------------------------------
# 用户相关模型 (User)
# -------------------------------------------------------------------

# 用户基础模型
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")

# 用户创建模型 (注册请求体)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    role: UserRole = Field(default=UserRole.USER, description="用户角色")

# 用户登录模型 (登录请求体)
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

# 用户响应模型 (返回给前端的数据)
class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    # 避免返回 password_hash

    class Config:
        from_attributes = True # 允许从 ORM 模型创建

# 用户修改密码模型
class UserUpdatePassword(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")

# 用户状态修改模型
class UserStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="是否启用")

# 用户基本信息修改模型
class UserUpdateInfo(BaseModel):
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    # 可以添加其他允许修改的字段，如昵称等

# -------------------------------------------------------------------
# Token 相关模型
# -------------------------------------------------------------------

# Token 响应模型
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    is_admin: bool

# Token 数据模型 (用于解析 Token)
class TokenData(BaseModel):
    username: Optional[str] = None

# -------------------------------------------------------------------
# 用户反馈相关模型
# -------------------------------------------------------------------

# 反馈创建模型 (请求体)
class FeedbackCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="反馈内容")

# 反馈响应模型 (返回给前端)
class FeedbackOut(BaseModel):
    id: int
    content: str
    status: str
    created_at: datetime
    username: str = Field(..., description="提交反馈的用户名")

    class Config:
        from_attributes = True

# -------------------------------------------------------------------
# 本地分类词典相关模型
# -------------------------------------------------------------------

# 词典基础模型
class DictionaryBase(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=100, description="物品名称")
    category: str = Field(..., min_length=1, max_length=50, description="垃圾分类类别")
    description: Optional[str] = Field(None, description="补充说明")

# 词典创建模型 (新增请求体)
class DictionaryCreate(DictionaryBase):
    pass

# 词典更新模型 (修改请求体)
class DictionaryUpdate(BaseModel):
    item_name: Optional[str] = Field(None, min_length=1, max_length=100, description="物品名称")
    category: Optional[str] = Field(None, min_length=1, max_length=50, description="垃圾分类类别")
    description: Optional[str] = Field(None, description="补充说明")

# 词典响应模型 (返回给前端)
class DictionaryOut(DictionaryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# -------------------------------------------------------------------
# 环保知识文章相关模型
# -------------------------------------------------------------------

# 文章基础模型
class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="文章标题")
    content: str = Field(..., description="文章内容")
    cover_image: Optional[str] = Field(None, description="封面图片URL")
    is_published: Optional[bool] = Field(True, description="是否发布")

# 文章创建模型 (新增请求体)
class ArticleCreate(ArticleBase):
    author: Optional[str] = Field("管理员", description="发布者姓名")

# 文章更新模型 (修改请求体)
class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文章标题")
    content: Optional[str] = Field(None, description="文章内容")
    cover_image: Optional[str] = Field(None, description="封面图片URL")
    is_published: Optional[bool] = Field(None, description="是否发布")
    author: Optional[str] = Field(None, description="发布者姓名")

# 文章响应模型 (返回给前端)
class ArticleOut(ArticleBase):
    id: int
    author: str
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
