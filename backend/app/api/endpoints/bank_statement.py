"""流水分析接口."""

from fastapi import APIRouter, HTTPException

from app.services.bank_statement_service import bank_statement_service

router = APIRouter()


@router.get("/projects")
def list_projects() -> dict:
    """获取流水分析项目列表.

    :return: 项目列表响应.
    :rtype: dict
    """
    return {"code": 0, "message": "success", "data": bank_statement_service.list_projects()}


@router.post("/projects/demo")
def create_demo_project() -> dict:
    """创建本地演示流水项目."""
    return {"code": 0, "message": "success", "data": bank_statement_service.create_demo_project()}


@router.post("/projects/upload-task")
def create_upload_task(file_name: str = "statement-demo.zip") -> dict:
    """创建文件上传、解压和解析队列任务."""
    return {"code": 0, "message": "success", "data": bank_statement_service.create_upload_task(file_name)}


@router.post("/projects/{project_id}/engineering-pipeline")
def run_engineering_pipeline(project_id: int, file_name: str = "statement-demo.zip") -> dict:
    """运行工程化流水解析全链路演示."""
    return {
        "code": 0,
        "message": "success",
        "data": bank_statement_service.run_engineering_pipeline(project_id, file_name),
    }


@router.get("/projects/{project_id}")
def get_project(project_id: int) -> dict:
    """获取流水项目详情.

    :param int project_id: 项目 ID.
    :return: 项目详情响应.
    :rtype: dict
    """
    project = bank_statement_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    return {"code": 0, "message": "success", "data": project}


@router.post("/projects/{project_id}/reviewed")
def mark_project_reviewed(project_id: int) -> dict:
    """标记流水项目复核完成."""
    project = bank_statement_service.mark_reviewed(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    return {"code": 0, "message": "success", "data": project}


@router.delete("/projects/{project_id}")
def delete_project(project_id: int) -> dict:
    """删除本地演示流水项目."""
    project = bank_statement_service.delete_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    return {"code": 0, "message": "success", "data": project}


@router.get("/projects/{project_id}/analysis-result")
def get_analysis_result(project_id: int, page: int = 1) -> dict:
    """获取指定页识别结果.

    :param int project_id: 项目 ID.
    :param int page: 页码.
    :return: 识别结果响应.
    :rtype: dict
    """
    return {"code": 0, "message": "success", "data": bank_statement_service.get_analysis_result(project_id, page)}


@router.get("/projects/{project_id}/full-pdf-recognition")
def recognize_full_pdf(project_id: int) -> dict:
    """获取完整 PDF 识别流程演示结果."""
    return {"code": 0, "message": "success", "data": bank_statement_service.recognize_full_pdf(project_id)}


@router.get("/projects/{project_id}/single-page-recognition")
def recognize_single_page(project_id: int, page: int = 1) -> dict:
    """获取单页识别流程演示结果."""
    return {"code": 0, "message": "success", "data": bank_statement_service.recognize_single_page(project_id, page)}


@router.get("/projects/{project_id}/sensitive-fallback")
def get_sensitive_fallback(project_id: int, page: int = 1) -> dict:
    """获取敏感词兜底流程演示结果."""
    return {"code": 0, "message": "success", "data": bank_statement_service.sensitive_fallback(project_id, page)}


@router.get("/projects/{project_id}/report")
def get_report(project_id: int) -> dict:
    """获取流水核查报告.

    :param int project_id: 项目 ID.
    :return: 报告响应.
    :rtype: dict
    """
    report = bank_statement_service.get_report(project_id)
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    return {"code": 0, "message": "success", "data": report}


@router.get("/projects/{project_id}/report/details")
def get_report_details(project_id: int, label: str = "all") -> dict:
    """获取报告抽屉明细."""
    return {"code": 0, "message": "success", "data": bank_statement_service.get_detail_rows(project_id, label)}


@router.get("/workflow-tasks")
def list_workflow_tasks() -> dict:
    """获取流水解析状态机任务列表."""
    return {"code": 0, "message": "success", "data": bank_statement_service.list_workflow_tasks()}


@router.get("/review-records")
def list_review_records(project_id: int | None = None) -> dict:
    """获取流水解析复核记录."""
    return {"code": 0, "message": "success", "data": bank_statement_service.list_review_records(project_id)}


@router.get("/audit-summary")
def get_audit_summary() -> dict:
    """获取流水解析审计日志、调用计数和队列状态."""
    return {"code": 0, "message": "success", "data": bank_statement_service.audit_summary()}
