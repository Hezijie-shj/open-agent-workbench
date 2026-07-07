# 配置说明

当前系统是独立演示版, 默认使用虚构 mock 数据。

- `config.toml`: Docker 默认配置, 适合下载仓库后直接运行。
- `config.dev.toml`: 本地开发配置, `start-dev.ps1` 会使用这个文件。
- `.env.example`: Docker Compose 环境变量样例, 复制为 `.env` 后可改端口和配置路径。

常用字段:

- `app.api_prefix`: 后端 API 前缀, 默认 `/api/v1`。
- `app.cors_origins`: 本地开发允许访问后端的前端地址。
- `bank_statement.mode = "mock"`: 流水分析使用本地模拟数据。
- `regulations.mode = "mock"`: 规章制度使用本地模拟数据。
- `document_diff.mode = "mock"`: 文档差异比对使用本地模拟数据。
- `features.enable_external_services = false`: 默认不启用任何外部私有服务。
- `storage.data_dir` / `storage.log_dir`: 容器内数据和日志目录, Compose 会挂载到宿主机 `./data` 和 `./logs`。

后续接入真实业务时, 可以继续在这里补数据库、文件存储、解析服务和 worker 配置。不要把生产密钥、内部地址、真实账号或真实业务数据提交到公开仓库。
