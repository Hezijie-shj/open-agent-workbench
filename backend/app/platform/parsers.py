"""Parsing, normalization, and validation helpers."""

from decimal import Decimal, InvalidOperation


class StructuredParser:
    """Parse model-style structured outputs."""

    def parse_csv_rows(self, rows: list[dict]) -> list[dict]:
        """Normalize transaction rows."""

        parsed = []
        for index, row in enumerate(rows, start=1):
            parsed.append(
                {
                    **row,
                    "row_no": index,
                    "amount_decimal": str(self.normalize_amount(row.get("amount", "0"))),
                    "balance_decimal": str(self.normalize_amount(row.get("balance", "0"))),
                }
            )
        return parsed

    def parse_json_items(self, items: list[dict]) -> list[dict]:
        """Normalize document comparison items."""

        return [{**item, "normalized": True, "risk_level": item.get("risk_level", "low")} for item in items]

    @staticmethod
    def normalize_amount(value: object) -> Decimal:
        """Convert common amount strings to Decimal."""

        raw = str(value).replace(",", "").replace("¥", "").replace("+", "").strip()
        try:
            return Decimal(raw)
        except InvalidOperation:
            return Decimal("0")


class BusinessValidator:
    """Business validation helpers."""

    def validate_balance_sequence(self, rows: list[dict]) -> dict:
        """Validate simple bank-statement balance continuity."""

        issues = []
        previous_balance: Decimal | None = None
        for row in rows:
            amount = StructuredParser.normalize_amount(row.get("amount", 0))
            balance = StructuredParser.normalize_amount(row.get("balance", 0))
            if previous_balance is not None and previous_balance + amount != balance:
                issues.append(
                    {
                        "row_no": row.get("row_no"),
                        "type": "balance_gap",
                        "expected": str(previous_balance + amount),
                        "actual": str(balance),
                    }
                )
            previous_balance = balance
        return {"passed": not issues, "issues": issues}

    @staticmethod
    def classify_error_pages(pages: list[dict]) -> list[dict]:
        """Convert page issues into review records."""

        return [
            {
                "page": page["page"],
                "error_type": page.get("issues", []),
                "ignored": False,
                "need_review": page.get("need_review", False),
            }
            for page in pages
            if page.get("issues")
        ]


structured_parser = StructuredParser()
business_validator = BusinessValidator()
