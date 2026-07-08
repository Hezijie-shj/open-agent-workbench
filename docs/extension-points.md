# Extension Points

Open Agent Workbench 把文件处理、OCR、模型任务、存储、队列、审计和报告生成拆成了一组 adapter。这样做的目的是让 demo 保持轻量，同时保留后续接入不同基础设施的清晰边界。

## Adapter Overview

| Adapter | 默认实现 | 可替换方向 |
| --- | --- | --- |
| 文件处理 | `backend/app/platform/file_pipeline.py` | 上传服务、压缩包解析、PDF 拆页、页面渲染 |
| OCR | `backend/app/platform/ocr.py` | OCR 引擎、版面分析、坐标映射、文本清洗 |
| 模型任务 | `backend/app/platform/model_gateway.py` | LLM 网关、提示词模板、重试策略、结构化输出 |
| 解析校验 | `backend/app/platform/parsers.py` | CSV/JSON 解析、字段归一化、金额和规则校验 |
| 任务状态 | `backend/app/platform/repository.py` | 数据库、事务、分页筛选、状态机、复核记录 |
| 异步处理 | `backend/app/platform/queue.py` | 队列、worker、重试、延迟任务 |
| 文件存储 | `backend/app/platform/storage.py` | 对象存储、文件元数据、checksum、访问链接 |
| 审计计数 | `backend/app/platform/audit.py` | 租户上下文、审计日志、调用计数、计量统计 |
| 报告输出 | `backend/app/platform/reporting.py` | JSON、DOCX、PDF、模板渲染、下载链接 |

## Prompt Templates

当前 demo 在 `model_gateway.py` 中只保留任务名称和结构化输入输出形态。实际接入模型时，可以按模块增加提示词模板目录，例如：

```text
backend/app/prompts/
├─ statement/
│  ├─ page_to_rows.md
│  ├─ continuity_check.md
│  └─ fallback_repair.md
├─ rules/
│  ├─ compare_document.md
│  ├─ normalize_risks.md
│  └─ locate_matches.md
└─ contract/
   ├─ compare_versions.md
   ├─ summarize_changes.md
   └─ local_diff_explain.md
```

建议把 prompt 写成面向输入 schema 和输出 schema 的模板，而不是把业务代码写进 prompt。这样便于测试、替换模型和控制版本。

## OCR Layout

当前 OCR adapter 返回统一的文本块结构：

```text
block_id
text
bbox
confidence
type
```

后续可以拆成更细的模块：

```text
backend/app/ocr/
├─ engines/
├─ layout.py
├─ coordinate_mapper.py
├─ text_cleaner.py
└─ schema.py
```

上层 workflow 只依赖统一的 blocks 结构，因此 OCR 引擎可以独立替换。

## File Pipeline

文件类任务统一走下面的抽象流程：

```text
upload
  -> metadata
  -> optional archive extraction
  -> page or paragraph extraction
  -> parser
  -> validator
  -> workflow result
```

不同模块只需要定义自己的解析策略和校验策略：

- 账单 PDF：更关注页码、坐标、金额和余额连续性。
- 规则文本：更关注段落、条款、风险项和高亮定位。
- 版本差异：更关注文档角色、版本差异和行级 diff。

## Persistence

默认 repository 是内存实现，便于本地启动和 demo 演示。替换成数据库时建议保持这些概念：

- task record
- task status
- current step
- progress
- payload
- review records
- audit events

## Report Output

默认报告层只返回元数据和下载地址描述：

```text
json
docx
pdf
```

接入真实模板渲染时，可以让 `reporting.py` 调用模板引擎或文档生成服务。上层 agent 不需要关心具体生成方式。

## Design Principle

这个项目的核心不是绑定某个具体基础设施，而是展示一套可替换的后端 workflow 边界：

```text
workflow stays stable
adapter can change
response shape remains predictable
```
