from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import models
from .. import schemas
from .user import get_current_admin # 复用管理员权限依赖

router = APIRouter(
    prefix="/dictionary",
    tags=["dictionary"],
    responses={404: {"description": "Not found"}},
)

# -------------------------------------------------------------------
# 公开接口
# -------------------------------------------------------------------

@router.get("/search", response_model=List[schemas.DictionaryOut], summary="搜索垃圾分类词典")
def search_dictionary(keyword: str, db: Session = Depends(get_db)):
    """
    搜索垃圾分类词典接口 (公开)：
    - 接收查询参数 keyword
    - 使用 fuzzy matching (ilike) 匹配 item_name
    - 返回匹配的词条列表
    """
    if not keyword:
        return []
    
    # 使用 ILIKE 进行不区分大小写的模糊匹配
    results = db.query(models.GarbageDictionary).filter(
        models.GarbageDictionary.item_name.ilike(f"%{keyword}%")
    ).all()
    
    return results

# -------------------------------------------------------------------
# 管理员接口 (需要管理员权限)
# -------------------------------------------------------------------

# 1. 获取全量词库列表
@router.get("/admin", response_model=List[schemas.DictionaryOut], summary="获取全量词库列表 (管理员)")
def get_all_dictionary_items(
    db: Session = Depends(get_db), 
    current_admin: models.User = Depends(get_current_admin)
):
    """
    获取全量词库列表接口 (管理员)：
    - 需要管理员权限
    - 返回所有词条
    """
    items = db.query(models.GarbageDictionary).all()
    return items

# 2. 新增词条
@router.post("/admin", response_model=schemas.DictionaryOut, status_code=status.HTTP_201_CREATED, summary="新增词条 (管理员)")
def create_dictionary_item(
    item: schemas.DictionaryCreate, 
    db: Session = Depends(get_db), 
    current_admin: models.User = Depends(get_current_admin)
):
    """
    新增词条接口 (管理员)：
    - 需要管理员权限
    - 创建新的垃圾分类词条
    """
    # 检查是否已存在同名物品 (可选，防止重复)
    existing_item = db.query(models.GarbageDictionary).filter(
        models.GarbageDictionary.item_name == item.item_name
    ).first()
    
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"物品 '{item.item_name}' 已存在"
        )

    # 创建新词条
    db_item = models.GarbageDictionary(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item

# 3. 修改词条
@router.put("/admin/{id}", response_model=schemas.DictionaryOut, summary="修改词条 (管理员)")
def update_dictionary_item(
    id: int, 
    item_update: schemas.DictionaryUpdate, 
    db: Session = Depends(get_db), 
    current_admin: models.User = Depends(get_current_admin)
):
    """
    修改词条接口 (管理员)：
    - 需要管理员权限
    - 根据 ID 修改指定词条
    """
    db_item = db.query(models.GarbageDictionary).filter(models.GarbageDictionary.id == id).first()
    
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="词条不存在"
        )
    
    # 更新字段
    update_data = item_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    
    return db_item

# 4. 删除词条
@router.delete("/admin/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除词条 (管理员)")
def delete_dictionary_item(
    id: int, 
    db: Session = Depends(get_db), 
    current_admin: models.User = Depends(get_current_admin)
):
    """
    删除词条接口 (管理员)：
    - 需要管理员权限
    - 根据 ID 删除指定词条
    """
    db_item = db.query(models.GarbageDictionary).filter(models.GarbageDictionary.id == id).first()
    
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="词条不存在"
        )
    
    db.delete(db_item)
    db.commit()
    
    return None
