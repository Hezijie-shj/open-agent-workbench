"""Model gateway simulation with prompt, retry, and fallback metadata."""


class ModelGateway:
    """Deterministic model adapter used by public demos."""

    blocked_words = {"真实身份证", "真实账号", "真实客户"}

    def run_structured_task(self, module: str, prompt_name: str, payload: dict, max_retries: int = 2) -> dict:
        """Run a local structured task with retry metadata."""

        attempt_logs = []
        for attempt in range(1, max_retries + 1):
            attempt_logs.append({"attempt": attempt, "status": "success" if attempt == 1 else "skipped"})
            break
        return {
            "module": module,
            "prompt_name": prompt_name,
            "status": "completed",
            "attempts": attempt_logs,
            "input_shape": sorted(payload.keys()),
            "output_format": "structured_json",
        }

    def guard_sensitive_output(self, rows: list[dict], fields: list[str]) -> dict:
        """Return id-only placeholders if demo sensitive text is detected."""

        should_fallback = any(
            any(word in str(row.get(field, "")) for word in self.blocked_words) for row in rows for field in fields
        )
        return {
            "used": should_fallback,
            "strategy": "id_reference_output" if should_fallback else "direct_output",
            "safe_rows": [
                {
                    "id": row.get("id"),
                    **{f"{field}_ref": f"{row.get('id')}-{field}" for field in fields},
                }
                for row in rows
            ]
            if should_fallback
            else [],
        }


model_gateway = ModelGateway()
