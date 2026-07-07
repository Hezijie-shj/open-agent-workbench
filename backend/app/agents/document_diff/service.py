"""Local document-diff workflow for the public demo boundary."""


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
                {"key": "normalize_files", "name": "标准文档与比对文档格式校验", "status": "completed"},
                {"key": "create_remote_task", "name": "创建文档比对任务", "status": "completed"},
                {"key": "save_history", "name": "保存历史记录", "status": "completed"},
                {"key": "wait_status_polling", "name": "等待状态轮询", "status": "processing"},
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

    @staticmethod
    def _advance_processing_tasks() -> None:
        for item in DOCUMENT_DIFF_HISTORY:
            if item.get("status") == "processing" and int(item.get("poll_count", 0)) > 0:
                item["status"] = "completed"
                item["success_count"] = max(int(item.get("success_count", 0)), 1)


document_diff_agent = DocumentDiffAgent()
