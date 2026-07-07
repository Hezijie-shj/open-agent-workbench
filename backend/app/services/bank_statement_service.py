"""流水分析服务."""

from app.agents.bank_statement.service import bank_statement_agent


class BankStatementService:
    """流水分析服务."""

    def list_projects(self) -> dict:
        """获取项目分页列表.

        :return: 项目分页数据.
        :rtype: dict
        """
        return bank_statement_agent.list_projects()

    def get_project(self, project_id: int) -> dict | None:
        """按 ID 获取项目.

        :param int project_id: 项目 ID.
        :return: 项目数据.
        :rtype: dict | None
        """
        return bank_statement_agent.get_project(project_id)

    def create_demo_project(self) -> dict:
        """创建本地演示项目."""
        return bank_statement_agent.create_demo_project()

    def create_upload_task(self, file_name: str = "statement-demo.zip") -> dict:
        """创建上传解析任务."""
        return bank_statement_agent.create_upload_task(file_name)

    def run_engineering_pipeline(self, project_id: int, file_name: str = "statement-demo.zip") -> dict:
        """运行完整工程化流水解析流程."""
        return bank_statement_agent.run_engineering_pipeline(project_id, file_name)

    def mark_reviewed(self, project_id: int) -> dict | None:
        """标记项目复核完成."""
        return bank_statement_agent.mark_reviewed(project_id)

    def delete_project(self, project_id: int) -> dict | None:
        """删除本地演示项目."""
        return bank_statement_agent.delete_project(project_id)

    def get_analysis_result(self, project_id: int, page: int) -> dict:
        """获取识别结果.

        :param int project_id: 项目 ID.
        :param int page: 页码.
        :return: 识别结果数据.
        :rtype: dict
        """
        return bank_statement_agent.recognize_page(project_id, page)

    def recognize_full_pdf(self, project_id: int) -> dict:
        """获取完整 PDF 识别流程演示结果."""
        return bank_statement_agent.recognize_full_pdf(project_id)

    def recognize_single_page(self, project_id: int, page: int) -> dict:
        """获取单页识别流程演示结果."""
        return bank_statement_agent.recognize_single_page(project_id, page)

    def sensitive_fallback(self, project_id: int, page: int) -> dict:
        """获取敏感词兜底流程演示结果."""
        return bank_statement_agent.sensitive_fallback(project_id, page)

    def get_report(self, project_id: int) -> dict | None:
        """获取核查报告.

        :param int project_id: 项目 ID.
        :return: 报告数据.
        :rtype: dict | None
        """
        return bank_statement_agent.get_report(project_id)

    def get_detail_rows(self, project_id: int, label: str) -> list[dict]:
        """获取报告抽屉明细."""
        return bank_statement_agent.detail_rows(project_id, label)

    def list_workflow_tasks(self) -> dict:
        """获取流水解析任务状态列表."""
        return bank_statement_agent.list_workflow_tasks()

    def list_review_records(self, project_id: int | None = None) -> list[dict]:
        """获取复核记录."""
        return bank_statement_agent.list_review_records(project_id)

    def audit_summary(self) -> dict:
        """获取审计与调用计数."""
        return bank_statement_agent.audit_summary()


bank_statement_service = BankStatementService()
