"""Local bank statement workflow for the public demo boundary."""

from app.mock_data import ANALYSIS_RESULTS, PROJECTS, REPORTS
from app.platform.audit import audit_ledger
from app.platform.context import demo_context
from app.platform.file_pipeline import file_pipeline
from app.platform.model_gateway import model_gateway
from app.platform.ocr import ocr_adapter
from app.platform.parsers import business_validator, structured_parser
from app.platform.queue import task_queue
from app.platform.reporting import report_builder
from app.platform.repository import WorkflowTask, repository


class BankStatementAgent:
    """Bank statement workflow without external service, storage, queue, or database dependencies."""

    total_pages = 6

    def list_projects(self) -> dict:
        return {"items": PROJECTS, "page": 1, "size": 10, "total": len(PROJECTS)}

    def get_project(self, project_id: int) -> dict | None:
        return next((item for item in PROJECTS if item["id"] == project_id), None)

    def create_demo_project(self) -> dict:
        next_id = max((item["id"] for item in PROJECTS), default=0) + 1
        project = {
            "id": next_id,
            "name": f"本地上传样例 {next_id}",
            "date_range": "2025-09-01 09:00:00 至 2025-09-30 18:00:00",
            "amount": "¥2,680,000.00",
            "created_at": "2026-07-08 10:00:00",
            "creator": "demo",
            "status": "解析中",
        }
        PROJECTS.insert(0, project)
        return project

    def create_upload_task(self, file_name: str = "statement-demo.zip") -> dict:
        """Create a public-safe upload task and queue a parse job."""

        context = demo_context()
        project = self.create_demo_project()
        uploaded = file_pipeline.upload_demo_file(file_name, "bank_statement")
        queue_job = task_queue.enqueue(
            "bank_statement",
            "parse_statement",
            project_id=project["id"],
            file_name=file_name,
        )
        task = WorkflowTask(
            task_id=f"bank-{project['id']:04d}",
            module="bank_statement",
            status="queued",
            title=project["name"],
            tenant_id=context.tenant_id,
            operator=context.operator,
            current_step="uploaded",
            progress=10,
            payload={"project": project, "uploaded": uploaded, "queue_job": queue_job},
        )
        with repository.transaction():
            saved = repository.save_task(task)
            audit_ledger.record(
                "bank_statement",
                "upload_file",
                context.tenant_id,
                context.operator,
                file_name=file_name,
                project_id=project["id"],
            )
        return saved

    def run_engineering_pipeline(self, project_id: int, file_name: str = "statement-demo.zip") -> dict:
        """Run the full public demo pipeline for a bank-statement project."""

        context = demo_context()
        project = self.get_project(project_id) or self.create_demo_project()
        upload = file_pipeline.upload_demo_file(file_name, "bank_statement")
        archive = file_pipeline.extract_archive(file_name)
        pdf_file = next((item for item in archive["extracted"] if item.endswith(".pdf")), "statement-demo.pdf")
        pages = file_pipeline.split_pdf(pdf_file, self.total_pages)
        rendered_pages = file_pipeline.render_page_images(pages)
        classified_pages = file_pipeline.classify_pages(rendered_pages)
        page_results = []
        all_rows = []
        for page in classified_pages:
            rows = ANALYSIS_RESULTS.get(project_id, {}).get(page["page"], [])
            ocr = ocr_adapter.extract_blocks(page["image_key"], page["page"], rows)
            model = model_gateway.run_structured_task(
                "bank_statement",
                "statement_page_to_rows",
                {"page": page, "ocr_blocks": ocr["blocks"]},
            )
            parsed_rows = structured_parser.parse_csv_rows(
                [self._with_trace(row, index) for index, row in enumerate(rows)]
            )
            all_rows.extend(parsed_rows)
            page_results.append(
                {
                    "page": page["page"],
                    "status": "empty" if page["status"] == "blank" else "recognized",
                    "ocr": {"block_count": ocr["block_count"], "image_key": ocr["image_key"]},
                    "model": model,
                    "row_count": len(parsed_rows),
                    "issues": page["issues"],
                }
            )
        validation = business_validator.validate_balance_sequence(all_rows)
        error_pages = business_validator.classify_error_pages(classified_pages)
        sensitive = model_gateway.guard_sensitive_output(all_rows, ["counterparty"])
        fallback = self.sensitive_fallback(project_id, 1)
        report = report_builder.build_report(
            "bank_statement",
            str(project_id),
            f"{project['name']} 核查报告",
            {
                "row_count": len(all_rows),
                "validation_passed": validation["passed"],
                "error_page_count": len(error_pages),
            },
            all_rows,
        )
        repository.save_task(
            WorkflowTask(
                task_id=f"bank-{project_id:04d}",
                module="bank_statement",
                status="completed",
                title=project["name"],
                tenant_id=context.tenant_id,
                operator=context.operator,
                current_step="report_generated",
                progress=100,
                payload={"upload": upload, "report": report, "validation": validation},
                errors=validation["issues"] + error_pages,
            )
        )
        repository.add_review_record(
            "bank_statement",
            str(project_id),
            context.operator,
            "need_review" if validation["issues"] or error_pages else "passed",
            validation["issues"] + error_pages,
        )
        audit_ledger.record(
            "bank_statement",
            "run_full_pipeline",
            context.tenant_id,
            context.operator,
            project_id=project_id,
            row_count=len(all_rows),
            error_page_count=len(error_pages),
        )
        return {
            "project": project,
            "task": repository.get_task(f"bank-{project_id:04d}"),
            "upload": upload,
            "archive": archive,
            "pages": page_results,
            "validation": validation,
            "error_pages": error_pages,
            "sensitive_guard": sensitive,
            "sensitive_fallback": fallback,
            "report": report,
            "workflow": [
                {"key": "upload", "name": "文件上传与对象存储", "status": "completed"},
                {"key": "extract_archive", "name": "压缩包识别与解压", "status": "completed"},
                {"key": "split_pdf", "name": "PDF 拆页", "status": "completed", "page_count": len(pages)},
                {"key": "render_pages", "name": "页面图片渲染", "status": "completed"},
                {"key": "ocr_blocks", "name": "OCR 文本块与坐标提取", "status": "completed"},
                {"key": "model_parse", "name": "模型结构化与重试记录", "status": "completed"},
                {"key": "parse_validate", "name": "CSV/JSON 解析与金额校验", "status": "completed"},
                {"key": "state_persist", "name": "状态机与事务保存", "status": "completed"},
                {"key": "review_report", "name": "复核记录与报告生成", "status": "completed"},
                {"key": "audit_billing", "name": "审计日志与调用计数", "status": "completed"},
            ],
        }

    def mark_reviewed(self, project_id: int) -> dict | None:
        project = self.get_project(project_id)
        if not project:
            return None
        project["status"] = "已完成"
        return project

    def delete_project(self, project_id: int) -> dict | None:
        project = self.get_project(project_id)
        if not project:
            return None
        PROJECTS.remove(project)
        return project

    def recognize_page(self, project_id: int, page: int) -> dict:
        transactions = ANALYSIS_RESULTS.get(project_id, {}).get(page, [])
        return {
            "project": self.get_project(project_id),
            "file_name": "demo-statement-2025-07.pdf",
            "page": page,
            "total_pages": self.total_pages,
            "items": [self._with_trace(item, index) for index, item in enumerate(transactions)],
            "error_pages": self.error_pages(project_id),
        }

    def recognize_full_pdf(self, project_id: int) -> dict:
        pages = [self.recognize_page(project_id, page) for page in range(1, self.total_pages + 1)]
        recognized_pages = [page for page in pages if page["items"]]
        return {
            "project": self.get_project(project_id),
            "file_name": "demo-statement-2025-07.pdf",
            "mode": "full_pdf",
            "status": "completed",
            "workflow": [
                {"key": "upload", "name": "文件上传与对象存储", "status": "completed"},
                {"key": "extract_archive", "name": "压缩包识别与解压", "status": "completed"},
                {"key": "split_pdf", "name": "PDF 拆页", "status": "completed", "page_count": self.total_pages},
                {"key": "render_pages", "name": "页面图片渲染", "status": "completed"},
                {"key": "ocr_blocks", "name": "OCR 文本块提取与坐标映射", "status": "completed"},
                {"key": "model_retry", "name": "模型调用、提示词模板与重试", "status": "completed"},
                {"key": "single_page_recognition", "name": "逐页识别", "status": "completed"},
                {"key": "parse_validate", "name": "CSV/JSON 解析与金额校验", "status": "completed"},
                {"key": "merge_rows", "name": "合并流水", "status": "completed"},
                {"key": "integrity_check", "name": "连续性与余额校验", "status": "completed"},
                {"key": "persist_state", "name": "数据库事务、分页、筛选、状态机模拟", "status": "completed"},
                {"key": "review_report", "name": "复核记录、报告模板与下载接口模拟", "status": "completed"},
            ],
            "pages": [
                {
                    "page": page["page"],
                    "status": "recognized" if page["items"] else "empty",
                    "row_count": len(page["items"]),
                    "fallback_used": self._needs_sensitive_fallback(project_id, page["page"]),
                }
                for page in pages
            ],
            "summary": {
                "total_pages": self.total_pages,
                "recognized_pages": len(recognized_pages),
                "row_count": sum(len(page["items"]) for page in pages),
                "error_pages": self.error_pages(project_id),
            },
        }

    def recognize_single_page(self, project_id: int, page: int) -> dict:
        result = self.recognize_page(project_id, page)
        fallback = self.sensitive_fallback(project_id, page)
        return {
            **result,
            "mode": "single_page",
            "workflow": [
                {"key": "render_page", "name": "PDF 单页渲染", "status": "completed"},
                {"key": "ocr_blocks", "name": "OCR 文本块提取", "status": "completed"},
                {"key": "model_csv", "name": "模型生成结构化 CSV", "status": "completed"},
                {
                    "key": "sensitive_guard",
                    "name": "敏感词打断检测",
                    "status": "fallback" if fallback["used"] else "passed",
                },
                {"key": "id_backfill", "name": "ID 回填与坐标绑定", "status": "completed"},
            ],
            "ocr_payload": {
                "layout_mode": "row_trace_mock",
                "block_count": len(result["items"]) * 4,
                "source_id_mode": "id_reference",
            },
            "sensitive_fallback": fallback,
        }

    def sensitive_fallback(self, project_id: int, page: int) -> dict:
        rows = self.recognize_page(project_id, page)["items"]
        used = self._needs_sensitive_fallback(project_id, page)
        return {
            "used": used,
            "reason": "mock_redaction_guard" if used else "",
            "strategy": "id_only_then_local_backfill",
            "id_only_fields": ["counterparty", "summary"],
            "backfilled_fields": ["counterparty", "source_ids", "bbox"],
            "recovered_row_count": len(rows) if used else 0,
            "safe_output": [
                {
                    "id": item["id"],
                    "source_ids": item["source_ids"],
                    "counterparty_ref": "#block_ref",
                    "summary_ref": "#block_ref",
                }
                for item in rows
            ],
        }

    def get_report(self, project_id: int) -> dict | None:
        return REPORTS.get(project_id)

    def error_pages(self, project_id: int) -> list[dict]:
        rows = ANALYSIS_RESULTS.get(project_id, {}).get(1, [])
        return [
            {
                "file_id": 1,
                "page": 1,
                "error_type": ["amount"] if any(item["amount"].startswith("-") for item in rows) else [],
                "ignored": False,
            }
        ]

    def detail_rows(self, project_id: int, label: str) -> list[dict]:
        rows = ANALYSIS_RESULTS.get(project_id, {}).get(1, [])
        return [
            {
                "id": item["id"],
                "date": item["date"],
                "counterparty": ["晨星材料样例", "北桥工程样例", "云舟信息样例", "星河经营账户"][index % 4],
                "type": item["type"],
                "amount": item["amount"],
                "balance": item["balance"],
                "label": label,
            }
            for index, item in enumerate(rows)
        ]

    def list_workflow_tasks(self) -> dict:
        """List persisted bank-statement workflow tasks."""

        return repository.list_tasks(module="bank_statement")

    def list_review_records(self, project_id: int | None = None) -> list[dict]:
        """List review records for bank-statement workflows."""

        return repository.list_review_records(
            module="bank_statement",
            subject_id=str(project_id) if project_id is not None else None,
        )

    def audit_summary(self) -> dict:
        """Return audit and usage summary."""

        return {
            "events": audit_ledger.list_events("bank_statement"),
            "usage": audit_ledger.usage_summary(),
            "jobs": task_queue.list_jobs("bank_statement"),
        }

    @staticmethod
    def _needs_sensitive_fallback(project_id: int, page: int) -> bool:
        return project_id == 1 and page == 1

    @staticmethod
    def _with_trace(item: dict, index: int) -> dict:
        top = 190 + index * 58
        return {
            **item,
            "counterparty": ["晨星材料样例", "北桥工程样例", "云舟信息样例", "星河经营账户"][index % 4],
            "source_ids": [f"T{item['id']}-D", f"T{item['id']}-A", f"T{item['id']}-B"],
            "bbox": [48, top, 672, top + 42],
            "confidence": 0.86 if item["amount"].startswith("-") else 0.94,
            "issue": "支出需复核" if item["amount"].startswith("-") else "",
        }


bank_statement_agent = BankStatementAgent()
