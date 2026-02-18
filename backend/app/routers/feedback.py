from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import models
from .. import schemas, database
from ..routers import user as user_router

router = APIRouter(
    prefix="/feedbacks",
    tags=["feedbacks"]
)

# -------------------------------------------------------------------
# 依赖项
# -------------------------------------------------------------------

def get_db():
    return database.get_db()

# -------------------------------------------------------------------
# 路由接口
# -------------------------------------------------------------------

@router.post("/", response_model=schemas.FeedbackOut, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(user_router.get_current_user)
):
    """
    提交用户反馈 (普通用户权限)。
    会自动绑定当前登录用户的 ID。
    """
    new_feedback = models.Feedback(
        user_id=current_user.id,
        content=feedback.content,
        status="pending"
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    # 构造返回数据，包含 username
    return schemas.FeedbackOut(
        id=new_feedback.id,
        content=new_feedback.content,
        status=new_feedback.status,
        created_at=new_feedback.created_at,
        username=current_user.username
    )

@router.get("/admin/all", response_model=List[schemas.FeedbackOut]) # 修改路径为 /admin/all 以避免冲突，或使用 /admin 路由组
def get_all_feedbacks(
    db: Session = Depends(database.get_db),
    current_admin: models.User = Depends(user_router.get_current_admin)
):
    """
    获取所有反馈列表 (管理员权限)。
    按时间倒序排列。
    """
    feedbacks = db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).all()
    
    # 手动组装响应数据，因为 Pydantic 直接映射可能无法获取关联的 username
    result = []
    for fb in feedbacks:
        result.append(schemas.FeedbackOut(
            id=fb.id,
            content=fb.content,
            status=fb.status,
            created_at=fb.created_at,
            username=fb.user.username if fb.user else "Unknown"
        ))
    return result

@router.put("/admin/{feedback_id}/resolve", status_code=status.HTTP_200_OK)
def resolve_feedback(
    feedback_id: int,
    db: Session = Depends(database.get_db),
    current_admin: models.User = Depends(user_router.get_current_admin)
):
    """
    将指定反馈标记为已解决 (管理员权限)。
    """
    feedback_query = db.query(models.Feedback).filter(models.Feedback.id == feedback_id)
    feedback = feedback_query.first()

    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    feedback.status = "resolved"
    db.commit()
    
    return {"message": "Feedback resolved successfully"}
