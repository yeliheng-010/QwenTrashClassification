from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import models
from .. import schemas
from .user import get_current_admin # 复用管理员权限依赖

router = APIRouter(
    prefix="/articles",
    tags=["articles"],
    responses={404: {"description": "Not found"}},
)

# -------------------------------------------------------------------
# 公开接口
# -------------------------------------------------------------------

@router.get("", response_model=List[schemas.ArticleOut], summary="获取文章列表")
def get_articles(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """
    获取文章列表接口 (公开)：
    - 按创建时间倒序排列
    - 支持分页 (skip, limit)
    - 仅返回已发布的文章
    """
    articles = db.query(models.Article).filter(
        models.Article.is_published == True
    ).order_by(models.Article.created_at.desc()).offset(skip).limit(limit).all()
    return articles

@router.get("/{id}", response_model=schemas.ArticleOut, summary="获取文章详情")
def get_article(id: int, db: Session = Depends(get_db)):
    """
    获取文章详情接口 (公开)：
    - 根据 ID 获取文章
    - 增加浏览量
    """
    article = db.query(models.Article).filter(models.Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 增加浏览量
    article.view_count += 1
    db.commit()
    db.refresh(article)
    
    return article

# -------------------------------------------------------------------
# 管理员接口 (需要管理员权限)
# -------------------------------------------------------------------

@router.post("/admin", response_model=schemas.ArticleOut, status_code=status.HTTP_201_CREATED, summary="发布新文章 (管理员)")
def create_article(
    article: schemas.ArticleCreate, 
    db: Session = Depends(get_db), 
    current_admin: models.User = Depends(get_current_admin)
):
    """
    发布新文章接口 (管理员)：
    - 需要管理员权限
    """
    db_article = models.Article(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

@router.put("/admin/{id}", response_model=schemas.ArticleOut, summary="修改文章 (管理员)")
def update_article(
    id: int, 
    article_update: schemas.ArticleUpdate, 
    db: Session = Depends(get_db), 
    current_admin: models.User = Depends(get_current_admin)
):
    """
    修改文章接口 (管理员)：
    - 需要管理员权限
    """
    db_article = db.query(models.Article).filter(models.Article.id == id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    update_data = article_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_article, key, value)
    
    db.commit()
    db.refresh(db_article)
    return db_article

@router.delete("/admin/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除文章 (管理员)")
def delete_article(
    id: int, 
    db: Session = Depends(get_db), 
    current_admin: models.User = Depends(get_current_admin)
):
    """
    删除文章接口 (管理员)：
    - 需要管理员权限
    """
    db_article = db.query(models.Article).filter(models.Article.id == id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    db.delete(db_article)
    db.commit()
    return None
