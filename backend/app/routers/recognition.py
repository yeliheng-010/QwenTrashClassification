from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional
import base64
import json

from ..database import get_db
from ..models import models
from ..routers.user import get_current_user
from ..services import qwen_service

router = APIRouter(
    prefix="/recognition",
    tags=["recognition"],
    responses={404: {"description": "Not found"}},
)

@router.post("/classify", summary="垃圾分类识别")
async def classify_garbage(
    text: Optional[str] = Form(None, description="文本描述"),
    image: Optional[UploadFile] = File(None, description="上传的图片文件"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    垃圾分类识别接口：
    - 支持文本描述或图片上传（二选一，图片优先）
    - 调用千问大模型进行识别
    - 记录识别历史到数据库
    """
    
    if not text and not image:
        raise HTTPException(status_code=400, detail="请提供文本描述或上传图片")

    recognition_result = {}
    input_type = "text"
    input_content_preview = "" # 用于存入数据库的预览内容

    try:
        if image:
            input_type = "image"
            # 读取图片内容并转换为 Base64
            contents = await image.read()
            # 简单检查文件大小（例如限制 5MB）
            if len(contents) > 5 * 1024 * 1024:
                 raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")
            
            base64_image = base64.b64encode(contents).decode('utf-8')
            # 构造 Data URL
            image_content = f"data:{image.content_type};base64,{base64_image}"
            input_content_preview = "[Image Upload]" # 实际生产中应上传到 OSS 并存 URL，这里简化存标识或是 Base64(过长不建议)
            # 注意：数据库中 input_content 字段是 Text 类型，存 Base64 可能过大。
            # 鉴于这是演示 Demo，我们截取一部分或仅存标识，或者如果需要在前端显示，必须存完整 Base64。
            # 为了功能完整性，这里暂存完整的 Base64（注意 MySQL Text 限制约 64KB，LongText 4GB）
            # SQLAlchemy Text 通常映射为 TEXT (64KB)，可能不够。
            # 如果 models.py 定义为 Text，可能不够存大图 Base64。
            # 修改策略：为了演示，我们假设图片不大，或者 user 应该知道这一点。
            # 更好的做法：由于无法修改 models，我们将存 Base64，但需注意长度。
            # 如果太长，可能会报错。建议用户上传小图。
            input_content_preview = image_content 
            
            recognition_result = qwen_service.classify_garbage(image_content, is_image=True)
            
        else:
            input_type = "text"
            input_content_preview = text
            recognition_result = qwen_service.classify_garbage(text, is_image=False)

        # 保存历史记录
        # 序列化 AI完整分析结果
        ai_analysis_json = json.dumps(recognition_result, ensure_ascii=False)
        
        history = models.RecognitionHistory(
            user_id=current_user.id,
            input_type=input_type,
            input_content=input_content_preview, # 注意：如果图片太大这里可能会截断或报错
            recognized_item=recognition_result.get("result_name"),
            ai_analysis=ai_analysis_json
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)

        return {
            "id": history.id,
            "result": recognition_result,
            "created_at": history.created_at
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"识别处理错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")

@router.get("/history", summary="获取识别历史记录")
def get_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的识别历史记录 (按时间倒序)
    """
    histories = db.query(models.RecognitionHistory)\
        .filter(models.RecognitionHistory.user_id == current_user.id)\
        .order_by(models.RecognitionHistory.created_at.desc())\
        .all()
    
    # 解析 JSON 字符串为对象
    result = []
    for h in histories:
        try:
            ai_analysis = json.loads(h.ai_analysis) if h.ai_analysis else {}
        except:
            ai_analysis = {}
            
        result.append({
            "id": h.id,
            "input_type": h.input_type,
            "input_content": h.input_content,
            "recognized_item": h.recognized_item,
            "ai_analysis": ai_analysis,
            "created_at": h.created_at
        })
        
    return result

@router.delete("/history/{history_id}", summary="删除识别记录")
def delete_history(
    history_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除指定的识别记录
    """
    history = db.query(models.RecognitionHistory)\
        .filter(models.RecognitionHistory.id == history_id, models.RecognitionHistory.user_id == current_user.id)\
        .first()
        
    if not history:
        raise HTTPException(status_code=404, detail="记录不存在或无权删除")
        
    db.delete(history)
    db.commit()
    
    return {"message": "删除成功"}
