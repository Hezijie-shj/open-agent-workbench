"""规章制度比对服务."""

from app.agents.regulations.service import regulations_agent


class RegulationsService:
    """规章制度比对服务."""

    def list_tasks(self) -> dict:
        """获取规章制度任务分页列表.

        :return: 任务分页数据.
        :rtype: dict
        """
        return regulations_agent.list_tasks()

    def create_demo_task(self, uploaded: bool = False) -> dict:
        """创建本地演示制度比对任务."""
        return regulations_agent.create_demo_task(uploaded)

    def create_upload_task(self, file_name: str = "origin-policy-demo.pdf") -> dict:
        """创建制度文档上传任务."""
        return regulations_agent.create_upload_task(file_name)

    def get_task(self, task_id: int) -> dict | None:
        """获取规章制度任务详情.

        :param int task_id: 任务 ID.
        :return: 任务详情.
        :rtype: dict | None
        """
        return regulations_agent.get_task(task_id)

    def match_text(self, task_id: int) -> dict:
        """获取本地文本匹配演示结果."""
        return regulations_agent.match_text(task_id)

    def compare_documents_workflow(self, task_id: int) -> dict:
        """获取完整制度文档比对流程演示结果."""
        return regulations_agent.compare_documents_workflow(task_id)

    def run_engineering_pipeline(self, task_id: int, file_name: str = "origin-policy-demo.pdf") -> dict:
        """运行完整工程化制度比对流程."""
        return regulations_agent.run_engineering_pipeline(task_id, file_name)

    def compare_single_document(self, task_id: int, compare_file: str = "rule-library-demo.pdf") -> dict:
        """获取单文档比对流程演示结果."""
        return regulations_agent.compare_single_document(task_id, compare_file)

    def text_match_fallback(self, task_id: int) -> dict:
        """获取文本定位和截断兜底流程演示结果."""
        return regulations_agent.text_match_fallback(task_id)

    def list_workflow_tasks(self) -> dict:
        """获取制度比对任务状态列表."""
        return regulations_agent.list_workflow_tasks()

    def list_review_records(self, task_id: int | None = None) -> list[dict]:
        """获取制度比对复核记录."""
        return regulations_agent.list_review_records(task_id)

    def audit_summary(self) -> dict:
        """获取审计与调用计数."""
        return regulations_agent.audit_summary()


regulations_service = RegulationsService()
