from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

# 创建基类
Base = declarative_base()

# 定义用户角色枚举
class UserRole(str, enum.Enum):
    ADMIN = "admin"  # 系统管理员
    USER = "user"    # 普通用户

# 1. 用户表 (Users)
class User(Base):
    """
    用户表：存储系统所有用户的信息，包括管理员和普通用户。
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID，主键")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名，唯一")
    password_hash = Column(String(255), nullable=False, comment="加密后的密码哈希值")
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False, comment="用户角色：admin-管理员, user-普通用户")
    is_admin = Column(Boolean, default=False, comment="是否为管理员")
    is_active = Column(Boolean, default=True, comment="是否启用")
    email = Column(String(100), unique=True, nullable=True, comment="邮箱地址（可选）")
    created_at = Column(DateTime, default=datetime.now, comment="注册时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    histories = relationship("RecognitionHistory", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")

# 2. 垃圾分类类别表 (GarbageCategories)
class GarbageCategory(Base):
    """
    垃圾分类类别表：存储四大类垃圾的标准定义（如湿垃圾、干垃圾等）。
    """
    __tablename__ = "garbage_categories"

    id = Column(Integer, primary_key=True, index=True, comment="分类ID，主键")
    name = Column(String(50), unique=True, nullable=False, comment="分类名称（如：可回收物、有害垃圾）")
    description = Column(Text, nullable=True, comment="分类描述/定义")
    guide = Column(Text, nullable=True, comment="投放指南/处理要求")
    icon_url = Column(String(255), nullable=True, comment="分类图标URL")

    # 关联关系
    items = relationship("GarbageItem", back_populates="category")

# 3. 常见垃圾物品表 (GarbageItems)
class GarbageItem(Base):
    """
    常见垃圾物品表：用于本地快速检索，存储常见物品及其所属分类。
    """
    __tablename__ = "garbage_items"

    id = Column(Integer, primary_key=True, index=True, comment="物品ID，主键")
    name = Column(String(100), index=True, nullable=False, comment="物品名称")
    category_id = Column(Integer, ForeignKey("garbage_categories.id"), nullable=False, comment="所属分类ID")
    search_count = Column(Integer, default=0, comment="被搜索次数，用于热词统计")

    # 关联关系
    category = relationship("GarbageCategory", back_populates="items")

# 4. 识别历史记录表 (RecognitionHistory)
class RecognitionHistory(Base):
    """
    识别历史记录表：记录用户上传图片或文本进行AI识别的历史。
    """
    __tablename__ = "recognition_histories"

    id = Column(Integer, primary_key=True, index=True, comment="记录ID，主键")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    input_type = Column(String(20), nullable=False, comment="输入类型：image-图片, text-文本")
    input_content = Column(Text, nullable=False, comment="输入内容：图片URL或文本内容")
    recognized_item = Column(String(100), nullable=True, comment="AI识别出的物品名称")
    ai_analysis = Column(Text, nullable=True, comment="AI返回的完整分析结果（JSON格式或文本）")
    created_at = Column(DateTime, default=datetime.now, comment="识别时间")
    
    # 关联关系
    user = relationship("User", back_populates="histories")
    # feedback = relationship("Feedback", uselist=False, back_populates="history") # 已移除关联

# 5. 环保知识文章表 (Articles)
class Article(Base):
    """
    环保知识文章表：存储科普文章、政策解读等资讯。
    """
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True, comment="文章ID，主键")
    title = Column(String(200), nullable=False, comment="文章标题")
    content = Column(Text, nullable=False, comment="文章内容（支持Markdown或HTML）")
    author = Column(String(50), default="管理员", comment="发布者姓名")
    cover_image = Column(String(255), nullable=True, comment="封面图片URL")
    view_count = Column(Integer, default=0, comment="浏览量")
    is_published = Column(Boolean, default=True, comment="是否发布")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

# 6. 用户反馈表 (Feedback)
class Feedback(Base):
    """
    用户反馈表：收集用户对识别结果的纠错或系统Bug反馈。
    """
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True, comment="反馈ID，主键")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    content = Column(Text, nullable=False, comment="反馈详情描述")
    status = Column(String(20), default="pending", comment="处理状态：pending-待处理, resolved-已解决")
    created_at = Column(DateTime, default=datetime.now, comment="提交时间")

    # 关联关系
    user = relationship("User", back_populates="feedbacks")

# 7. 本地垃圾分类词典表 (GarbageDictionary)
class GarbageDictionary(Base):
    """
    本地垃圾分类词典表：存储垃圾物品及其分类信息，用于本地检索和管理。
    """
    __tablename__ = "garbage_dictionary"

    id = Column(Integer, primary_key=True, index=True, comment="词条ID，主键")
    item_name = Column(String(100), index=True, nullable=False, comment="物品名称（索引，用于加速模糊查询）")
    category = Column(String(50), nullable=False, comment="垃圾分类（如：可回收物、干垃圾、湿垃圾、有害垃圾）")
    description = Column(Text, nullable=True, comment="补充说明/投放建议")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
