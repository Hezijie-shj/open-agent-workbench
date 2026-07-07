"""File upload, archive extraction, PDF split, and rendering simulation."""

from dataclasses import asdict, dataclass
from pathlib import PurePath

from app.platform.storage import object_store


@dataclass
class UploadedFile:
    """Uploaded file metadata."""

    file_name: str
    content_type: str
    size: int
    object_key: str
    checksum: str


class FilePipeline:
    """Public-safe file pipeline with deterministic demo outputs."""

    archive_suffixes = {".zip", ".rar", ".7z"}
    document_suffixes = {".pdf", ".docx", ".txt", ".xlsx", ".csv"}

    def upload_demo_file(self, file_name: str, module: str) -> dict:
        """Store a tiny demo payload and return metadata."""

        payload = f"demo payload for {module}: {file_name}".encode()
        metadata = object_store.put(file_name, payload, self._guess_content_type(file_name), module=module)
        return asdict(
            UploadedFile(
                file_name=file_name,
                content_type=metadata["content_type"],
                size=metadata["size"],
                object_key=metadata["object_key"],
                checksum=metadata["checksum"],
            )
        )

    def extract_archive(self, file_name: str) -> dict:
        """Simulate archive extraction and return child files."""

        suffix = PurePath(file_name).suffix.lower()
        extracted = [file_name]
        if suffix in self.archive_suffixes:
            extracted = [
                file_name.replace(suffix, "-statement.pdf"),
                file_name.replace(suffix, "-extra.csv"),
            ]
        return {"archive": file_name, "extracted": extracted, "archive_detected": suffix in self.archive_suffixes}

    def split_pdf(self, file_name: str, total_pages: int = 6) -> list[dict]:
        """Return page descriptors for a PDF."""

        return [
            {
                "page": page,
                "page_key": f"{file_name}:page-{page}",
                "status": "blank" if page in {5, 6} else "ready",
                "width": 1240,
                "height": 1754,
            }
            for page in range(1, total_pages + 1)
        ]

    def render_page_images(self, pages: list[dict]) -> list[dict]:
        """Return rendered page image descriptors."""

        return [
            {
                **page,
                "image_key": f"rendered/{page['page_key']}.png",
                "dpi": 180,
                "render_status": "skipped_blank" if page["status"] == "blank" else "rendered",
            }
            for page in pages
        ]

    def classify_pages(self, rendered_pages: list[dict]) -> list[dict]:
        """Classify blank and error pages."""

        results = []
        for page in rendered_pages:
            issues: list[str] = []
            if page["status"] == "blank":
                issues.append("blank_page")
            if page["page"] == 2:
                issues.append("low_contrast")
            results.append({**page, "issues": issues, "need_review": bool(issues)})
        return results

    @staticmethod
    def _guess_content_type(file_name: str) -> str:
        suffix = PurePath(file_name).suffix.lower()
        if suffix == ".pdf":
            return "application/pdf"
        if suffix == ".docx":
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if suffix in {".zip", ".rar", ".7z"}:
            return "application/archive"
        return "application/octet-stream"


file_pipeline = FilePipeline()
