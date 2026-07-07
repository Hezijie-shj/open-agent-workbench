"""Local bank statement workflow for the public demo boundary."""

from app.mock_data import ANALYSIS_RESULTS, PROJECTS, REPORTS


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
                {"key": "split_pdf", "name": "PDF 拆页", "status": "completed", "page_count": self.total_pages},
                {"key": "single_page_recognition", "name": "逐页识别", "status": "completed"},
                {"key": "merge_rows", "name": "合并流水", "status": "completed"},
                {"key": "integrity_check", "name": "连续性与余额校验", "status": "completed"},
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
