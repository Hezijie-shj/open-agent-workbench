"""Local regulation comparison workflow for the public demo boundary."""

from app.mock_data import REGULATION_TASKS
from app.platform.audit import audit_ledger
from app.platform.context import demo_context
from app.platform.file_pipeline import file_pipeline
from app.platform.model_gateway import model_gateway
from app.platform.parsers import structured_parser
from app.platform.queue import task_queue
from app.platform.reporting import report_builder
from app.platform.repository import WorkflowTask, repository


class RegulationsAgent:
    """Policy document comparison workflow using local demo data."""

    def list_tasks(self) -> dict:
        return {"items": REGULATION_TASKS, "page": 1, "size": 10, "total": len(REGULATION_TASKS)}

    def create_demo_task(self, uploaded: bool = False) -> dict:
        next_id = max((item["id"] for item in REGULATION_TASKS), default=0) + 1
        task = {
            "id": next_id,
            "name": f"制度比对本地任务 {next_id}",
            "standard": "通用合规规则库 V2026",
            "uploaded_at": "2026-07-08 10:00:00",
            "status": "比对中" if uploaded else "待比对",
            "risk_count": 0,
            "summary": "示例文档已上传, 等待本地演示比对。" if uploaded else "任务已创建, 等待上传示例文档。",
        }
        REGULATION_TASKS.insert(0, task)
        return task

    def create_upload_task(self, file_name: str = "origin-policy-demo.pdf") -> dict:
        """Create an uploaded regulation task and queue comparison."""

        context = demo_context()
        task = self.create_demo_task(uploaded=True)
        upload = file_pipeline.upload_demo_file(file_name, "regulations")
        queue_job = task_queue.enqueue("regulations", "compare_regulation", task_id=task["id"], file_name=file_name)
        saved = repository.save_task(
            WorkflowTask(
                task_id=f"reg-{task['id']:04d}",
                module="regulations",
                status="queued",
                title=task["name"],
                tenant_id=context.tenant_id,
                operator=context.operator,
                current_step="uploaded",
                progress=15,
                payload={"task": task, "upload": upload, "queue_job": queue_job},
            )
        )
        audit_ledger.record("regulations", "upload_document", context.tenant_id, context.operator, task_id=task["id"])
        return saved

    def get_task(self, task_id: int) -> dict | None:
        task = next((item for item in REGULATION_TASKS if item["id"] == task_id), None)
        if not task:
            return None
        return {
            **task,
            "files": [
                {"name": "origin-policy-demo.pdf", "role": "origin", "status": "已读取"},
                {"name": "rule-library-demo.pdf", "role": "compare", "status": "已匹配"},
            ],
            "highlights": [
                {"text": "审批流程", "page": 2, "color": "yellow", "similarity": 0.92},
                {"text": "资料留痕", "page": 4, "color": "red", "similarity": 0.88},
            ],
        }

    def match_text(self, task_id: int) -> dict:
        task = self.get_task(task_id)
        return {
            "task": task,
            "group_y": [{"target_text": "审批流程", "matched_text": "采购审批流程应完整留痕"}],
            "group_r": {"target_text": "资料留痕", "matched_text": "资料留痕不少于三年"},
        }

    def compare_documents_workflow(self, task_id: int) -> dict:
        task = self.get_task(task_id)
        return {
            "task": task,
            "mode": "full_document_compare",
            "status": "completed",
            "workflow": [
                {"key": "upload_origin", "name": "制度文件上传与对象存储", "status": "completed"},
                {"key": "download_origin", "name": "下载源制度文件", "status": "completed"},
                {
                    "key": "load_knowledge_base",
                    "name": "读取规则库文档列表",
                    "status": "completed",
                    "document_count": 2,
                },
                {"key": "download_compare_files", "name": "下载比对文件并建立本地缓存", "status": "completed"},
                {"key": "create_task_record", "name": "创建比对任务记录", "status": "completed"},
                {"key": "extract_text", "name": "提取 PDF/DOCX/TXT 文本", "status": "completed"},
                {"key": "prompt_compare", "name": "比对提示词模板与模型重试", "status": "completed"},
                {"key": "compare_each_document", "name": "逐文件调用比对 Agent", "status": "completed"},
                {"key": "parse_json", "name": "JSON 解析、字段标准化和风险分级", "status": "completed"},
                {"key": "save_result", "name": "保存比对结果", "status": "completed"},
                {"key": "highlight_document", "name": "生成定位与高亮信息", "status": "completed"},
                {"key": "audit_usage", "name": "审计日志与调用计数", "status": "completed"},
            ],
            "comparison_results": [
                {
                    "compare_file": "rule-library-demo.pdf",
                    "status": "success",
                    "risk_count": task["risk_count"] if task else 0,
                    "summary": "发现审批流程、资料留痕、责任边界三类差异。",
                },
                {
                    "compare_file": "operation-guideline-demo.docx",
                    "status": "success",
                    "risk_count": 2,
                    "summary": "发现术语表述不一致和附件引用缺失。",
                },
            ],
            "success_count": 2,
            "fail_count": 0,
        }

    def run_engineering_pipeline(self, task_id: int, file_name: str = "origin-policy-demo.pdf") -> dict:
        """Run the full public demo regulation comparison pipeline."""

        context = demo_context()
        task = self.get_task(task_id) or self.create_demo_task(uploaded=True)
        upload = file_pipeline.upload_demo_file(file_name, "regulations")
        compare_files = ["rule-library-demo.pdf", "operation-guideline-demo.docx"]
        extracted_text = [
            {
                "file_name": file_name,
                "role": "origin",
                "paragraph_count": 36,
                "checksum": upload["checksum"],
            },
            *[
                {
                    "file_name": compare_file,
                    "role": "knowledge_base",
                    "paragraph_count": 24 + index * 8,
                    "checksum": f"demo-kb-{index}",
                }
                for index, compare_file in enumerate(compare_files, start=1)
            ],
        ]
        model = model_gateway.run_structured_task(
            "regulations",
            "regulation_semantic_compare",
            {"origin": extracted_text[0], "compare_files": extracted_text[1:]},
        )
        single = self.compare_single_document(task_id)
        items = structured_parser.parse_json_items(single["items"])
        fallback = self.text_match_fallback(task_id)
        report = report_builder.build_report(
            "regulations",
            str(task_id),
            f"{task['name']} 风险比对报告",
            {"risk_count": len(items), "highlight_count": len(self.get_task(task_id)["highlights"]) if task else 0},
            items,
        )
        repository.save_task(
            WorkflowTask(
                task_id=f"reg-{task_id:04d}",
                module="regulations",
                status="completed",
                title=task["name"],
                tenant_id=context.tenant_id,
                operator=context.operator,
                current_step="report_generated",
                progress=100,
                payload={"upload": upload, "items": items, "report": report},
            )
        )
        repository.add_review_record("regulations", str(task_id), context.operator, "need_review", items)
        audit_ledger.record(
            "regulations",
            "run_full_pipeline",
            context.tenant_id,
            context.operator,
            task_id=task_id,
            risk_count=len(items),
        )
        return {
            "task": task,
            "upload": upload,
            "knowledge_base": {"files": compare_files, "source": "local_demo_rule_library"},
            "extracted_text": extracted_text,
            "model": model,
            "items": items,
            "fallback": fallback,
            "report": report,
            "persisted_task": repository.get_task(f"reg-{task_id:04d}"),
            "workflow": [
                {"key": "upload", "name": "制度文件上传与对象存储", "status": "completed"},
                {"key": "load_rule_library", "name": "规则库文件列表读取", "status": "completed"},
                {"key": "extract_text", "name": "PDF/DOCX/TXT 文本抽取", "status": "completed"},
                {"key": "model_compare", "name": "模型比对、提示词模板和重试", "status": "completed"},
                {"key": "parse_normalize", "name": "JSON 解析、字段标准化和风险分级", "status": "completed"},
                {"key": "highlight_fallback", "name": "文本定位、高亮和截断兜底", "status": "completed"},
                {"key": "persist_review", "name": "事务保存、复核记录和状态机", "status": "completed"},
                {"key": "report_audit", "name": "报告输出、审计日志和调用计数", "status": "completed"},
            ],
        }

    def compare_single_document(self, task_id: int, compare_file: str = "rule-library-demo.pdf") -> dict:
        task = self.get_task(task_id)
        return {
            "task": task,
            "mode": "single_document_compare",
            "origin_file": "origin-policy-demo.pdf",
            "compare_file": compare_file,
            "workflow": [
                {"key": "read_origin_text", "name": "读取源制度文本", "status": "completed"},
                {"key": "read_compare_text", "name": "读取单个规则库文档", "status": "completed"},
                {"key": "agent_compare", "name": "执行单文档语义比对", "status": "completed"},
                {"key": "normalize_result", "name": "标准化风险项和条款差异", "status": "completed"},
            ],
            "items": [
                {
                    "clause": "审批流程",
                    "origin_text": "采购事项按金额分级审批。",
                    "compare_text": "采购审批流程应完整留痕并保留审批链路。",
                    "risk_level": "medium",
                    "suggestion": "补充审批链路留痕要求。",
                },
                {
                    "clause": "资料留痕",
                    "origin_text": "业务资料由经办部门保存。",
                    "compare_text": "关键资料留痕不少于三年。",
                    "risk_level": "high",
                    "suggestion": "明确保存期限和责任部门。",
                },
            ],
        }

    def text_match_fallback(self, task_id: int) -> dict:
        task = self.get_task(task_id)
        return {
            "task": task,
            "mode": "text_match_fallback",
            "workflow": [
                {"key": "extract_document_paragraphs", "name": "提取 Word/PDF 段落", "status": "completed"},
                {"key": "fast_similarity", "name": "快速相似度召回", "status": "completed"},
                {"key": "best_match_fallback", "name": "无强命中时返回最高相似段落", "status": "completed"},
                {"key": "extend_truncated_match", "name": "跨段落截断补全文本", "status": "completed"},
                {"key": "highlight_coordinates", "name": "生成高亮坐标或段落范围", "status": "completed"},
            ],
            "group_y": [
                {
                    "target_text": "审批流程",
                    "matched_text": "采购审批流程应完整留痕",
                    "similarity": 0.92,
                    "page": 2,
                    "fallback": False,
                }
            ],
            "group_r": {
                "target_text": "资料留痕",
                "matched_text": "资料留痕不少于三年",
                "similarity": 0.88,
                "page": 4,
                "fallback": True,
                "fallback_reason": "跨段落文本被截断, 已使用后续段落补全。",
            },
        }

    def list_workflow_tasks(self) -> dict:
        """List persisted regulation workflow tasks."""

        return repository.list_tasks(module="regulations")

    def list_review_records(self, task_id: int | None = None) -> list[dict]:
        """List regulation review records."""

        return repository.list_review_records(module="regulations", subject_id=str(task_id) if task_id else None)

    def audit_summary(self) -> dict:
        """Return audit and usage summary."""

        return {
            "events": audit_ledger.list_events("regulations"),
            "usage": audit_ledger.usage_summary(),
            "jobs": task_queue.list_jobs("regulations"),
        }


regulations_agent = RegulationsAgent()
