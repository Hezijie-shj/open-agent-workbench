"""文档差异比对接口."""

from fastapi import APIRouter, HTTPException

from app.services.document_diff_service import document_diff_service

router = APIRouter()


@router.get("/history")
def list_history() -> dict:
    """获取文档差异比对历史."""
    return {"code": 0, "message": "success", "data": document_diff_service.list_history()}


@router.post("/history/demo")
def create_demo_task() -> dict:
    """创建本地文档差异比对样例."""
    return {"code": 0, "message": "success", "data": document_diff_service.create_demo_task()}


@router.post("/compare-documents")
def compare_documents() -> dict:
    """创建文档差异比对任务."""
    return {"code": 0, "message": "success", "data": document_diff_service.compare_documents()}


@router.get("/history/{task_id}")
def get_detail(task_id: str) -> dict:
    """获取文档差异比对详情."""
    detail = document_diff_service.get_detail(task_id)
    if not detail:
        raise HTTPException(status_code=404, detail="document diff task not found")
    return {"code": 0, "message": "success", "data": detail}


@router.get("/history/{task_id}/status")
def load_task_status(task_id: str) -> dict:
    """同步文档差异比对任务状态."""
    status = document_diff_service.load_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="document diff task not found")
    return {"code": 0, "message": "success", "data": status}


@router.get("/history/{task_id}/preview")
def preview(task_id: str) -> dict:
    """获取文档差异比对预览地址."""
    result = document_diff_service.preview(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="document diff task not found")
    return {"code": 0, "message": "success", "data": result}


@router.get("/history/{task_id}/local-line-diff")
def local_line_diff(task_id: str) -> dict:
    """获取本地行级 diff 流程演示结果."""
    result = document_diff_service.local_line_diff(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="document diff task not found")
    return {"code": 0, "message": "success", "data": result}
