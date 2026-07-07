# Open Agent Workbench

<p align="center">
  <img src="docs/assets/project-cover.svg" alt="Open Agent Workbench 项目封面" width="100%" />
</p>

<p align="center">
  <img alt="Backend" src="https://img.shields.io/badge/backend-FastAPI-0f766e" />
  <img alt="Frontend" src="https://img.shields.io/badge/frontend-Vue%203%20%2B%20TypeScript-2563eb" />
  <img alt="Runtime" src="https://img.shields.io/badge/runtime-local%20mock%20demo-7c3aed" />
  <img alt="Docker" src="https://img.shields.io/badge/docker-compose-334155" />
</p>

Open Agent Workbench 是一个**面向 SaaS 业务场景的后端 Agent 流程演示项目**。项目覆盖银行流水解析、制度文档比对、合同文档差异比对三个典型业务链路，重点展示后端任务编排、状态流转、结果复核、报告输出、脱敏兜底和本地化部署方式。

> 这个仓库的重点是后端业务流程和接口边界。前端只是用于触发接口、查看状态和演示结果的轻量工作台，不定位为完整商业产品 UI。

## 项目定位

- **后端优先**：以 FastAPI 服务、业务 service、agent workflow、配置文件和 Docker 部署为核心。
- **三类 Agent 场景**：银行流水解析、制度文档比对、合同文档差异比对。
- **本地可运行**：默认使用 mock 数据和本地适配器，不依赖外部私有服务。
- **公开仓库友好**：不包含真实业务数据、生产密钥、内部接口地址、数据库连接或私有 SDK。
- **便于二次开发**：保留清晰的 API 层、service 层、agent 层边界，后续可以替换为真实 OCR、模型网关、对象存储、队列和数据库。

## 效果预览

<p align="center">
  <img src="docs/assets/backend-architecture.svg" alt="后端架构图" width="100%" />
</p>

<p align="center">
  <img src="docs/assets/agent-workflows.svg" alt="三类 Agent 流程总览" width="100%" />
</p>

## 核心能力

| 模块 | 业务目标 | 已演示能力 |
| --- | --- | --- |
| 银行流水解析 | 对 PDF 流水进行结构化识别、复核和报告生成 | 完整 PDF 流程、单页识别、敏感词兜底、问题页标记、复核状态、报告详情 |
| 制度文档比对 | 将制度原文与规则库文档进行差异比对 | 完整文档比对、单文档比对、文本匹配兜底、高亮信息、风险摘要 |
| 合同文档差异比对 | 对标准合同和多个版本合同进行差异分析 | 创建比对任务、状态轮询、预览链接、本地行级 diff、历史记录 |
| 应用市场 | 统一展示可进入的业务流程 | 流程目录、分类筛选、收藏状态、入口跳转 |

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 后端服务 | FastAPI、Pydantic、Uvicorn |
| 后端依赖管理 | uv |
| 前端工作台 | Vue 3、TypeScript、Vite |
| 部署 | Docker、Docker Compose、Nginx |
| 配置 | TOML、`.env` |
| 数据 | 本地 mock 数据，无真实业务数据 |

## 快速开始

### 1. 克隆项目

```powershell
git clone https://github.com/Hezijie-shj/open-agent-workbench.git
cd open-agent-workbench
```

### 2. 启动后端

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

后端地址：

```text
http://localhost:8001
```

接口文档：

```text
http://localhost:8001/docs
```

### 3. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

前端地址：

```text
http://localhost:5173
```

### 4. 一键本地启动

Windows PowerShell 可以直接使用：

```powershell
.\start-dev.ps1
```

## Docker 部署

项目提供了可直接使用的 Docker Compose 配置。

```powershell
Copy-Item .env.example .env
docker compose --env-file .env up --build
```

启动后访问：

| 服务 | 地址 |
| --- | --- |
| 前端 | `http://localhost:5173` |
| 后端 | `http://localhost:8001` |
| API 文档 | `http://localhost:8001/docs` |

Docker 默认读取：

```text
config/config.toml
```

常用环境变量在 `.env` 中调整：

```text
FRONTEND_PORT=5173
BACKEND_PORT=8001
CONFIG_PATH=/app/config/config.toml
```

Compose 挂载目录：

| 本地目录 | 容器目录 | 说明 |
| --- | --- | --- |
| `./config` | `/app/config` | 只读配置 |
| `./data` | `/app/data` | 本地运行数据，不提交 |
| `./logs` | `/app/logs` | 运行日志，不提交 |

## 后端架构

```text
frontend views
  -> FastAPI endpoints
    -> service layer
      -> backend/app/agents/*
        -> mock data and local workflow adapters
```

后端保留了 SaaS Agent 项目中常见的分层方式：

- `api/endpoints`：对外暴露工作流动作、状态查询和结果接口。
- `services`：封装模块级业务入口，保持 API 层轻量。
- `agents`：承载具体业务流程，返回结构化 workflow、summary、detail。
- `mock_data.py`：提供公开演示数据。
- `config/*.toml`：统一管理运行配置。

更详细的后端流程说明见：[docs/backend-workflows.md](docs/backend-workflows.md)。

## 三个 Agent 流程

### 银行流水解析

主要路径：

```text
backend/app/agents/bank_statement/service.py
backend/app/api/endpoints/bank_statement.py
```

核心接口：

| 能力 | 接口 |
| --- | --- |
| 项目列表 | `GET /api/v1/bank_statement/projects` |
| 创建演示项目 | `POST /api/v1/bank_statement/projects/demo` |
| 完整 PDF 识别 | `GET /api/v1/bank_statement/projects/{project_id}/full-pdf-recognition` |
| 单页识别 | `GET /api/v1/bank_statement/projects/{project_id}/single-page-recognition?page=1` |
| 敏感词兜底 | `GET /api/v1/bank_statement/projects/{project_id}/sensitive-fallback?page=1` |
| 报告结果 | `GET /api/v1/bank_statement/projects/{project_id}/report` |
| 报告明细 | `GET /api/v1/bank_statement/projects/{project_id}/report/details?label=经营收入` |

流程摘要：

```text
上传流水 PDF
  -> 拆分页面
  -> 单页 OCR/结构化识别
  -> 敏感输出检测与兜底回填
  -> 合并交易明细
  -> 连续性和余额校验
  -> 人工复核
  -> 生成报告和明细
```

### 制度文档比对

主要路径：

```text
backend/app/agents/regulations/service.py
backend/app/api/endpoints/regulations.py
```

核心接口：

| 能力 | 接口 |
| --- | --- |
| 任务列表 | `GET /api/v1/regulations/tasks` |
| 创建任务 | `POST /api/v1/regulations/tasks` |
| 上传示例文档 | `POST /api/v1/regulations/tasks/{task_id}/upload-demo` |
| 完整文档比对 | `GET /api/v1/regulations/tasks/{task_id}/workflow` |
| 单文档比对 | `GET /api/v1/regulations/tasks/{task_id}/single-document-compare` |
| 文本匹配兜底 | `GET /api/v1/regulations/tasks/{task_id}/text-match-fallback` |
| 高亮匹配 | `GET /api/v1/regulations/tasks/{task_id}/matches` |

流程摘要：

```text
制度原文
  -> 读取规则库文档
  -> 提取 PDF/DOCX/TXT 文本
  -> 执行语义差异比对
  -> 标准化风险项
  -> 文本定位与高亮
  -> 截断/弱匹配兜底
  -> 输出风险摘要
```

### 合同文档差异比对

主要路径：

```text
backend/app/agents/document_diff/service.py
backend/app/api/endpoints/document_diff.py
```

核心接口：

| 能力 | 接口 |
| --- | --- |
| 历史记录 | `GET /api/v1/document_diff/history` |
| 创建演示任务 | `POST /api/v1/document_diff/history/demo` |
| 创建比对任务 | `POST /api/v1/document_diff/compare-documents` |
| 查询任务状态 | `GET /api/v1/document_diff/history/{task_id}/status` |
| 获取预览链接 | `GET /api/v1/document_diff/history/{task_id}/preview` |
| 本地行级 diff | `GET /api/v1/document_diff/history/{task_id}/local-line-diff` |
| 查看详情 | `GET /api/v1/document_diff/history/{task_id}` |

流程摘要：

```text
标准文档 + 多版本文档
  -> 创建比对任务
  -> 保存历史记录
  -> 轮询任务状态
  -> 获取差异详情
  -> 生成预览链接
  -> 本地行级 diff 兜底
  -> 输出条款差异
```

## 目录结构

```text
open-agent-workbench
├─ backend              FastAPI 后端
│  ├─ app/api           API 路由和 endpoints
│  ├─ app/services      模块业务入口
│  ├─ app/agents        三类 Agent 工作流
│  ├─ app/core          配置加载
│  └─ app/mock_data.py  本地演示数据
├─ frontend             Vue 3 + TypeScript 前端工作台
├─ config               TOML 运行配置
├─ docs                 后端流程文档和图片资源
├─ data                 本地运行数据，不提交
├─ logs                 本地运行日志，不提交
├─ docker-compose.yaml  Docker Compose 编排
└─ start-dev.ps1        本地开发启动脚本
```

## 配置说明

配置文件位于：

```text
config/config.toml
config/config.dev.toml
```

默认配置只启用本地 mock 工作流，不启用外部服务。后续如果要接入真实环境，可以按模块逐步替换：

- OCR 或 PDF 解析服务
- 模型网关
- 对象存储
- 消息队列
- 数据库
- 权限与租户系统

公开仓库中不要提交真实密钥、真实账号、内部域名、数据库连接、客户文件或运行日志。

## 开发检查

前端构建：

```powershell
cd frontend
npm run build
```

后端 lint：

```powershell
cd backend
$env:UV_CACHE_DIR = ".uv-cache"
uv run ruff check .
```

Docker 配置校验：

```powershell
docker compose --env-file .env.example config --quiet
```

公开发布前可以按自己的项目情况做关键词扫描，例如：

```powershell
rg -n "内部项目名|真实客户名|真实域名|本机绝对路径" -g "!frontend/node_modules/**" -g "!frontend/dist/**" -g "!backend/.uv-cache/**" .
```

## 公开发布边界

这个项目适合作为公开的后端流程 demo，但需要遵守以下边界：

- 只提交 mock 数据和演示文件名。
- 不提交真实流水、合同、制度文档、账号、客户名称或报告。
- 不提交 `.env`、日志、缓存、构建产物、虚拟环境和本地数据目录。
- 不提交内部接口地址、生产密钥、数据库连接和私有 SDK。
- README 和文档只描述公开可复用的业务流程，不描述内部系统细节。

## 路线图

- [ ] 增加真实文件上传的本地解析适配器示例。
- [ ] 增加 SQLite/PostgreSQL 持久化示例。
- [ ] 增加任务队列和异步 worker 示例。
- [ ] 增加更完整的前端状态流转和错误提示。
- [ ] 增加 API 自动化测试。

## License

当前仓库暂未声明开源 License。未获得明确授权前，请不要默认将其用于商业分发或二次发布。
