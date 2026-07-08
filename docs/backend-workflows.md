# Workflow Notes

这份文档记录 Open Agent Workbench 的后端 workflow 设计。它不是完整业务系统说明书，而是一个本地可运行的工程骨架：用 mock 数据模拟文件处理、模型调用、任务状态、复核和报告输出。

## 总体结构

```text
frontend
  -> api endpoints
    -> services
      -> agents
        -> platform adapters
          -> mock data
```

核心约定：

- `api/endpoints` 负责暴露 HTTP 接口。
- `services` 负责模块级业务入口。
- `agents` 负责编排具体 workflow。
- `platform` 模拟文件、OCR、模型、存储、队列、仓储、审计和报告等基础设施。
- `mock_data.py` 提供公开演示数据。

## Platform Adapters

| Adapter | 说明 |
| --- | --- |
| `file_pipeline.py` | 上传元数据、压缩包展开、PDF 拆页、页面渲染、页面分类 |
| `ocr.py` | OCR 文本块、坐标框、置信度、文本清洗 |
| `model_gateway.py` | 模型任务名称、重试记录、结构化输出和兜底策略 |
| `parsers.py` | CSV/JSON 解析、字段标准化、金额校验 |
| `repository.py` | 内存状态机、事务回滚、分页筛选、复核记录 |
| `queue.py` | 本地队列和 worker 行为模拟 |
| `storage.py` | 对象 key、checksum、content type 等元数据 |
| `audit.py` | 审计日志、租户上下文、调用计数 |
| `reporting.py` | 报告模板描述和下载地址描述 |

这些 adapter 默认不连接外部服务。实际项目中可以保留上层接口和 workflow，只替换 adapter 实现。

## Workflow A: Statement PDF

接口入口：

```text
POST /api/v1/bank_statement/projects/{project_id}/engineering-pipeline
```

流程：

```text
upload file
  -> object metadata
  -> archive extraction
  -> PDF pages
  -> page images
  -> OCR blocks
  -> structured rows
  -> amount checks
  -> fallback handling
  -> task state
  -> review record
  -> report metadata
```

辅助接口：

```text
POST /api/v1/bank_statement/projects/upload-task
GET  /api/v1/bank_statement/projects/{project_id}/single-page-recognition
GET  /api/v1/bank_statement/projects/{project_id}/sensitive-fallback
GET  /api/v1/bank_statement/workflow-tasks
GET  /api/v1/bank_statement/review-records
GET  /api/v1/bank_statement/audit-summary
```

## Workflow B: Rule Document Compare

接口入口：

```text
POST /api/v1/regulations/tasks/{task_id}/engineering-pipeline
```

流程：

```text
upload source document
  -> load local rule files
  -> extract paragraphs
  -> semantic compare
  -> normalize risk items
  -> locate matched text
  -> fallback search
  -> task state
  -> review record
  -> report metadata
```

辅助接口：

```text
POST /api/v1/regulations/tasks/upload-task
GET  /api/v1/regulations/tasks/{task_id}/workflow
GET  /api/v1/regulations/tasks/{task_id}/single-document-compare
GET  /api/v1/regulations/tasks/{task_id}/text-match-fallback
GET  /api/v1/regulations/workflow-tasks
GET  /api/v1/regulations/review-records
GET  /api/v1/regulations/audit-summary
```

## Workflow C: Contract Version Diff

接口入口：

```text
POST /api/v1/document_diff/engineering-pipeline
```

流程：

```text
upload standard and compare docs
  -> validate file roles
  -> extract text
  -> create compare task
  -> queue status polling
  -> sync result
  -> preview link
  -> local line diff
  -> task state
  -> review record
  -> report metadata
```

辅助接口：

```text
POST /api/v1/document_diff/history/upload-task
GET  /api/v1/document_diff/history/{task_id}/status
GET  /api/v1/document_diff/history/{task_id}/preview
GET  /api/v1/document_diff/history/{task_id}/local-line-diff
GET  /api/v1/document_diff/workflow-tasks
GET  /api/v1/document_diff/review-records
GET  /api/v1/document_diff/audit-summary
```

## Public Demo Boundary

- 使用 mock 数据，不提交真实文件。
- 使用本地内存状态，不依赖数据库。
- 使用本地 adapter，不依赖外部 OCR、模型、对象存储或队列。
- 返回结构化 workflow，便于前端展示和后续替换。
- 真实部署时建议从 `platform` 层开始替换实现。
