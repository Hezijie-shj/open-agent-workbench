"""文档差异比对服务."""

from app.agents.document_diff.service import document_diff_agent


class DocumentDiffService:
    """文档差异比对服务."""

    def list_history(self) -> dict:
        """获取文档比对历史."""
        return document_diff_agent.list_history()

    def create_demo_task(self) -> dict:
        """创建本地文档差异比对样例."""
        return document_diff_agent.create_demo_task()

    def create_upload_task(self, file_names: list[str] | None = None) -> dict:
        """创建文档差异上传任务."""
        return document_diff_agent.create_upload_task(file_names)

    def compare_documents(self) -> dict:
        """创建文档差异比对任务."""
        return document_diff_agent.compare_documents()

    def run_engineering_pipeline(self, file_names: list[str] | None = None) -> dict:
        """运行完整工程化文档差异比对流程."""
        return document_diff_agent.run_engineering_pipeline(file_names)

    def get_detail(self, task_id: str) -> dict | None:
        """获取文档比对详情."""
        return document_diff_agent.get_detail(task_id)

    def load_task_status(self, task_id: str) -> dict | None:
        """同步文档比对任务状态."""
        return document_diff_agent.load_task_status(task_id)

    def preview(self, task_id: str) -> dict | None:
        """获取文档比对预览地址."""
        return document_diff_agent.preview(task_id)

    def local_line_diff(self, task_id: str) -> dict | None:
        """获取本地行级 diff 流程演示结果."""
        return document_diff_agent.local_line_diff(task_id)

    def list_workflow_tasks(self) -> dict:
        """获取文档差异任务状态列表."""
        return document_diff_agent.list_workflow_tasks()

    def list_review_records(self, task_id: str | None = None) -> list[dict]:
        """获取复核记录."""
        return document_diff_agent.list_review_records(task_id)

    def audit_summary(self) -> dict:
        """获取审计与调用计数."""
        return document_diff_agent.audit_summary()


document_diff_service = DocumentDiffService()
