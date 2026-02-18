from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import json

from ..database import get_db
from ..models import models
from ..routers.user import get_current_user
from .. import schemas

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

# 管理员权限依赖
def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

@router.get("/users", summary="获取所有用户列表")
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取所有用户信息 (仅管理员)
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    # 转换为 Schema (需注意 Schema 定义，避免返回密码)
    # 这里简单处理，手动构建返回
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "is_admin": u.is_admin,
            "is_active": u.is_active, # 返回封禁状态
            "created_at": u.created_at
        })
    return result

@router.put("/users/{user_id}/password", summary="管理员重置用户密码")
def reset_user_password(
    user_id: int,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    管理员强制重置用户密码 (默认为 123456)
    """
    from ..routers.user import get_password_hash
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
        
    user.password_hash = get_password_hash("123456")
    db.commit()
    return {"message": "密码已重置为 123456"}

@router.put("/users/{user_id}/status", summary="管理员修改用户状态")
def update_user_status(
    user_id: int,
    status_update: schemas.UserStatusUpdate,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    管理员封禁或解禁用户
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
        
    # 不允许禁用自己
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="不能禁用自己")
        
    user.is_active = status_update.is_active
    db.commit()
    
    status_text = "解禁" if user.is_active else "封禁"
    return {"message": f"用户已{status_text}"}

@router.get("/stats", summary="获取全站统计数据")
def get_global_stats(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取全站统计数据 (仅管理员)
    """
    total_users = db.query(func.count(models.User.id)).scalar()
    total_records = db.query(func.count(models.RecognitionHistory.id)).scalar()
    
    # 分类统计
    # 获取所有记录的 ai_analysis
    histories = db.query(models.RecognitionHistory).all()
    category_counts = {}
    
    for h in histories:
        try:
            if h.ai_analysis:
                analysis = json.loads(h.ai_analysis)
                category = analysis.get("category", "未知")
                category_counts[category] = category_counts.get(category, 0) + 1
        except:
             pass
             
    return {
        "total_users": total_users,
        "total_records": total_records,
        "category_distribution": category_counts
    }

@router.get("/records", summary="获取所有识别记录")
def get_all_records(
    skip: int = 0,
    limit: int = 50,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取所有识别记录 (按时间倒序)
    """
    histories = db.query(models.RecognitionHistory)\
        .order_by(models.RecognitionHistory.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
        
    result = []
    for h in histories:
        try:
            ai_analysis = json.loads(h.ai_analysis) if h.ai_analysis else {}
        except:
            ai_analysis = {}
            
        result.append({
            "id": h.id,
            "user_id": h.user_id,
            "username": h.user.username, # 关联查询
            "input_type": h.input_type,
            "input_content": h.input_content,
            "recognized_item": h.recognized_item,
            "ai_analysis": ai_analysis,
            "created_at": h.created_at
        })
        
    return result

@router.delete("/records/{history_id}", summary="管理员删除记录")
def admin_delete_history(
    history_id: int,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    管理员删除任意识别记录
    """
    history = db.query(models.RecognitionHistory).filter(models.RecognitionHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="记录不存在")
        
    db.delete(history)
    db.commit()
    return {"message": "删除成功"}

@router.get("/logs", summary="获取系统日志")
def get_system_logs(
    lines: int = 500,
    current_admin: models.User = Depends(get_current_admin)
):
    """
    获取系统后端日志 (仅管理员)
    """
    import os
    log_file = "app.log"
    
    if not os.path.exists(log_file):
        return {"logs": "日志文件不存在"}
        
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            # 读取所有行
            all_lines = f.readlines()
            # 取最后 N 行
            last_lines = all_lines[-lines:] if lines > 0 else all_lines
            return {"logs": "".join(last_lines)}
    except Exception as e:
        return {"logs": f"读取日志出错: {str(e)}"}
