"""Local document-diff workflow for the public demo boundary."""

from app.platform.audit import audit_ledger
from app.platform.context import demo_context
from app.platform.file_pipeline import file_pipeline
from app.platform.model_gateway import model_gateway
from app.platform.parsers import structured_parser
from app.platform.queue import task_queue
from app.platform.reporting import report_builder
from app.platform.repository import WorkflowTask, repository

DOCUMENT_DIFF_HISTORY = [
    {
        "id": 1,
        "task_id": "demo-diff-001",
        "title": "合同条款差异比对",
        "status": "completed",
        "created_at": "2026-07-07 11:20:00",
        "success_count": 2,
        "fail_count": 0,
    },
    {
        "id": 2,
        "task_id": "demo-diff-002",
        "title": "补充协议版本比对",
        "status": "processing",
        "created_at": "2026-07-06 14:10:00",
        "success_count": 1,
        "fail_count": 0,
    },
]


class DocumentDiffAgent:
    """Document diff workflow without an external comparator SDK dependency."""

    def list_history(self) -> dict:
        self._advance_processing_tasks()
        return {"items": DOCUMENT_DIFF_HISTORY, "page": 1, "size": 10, "total": len(DOCUMENT_DIFF_HISTORY)}

    def create_demo_task(self) -> dict:
        next_id = max((item["id"] for item in DOCUMENT_DIFF_HISTORY), default=0) + 1
        task = {
            "id": next_id,
            "task_id": f"demo-diff-{next_id:03d}",
            "title": f"本地文档比对 {next_id}",
            "status": "completed",
            "created_at": "2026-07-08 10:00:00",
            "success_count": 2,
            "fail_count": 0,
        }
        DOCUMENT_DIFF_HISTORY.insert(0, task)
        return self.get_detail(task["task_id"])

    def create_upload_task(self, file_names: list[str] | None = None) -> dict:
        """Create a document-diff upload task."""

        context = demo_context()
        file_names = file_names or ["standard-contract-demo.docx", "contract-v1-demo.docx", "contract-v2-demo.docx"]
        uploads = [file_pipeline.upload_demo_file(file_name, "document_diff") for file_name in file_names]
        detail = self.create_demo_task()
        queue_job = task_queue.enqueue(
            "document_diff",
            "compare_documents",
            task_id=detail["task_id"],
            files=file_names,
        )
        saved = repository.save_task(
            WorkflowTask(
                task_id=detail["task_id"],
                module="document_diff",
                status="queued",
                title=detail["title"],
                tenant_id=context.tenant_id,
                operator=context.operator,
                current_step="uploaded",
                progress=15,
                payload={"uploads": uploads, "queue_job": queue_job},
            )
        )
        audit_ledger.record(
            "document_diff",
            "upload_documents",
            context.tenant_id,
            context.operator,
            file_count=len(file_names),
            task_id=detail["task_id"],
        )
        return saved

    def compare_documents(self) -> dict:
        next_id = max((item["id"] for item in DOCUMENT_DIFF_HISTORY), default=0) + 1
        task = {
            "id": next_id,
            "task_id": f"demo-diff-{next_id:03d}",
            "title": f"合同多版本比对 {next_id}",
            "status": "processing",
            "created_at": "2026-07-08 10:00:00",
            "success_count": 0,
            "fail_count": 0,
            "poll_count": 0,
        }
        DOCUMENT_DIFF_HISTORY.insert(0, task)
        return {
            "task_id": task["task_id"],
            "status": task["status"],
            "workflow": [
                {"key": "upload_files", "name": "标准文档与比对文档上传", "status": "completed"},
                {"key": "normalize_files", "name": "标准文档与比对文档格式校验", "status": "completed"},
                {"key": "create_remote_task", "name": "创建文档比对任务", "status": "completed"},
                {"key": "enqueue_polling", "name": "加入状态轮询队列", "status": "completed"},
                {"key": "save_history", "name": "保存历史记录", "status": "completed"},
                {"key": "wait_status_polling", "name": "等待状态轮询", "status": "processing"},
            ],
        }

    def run_engineering_pipeline(self, file_names: list[str] | None = None) -> dict:
        """Run a complete document-diff pipeline."""

        context = demo_context()
        file_names = file_names or ["standard-contract-demo.docx", "contract-v1-demo.docx", "contract-v2-demo.docx"]
        uploads = [file_pipeline.upload_demo_file(file_name, "document_diff") for file_name in file_names]
        created = self.compare_documents()
        task_id = created["task_id"]
        extraction = [
            {
                "file_name": file_name,
                "line_count": 24 + index * 3,
                "paragraph_count": 12 + index,
                "role": "standard" if index == 0 else "compare",
            }
            for index, file_name in enumerate(file_names)
        ]
        model = model_gateway.run_structured_task(
            "document_diff",
            "contract_multi_version_diff",
            {"files": extraction},
        )
        status = self.load_task_status(task_id)
        detail = self.get_detail(task_id)
        diff_items = structured_parser.parse_json_items(detail["diffs"] if detail else [])
        preview = self.preview(task_id)
        local_diff = self.local_line_diff(task_id)
        report = report_builder.build_report(
            "document_diff",
            task_id,
            "合同多版本差异报告",
            {"diff_count": len(diff_items), "success_count": status["success_count"] if status else 0},
            diff_items,
        )
        repository.save_task(
            WorkflowTask(
                task_id=task_id,
                module="document_diff",
                status="completed",
                title="合同多版本差异比对",
                tenant_id=context.tenant_id,
                operator=context.operator,
                current_step="report_generated",
                progress=100,
                payload={"uploads": uploads, "detail": detail, "report": report},
            )
        )
        repository.add_review_record("document_diff", task_id, context.operator, "need_review", diff_items)
        audit_ledger.record(
            "document_diff",
            "run_full_pipeline",
            context.tenant_id,
            context.operator,
            task_id=task_id,
            diff_count=len(diff_items),
        )
        return {
            "task_id": task_id,
            "uploads": uploads,
            "extraction": extraction,
            "model": model,
            "status": status,
            "detail": detail,
            "preview": preview,
            "local_diff": local_diff,
            "report": report,
            "persisted_task": repository.get_task(task_id),
            "workflow": [
                {"key": "upload", "name": "多文档上传与对象存储", "status": "completed"},
                {"key": "format_check", "name": "格式校验和标准文档识别", "status": "completed"},
                {"key": "extract_text", "name": "DOCX/PDF/TXT 文本抽取", "status": "completed"},
                {"key": "create_compare_task", "name": "创建比对任务并写入队列", "status": "completed"},
                {"key": "poll_status", "name": "状态轮询与历史同步", "status": "completed"},
                {"key": "model_diff", "name": "模型差异归纳与异常重试", "status": "completed"},
                {"key": "preview", "name": "预览授权与链接生成", "status": "completed"},
                {"key": "local_fallback", "name": "本地行级 diff 兜底", "status": "completed"},
                {"key": "report_audit", "name": "报告输出、审计日志和调用计数", "status": "completed"},
            ],
        }

    def get_detail(self, task_id: str) -> dict | None:
        item = next((history for history in DOCUMENT_DIFF_HISTORY if history["task_id"] == task_id), None)
        if not item:
            return None
        return {
            **item,
            "origin_file": "standard-contract-demo.docx",
            "compare_files": ["contract-v1-demo.docx", "contract-v2-demo.docx"],
            "diffs": [
                {"clause": "付款周期", "before": "30 日内支付", "after": "15 日内支付", "level": "medium"},
                {"clause": "违约责任", "before": "按实际损失", "after": "固定违约金 5%", "level": "high"},
            ],
        }

    def load_task_status(self, task_id: str) -> dict | None:
        item = next((history for history in DOCUMENT_DIFF_HISTORY if history["task_id"] == task_id), None)
        if not item:
            return None
        item["poll_count"] = int(item.get("poll_count", 0)) + 1
        if item["status"] != "completed" and item["poll_count"] >= 1:
            item["status"] = "completed"
            item["success_count"] = 2
            item["fail_count"] = 0
        return {
            "task_id": task_id,
            "status": item["status"],
            "success_count": item["success_count"],
            "fail_count": item["fail_count"],
            "workflow": [
                {"key": "query_remote_status", "name": "查询比对任务状态", "status": "completed"},
                {"key": "sync_history", "name": "同步历史记录状态", "status": "completed"},
                {"key": "load_diff_info", "name": "读取差异详情", "status": item["status"]},
            ],
            "detail": self.get_detail(task_id) if item["status"] == "completed" else None,
        }

    def preview(self, task_id: str) -> dict | None:
        item = next((history for history in DOCUMENT_DIFF_HISTORY if history["task_id"] == task_id), None)
        if not item:
            return None
        return {
            "task_id": task_id,
            "preview_url": f"/document-diff/preview/{task_id}?preview_key=demo-preview-grant",
            "workflow": [
                {"key": "apply_preview_grant", "name": "申请预览授权", "status": "completed"},
                {"key": "build_preview_url", "name": "生成预览地址", "status": "completed"},
            ],
        }

    def local_line_diff(self, task_id: str) -> dict | None:
        item = next((history for history in DOCUMENT_DIFF_HISTORY if history["task_id"] == task_id), None)
        if not item:
            return None
        return {
            "task_id": task_id,
            "mode": "local_line_diff",
            "left_file": "standard-contract-demo.docx",
            "right_file": "contract-v2-demo.docx",
            "similarity": 0.8732,
            "left_lines": 24,
            "right_lines": 27,
            "added_lines": 3,
            "deleted_lines": 1,
            "workflow": [
                {"key": "extract_left_text", "name": "提取标准文档文本", "status": "completed"},
                {"key": "extract_right_text", "name": "提取比对文档文本", "status": "completed"},
                {"key": "sequence_match", "name": "行级 diff 与相似度计算", "status": "completed"},
                {"key": "limit_detail_rows", "name": "限制明细行数防止超大响应", "status": "completed"},
            ],
            "diff": [
                "- 付款周期: 30 日内支付",
                "+ 付款周期: 15 日内支付",
                "+ 新增保密义务: 未经许可不得披露合同内容",
            ],
        }

    def list_workflow_tasks(self) -> dict:
        """List persisted document-diff workflow tasks."""

        return repository.list_tasks(module="document_diff")

    def list_review_records(self, task_id: str | None = None) -> list[dict]:
        """List document-diff review records."""

        return repository.list_review_records(module="document_diff", subject_id=task_id)

    def audit_summary(self) -> dict:
        """Return audit and usage summary."""

        return {
            "events": audit_ledger.list_events("document_diff"),
            "usage": audit_ledger.usage_summary(),
            "jobs": task_queue.list_jobs("document_diff"),
        }

    @staticmethod
    def _advance_processing_tasks() -> None:
        for item in DOCUMENT_DIFF_HISTORY:
            if item.get("status") == "processing" and int(item.get("poll_count", 0)) > 0:
                item["status"] = "completed"
                item["success_count"] = max(int(item.get("success_count", 0)), 1)


document_diff_agent = DocumentDiffAgent()
