"""OCR adapter simulation."""


class OcrAdapter:
    """Generate deterministic OCR blocks and coordinates."""

    def extract_blocks(self, image_key: str, page: int, rows: list[dict] | None = None) -> dict:
        """Return OCR blocks for a rendered page."""

        source_rows = rows or []
        blocks = []
        if not source_rows:
            blocks.append(
                {
                    "block_id": f"P{page}-B0",
                    "text": "空白页或未识别到有效交易",
                    "bbox": [64, 160, 760, 204],
                    "confidence": 0.62,
                    "type": "notice",
                }
            )
        for index, row in enumerate(source_rows):
            top = 190 + index * 58
            blocks.extend(
                [
                    {
                        "block_id": f"P{page}-R{index}-D",
                        "text": row.get("date", ""),
                        "bbox": [48, top, 210, top + 36],
                        "confidence": 0.96,
                        "type": "date",
                    },
                    {
                        "block_id": f"P{page}-R{index}-A",
                        "text": row.get("amount", ""),
                        "bbox": [420, top, 560, top + 36],
                        "confidence": 0.94,
                        "type": "amount",
                    },
                    {
                        "block_id": f"P{page}-R{index}-B",
                        "text": row.get("balance", ""),
                        "bbox": [586, top, 728, top + 36],
                        "confidence": 0.92,
                        "type": "balance",
                    },
                ]
            )
        return {
            "image_key": image_key,
            "page": page,
            "blocks": self.clean_blocks(blocks),
            "block_count": len(blocks),
        }

    @staticmethod
    def clean_blocks(blocks: list[dict]) -> list[dict]:
        """Normalize OCR text blocks."""

        cleaned = []
        for block in blocks:
            text = " ".join(str(block.get("text", "")).split())
            cleaned.append({**block, "text": text})
        return cleaned


ocr_adapter = OcrAdapter()
