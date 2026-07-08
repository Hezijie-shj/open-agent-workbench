# Public Scope

这个仓库是一个公开可运行的后端 Agent workflow demo，不是完整私有业务系统的开源版。

项目保留的是通用后端工程形态：API、service、agent workflow、adapter 边界、mock 数据、任务状态、复核记录、审计计数和报告描述。项目没有放入会暴露具体业务实现或私有依赖的内容。

## 没有放入仓库的内容

| 类别 | 公开版处理 |
| --- | --- |
| 真实提示词 | 只保留 prompt 名称和结构化任务说明，不提交实际业务 prompt |
| OCR 供应商目录 | 使用 `backend/app/platform/ocr.py` 的 mock adapter 代替 |
| OCR 私有参数 | 不提交供应商账号、模型名、版面参数、识别阈值和重试策略 |
| PDF 真实解析细节 | 用 `file_pipeline.py` 模拟上传、拆页、渲染、空白页识别 |
| 模型网关调用 | 用 `model_gateway.py` 模拟任务调用、重试和兜底元数据 |
| 私有 SDK | 不提交任何公司或供应商私有 SDK |
| 数据库模型 | 使用内存 repository 模拟状态机、分页、筛选、复核记录 |
| 任务队列 | 使用本地 queue 模拟异步任务和 worker 行为 |
| 对象存储 | 使用本地 object metadata 模拟文件 key、checksum、content type |
| 报告模板 | 只返回报告元数据和下载地址描述，不提交真实 docx/pdf 模板 |
| 业务规则细节 | 只保留通用校验示例，不提交真实规则、黑名单、白名单或客户规则 |
| 真实文件样本 | 只使用 mock 数据和演示文件名 |
| 运行凭据 | 不提交 `.env`、密钥、账号、非公开地址、数据库连接或日志 |

## 为什么这样处理

提示词、OCR 目录、供应商适配、字段规则、异常分支、报告模板和真实样本，通常会体现一个私有系统的具体实现方式。公开仓库更适合展示可复用的工程边界，而不是公开具体业务资产。

因此这个项目采用下面的公开版替代方式：

```text
真实提示词        -> prompt_name + mock structured task
真实 OCR 服务     -> local OCR adapter
真实 PDF 解析     -> file pipeline simulator
真实数据库        -> in-memory repository
真实任务队列      -> local queue simulator
真实对象存储      -> object metadata simulator
真实报告模板      -> report descriptor
真实业务规则      -> generic validation examples
```

## 私有部署时建议补充的位置

如果要把这个 demo 改造成真实业务系统，建议优先替换 `backend/app/platform` 下的 adapter。

| 目标 | 建议替换位置 |
| --- | --- |
| OCR 接入 | `backend/app/platform/ocr.py` |
| PDF 渲染和拆页 | `backend/app/platform/file_pipeline.py` |
| 模型网关 | `backend/app/platform/model_gateway.py` |
| 数据库 | `backend/app/platform/repository.py` |
| 队列 / worker | `backend/app/platform/queue.py` |
| 对象存储 | `backend/app/platform/storage.py` |
| 报告生成 | `backend/app/platform/reporting.py` |
| 审计和计费 | `backend/app/platform/audit.py` |

可以新增私有目录，例如：

```text
backend/app/private_adapters/
backend/app/prompts_private/
backend/app/report_templates/
```

这些目录应当保留在私有仓库中，不建议提交到公开仓库。

## 当前公开版保留了什么

- 三类 Agent 的 API 入口。
- 工作流状态和步骤返回。
- 文件类任务的上传、解析、校验、复核和报告链路。
- 多租户上下文、审计日志和调用计数的占位实现。
- Docker Compose 本地部署。
- 前端轻量工作台。
- 方便替换为真实服务的 adapter 分层。

## 结论

这个仓库适合作为公开的后端 workflow demo。它展示的是架构、接口和流程边界；不包含真实提示词、真实 OCR 目录、真实业务规则或私有服务实现。
