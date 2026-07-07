"""应用配置."""

import os
import tomllib
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """应用基础配置."""

    app_name: str = "open-agent-workbench"
    version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    environment: str = "demo"
    log_level: str = "info"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    bank_statement_mode: str = Field(default="mock")
    regulations_mode: str = Field(default="mock")
    document_diff_mode: str = Field(default="mock")


def load_settings() -> Settings:
    """加载应用配置.

    :return: 应用配置.
    :rtype: Settings
    """
    config_path = Path(os.getenv("CONFIG_PATH") or os.getenv("config_path", "config/config.dev.toml"))
    if not config_path.exists():
        return Settings()

    with config_path.open("rb") as file:
        data = tomllib.load(file)

    app_config = data.get("app", {})
    bank_statement_config = data.get("bank_statement", {})
    regulations_config = data.get("regulations", {})
    document_diff_config = data.get("document_diff", {})
    return Settings(
        app_name=app_config.get("name", "open-agent-workbench"),
        version=app_config.get("version", "0.1.0"),
        api_prefix=app_config.get("api_prefix", "/api/v1"),
        environment=app_config.get("environment", os.getenv("APP_ENV", "demo")),
        log_level=app_config.get("log_level", os.getenv("LOG_LEVEL", "info")),
        cors_origins=app_config.get("cors_origins", ["http://localhost:5173", "http://127.0.0.1:5173"]),
        bank_statement_mode=bank_statement_config.get("mode", "mock"),
        regulations_mode=regulations_config.get("mode", "mock"),
        document_diff_mode=document_diff_config.get("mode", "mock"),
    )


settings = load_settings()
