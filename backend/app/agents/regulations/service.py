"""Local regulation comparison workflow for the public demo boundary."""

from app.mock_data import REGULATION_TASKS


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
                {"key": "compare_each_document", "name": "逐文件调用比对 Agent", "status": "completed"},
                {"key": "save_result", "name": "保存比对结果", "status": "completed"},
                {"key": "highlight_document", "name": "生成定位与高亮信息", "status": "completed"},
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


regulations_agent = RegulationsAgent()
