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

    def compare_documents(self) -> dict:
        """创建文档差异比对任务."""
        return document_diff_agent.compare_documents()

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


document_diff_service = DocumentDiffService()
