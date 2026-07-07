"""规章制度比对接口."""

from fastapi import APIRouter

from app.services.regulations_service import regulations_service

router = APIRouter()


@router.get("/tasks")
def list_tasks() -> dict:
    """获取规章制度比对任务列表.

    :return: 任务列表响应.
    :rtype: dict
    """
    return {"code": 0, "message": "success", "data": regulations_service.list_tasks()}


@router.post("/tasks/demo")
def create_demo_task() -> dict:
    """创建本地演示制度比对任务."""
    return {"code": 0, "message": "success", "data": regulations_service.create_demo_task()}


@router.post("/tasks")
def create_task() -> dict:
    """创建制度比对任务."""
    return {"code": 0, "message": "success", "data": regulations_service.create_demo_task()}


@router.post("/tasks/upload-demo")
def upload_demo_task() -> dict:
    """上传示例文档并创建本地演示任务."""
    return {"code": 0, "message": "success", "data": regulations_service.create_demo_task(uploaded=True)}


@router.post("/tasks/{task_id}/upload-demo")
def upload_demo_file(task_id: int) -> dict:
    """为指定制度任务上传示例文档."""
    return {"code": 0, "message": "success", "data": regulations_service.run_engineering_pipeline(task_id)}


@router.post("/tasks/upload-task")
def create_upload_task(file_name: str = "origin-policy-demo.pdf") -> dict:
    """创建制度文档上传和比对队列任务."""
    return {"code": 0, "message": "success", "data": regulations_service.create_upload_task(file_name)}


@router.get("/tasks/{task_id}")
def get_task(task_id: int) -> dict:
    """获取规章制度比对任务详情.

    :param int task_id: 任务 ID.
    :return: 任务详情响应.
    :rtype: dict
    """
    return {"code": 0, "message": "success", "data": regulations_service.get_task(task_id)}


@router.get("/tasks/{task_id}/matches")
def get_task_matches(task_id: int) -> dict:
    """获取制度比对文本匹配演示结果."""
    return {"code": 0, "message": "success", "data": regulations_service.match_text(task_id)}


@router.get("/tasks/{task_id}/workflow")
def get_compare_workflow(task_id: int) -> dict:
    """获取完整制度文档比对流程演示结果."""
    return {"code": 0, "message": "success", "data": regulations_service.compare_documents_workflow(task_id)}


@router.post("/tasks/{task_id}/engineering-pipeline")
def run_engineering_pipeline(task_id: int, file_name: str = "origin-policy-demo.pdf") -> dict:
    """运行工程化制度文档比对全链路演示."""
    return {"code": 0, "message": "success", "data": regulations_service.run_engineering_pipeline(task_id, file_name)}


@router.get("/tasks/{task_id}/single-document-compare")
def get_single_document_compare(task_id: int, compare_file: str = "rule-library-demo.pdf") -> dict:
    """获取单文档比对流程演示结果."""
    return {
        "code": 0,
        "message": "success",
        "data": regulations_service.compare_single_document(task_id, compare_file),
    }


@router.get("/tasks/{task_id}/text-match-fallback")
def get_text_match_fallback(task_id: int) -> dict:
    """获取文本定位和截断兜底流程演示结果."""
    return {"code": 0, "message": "success", "data": regulations_service.text_match_fallback(task_id)}


@router.get("/workflow-tasks")
def list_workflow_tasks() -> dict:
    """获取制度比对状态机任务列表."""
    return {"code": 0, "message": "success", "data": regulations_service.list_workflow_tasks()}


@router.get("/review-records")
def list_review_records(task_id: int | None = None) -> dict:
    """获取制度比对复核记录."""
    return {"code": 0, "message": "success", "data": regulations_service.list_review_records(task_id)}


@router.get("/audit-summary")
def get_audit_summary() -> dict:
    """获取制度比对审计日志、调用计数和队列状态."""
    return {"code": 0, "message": "success", "data": regulations_service.audit_summary()}
