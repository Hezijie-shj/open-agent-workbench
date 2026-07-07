# Open Agent Workbench

一个用于演示智能工作流的独立 Web Demo, 聚焦三个通用场景:

- 流水文件解析与报告生成
- 制度文档差异比对
- 文档版本差异比对

项目包含一个 FastAPI 后端和一个 Vue 3 + TypeScript 前端。当前版本只使用虚构 mock 数据, 方便本地独立运行、演示页面链路和二次开发。

定位说明:

- 这是一个偏后端的 SaaS 业务流程方案 demo。
- 前端只是用于触发接口、查看状态和演示结果的轻量工作台, 不作为完整产品 UI。
- 后端重点展示三个 agent 的业务边界、流程状态、任务动作、兜底策略和公开版 adapter 结构。

更详细的后端流程说明见 [Backend Workflow Design](docs/backend-workflows.md)。

## 公开说明

- 仓库不包含生产密钥、数据库连接、内部接口地址或真实业务数据。
- 前端展示内容、公司名称、账号、文件名和交易记录均为虚构样例。
- `node_modules/`、`dist/`、日志和 Python 缓存目录已通过 `.gitignore` 排除。

## 启动后端

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 启动前端

```powershell
cd frontend
npm install
npm run dev
```

默认前端地址:

```text
http://localhost:5173
```

默认后端地址:

```text
http://localhost:8001
```

## 一键本地启动

```powershell
.\start-dev.ps1
```

## Docker 启动

```powershell
Copy-Item .env.example .env
docker compose --env-file .env up --build
```

Docker 启动后:

```text
前端: http://localhost:5173
后端: http://localhost:8001
接口文档: http://localhost:8001/docs
```

Docker 使用的默认配置文件是 `config/config.toml`。常用端口和配置路径在 `.env` 中修改:

```text
FRONTEND_PORT=5173
BACKEND_PORT=8001
CONFIG_PATH=/app/config/config.toml
```

Compose 会挂载这些目录:

```text
./config -> /app/config  只读配置
./data   -> /app/data    本地数据目录
./logs   -> /app/logs    日志目录
```

本地开发使用 `config/config.dev.toml`; 一键脚本会自动把它传给后端。

## 目录结构

```text
open-agent-workbench
├─ backend              FastAPI 后端
├─ frontend             Vue 3 + TypeScript 前端
├─ config               运行配置
├─ docs                 后端流程说明
├─ data                 本地运行数据, 不提交
├─ logs                 本地运行日志, 不提交
├─ docker-compose.yaml  Docker 编排
└─ start-dev.ps1        本地开发启动脚本
```
