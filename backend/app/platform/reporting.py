"""Report generation simulation."""


class ReportBuilder:
    """Build public-safe report metadata."""

    def build_report(self, module: str, subject_id: str, title: str, summary: dict, rows: list[dict]) -> dict:
        """Return report metadata and download descriptors."""

        base = f"/api/v1/{module}/reports/{subject_id}"
        return {
            "subject_id": subject_id,
            "title": title,
            "template": "public-demo-template.docx",
            "summary": summary,
            "row_count": len(rows),
            "downloads": {
                "json": f"{base}.json",
                "docx": f"{base}.docx",
                "pdf": f"{base}.pdf",
            },
            "status": "generated",
        }


report_builder = ReportBuilder()
