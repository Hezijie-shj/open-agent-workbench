# Backend Workflow Design

This project is a backend-oriented SaaS workflow demo. The frontend is intentionally lightweight: it exists to trigger APIs, display state changes, and make the backend workflow easy to inspect. The core value is in the backend service boundaries, workflow states, and public-safe adapter design.

All data is mock data. The repository does not include external SDKs, real storage, queues, databases, credentials, internal endpoints, or business records.

## Architecture

```text
frontend views
  -> FastAPI endpoints
    -> service layer
      -> backend/app/agents/*
        -> mock data and local workflow adapters
```

The backend keeps the same kind of layering used in a SaaS agent system:

- API endpoints expose workflow actions and status queries.
- Services provide module-level business methods.
- Agents hold the business workflow and return structured results.
- Configuration lives under `config/*.toml`.

## Agent 1: Bank Statement Analysis

Module path:

```text
backend/app/agents/bank_statement/service.py
backend/app/api/endpoints/bank_statement.py
```

This agent models a bank-statement SaaS workflow: upload, full PDF recognition, single-page recognition, review, report generation, report details, and sensitive-output fallback.

### Full PDF Flow

Endpoint:

```text
GET /api/v1/bank_statement/projects/{project_id}/full-pdf-recognition
```

Flow:

```text
PDF input
  -> split PDF pages
  -> run single-page recognition for each page
  -> merge recognized rows
  -> mark empty/error pages
  -> run continuity and balance checks
  -> return page summary and row count
```

Public demo behavior:

- Uses mock page data.
- Returns workflow steps with `completed`, `empty`, and fallback flags.
- Does not call external OCR, model gateways, object storage, queues, or databases.

### Single Page Flow

Endpoint:

```text
GET /api/v1/bank_statement/projects/{project_id}/single-page-recognition?page=1
```

Flow:

```text
PDF page
  -> render target page image
  -> extract OCR text blocks
  -> generate structured CSV-style rows
  -> detect sensitive-output interruption risk
  -> backfill text from local OCR block references
  -> bind source ids and bounding boxes
  -> return structured rows for frontend review
```

Returned fields include page metadata, transaction rows, source ids, bounding boxes, confidence, issue flags, and fallback status.

### Sensitive Output Fallback

Endpoint:

```text
GET /api/v1/bank_statement/projects/{project_id}/sensitive-fallback?page=1
```

Flow:

```text
sensitive field risk
  -> output block references instead of sensitive text
  -> recover text locally from OCR block mapping
  -> preserve source traceability
  -> return safe intermediate output and recovered row count
```

The public version demonstrates the strategy without real sensitive content.

### Review And Report

Endpoints:

```text
POST   /api/v1/bank_statement/projects/demo
POST   /api/v1/bank_statement/projects/{project_id}/reviewed
DELETE /api/v1/bank_statement/projects/{project_id}
GET    /api/v1/bank_statement/projects/{project_id}/report
GET    /api/v1/bank_statement/projects/{project_id}/report/details?label=...
```

These endpoints support task creation, review state changes, deletion, report overview, and drawer-style transaction details.

## Agent 2: Regulation Document Comparison

Module path:

```text
backend/app/agents/regulations/service.py
backend/app/api/endpoints/regulations.py
```

This agent models a regulation/policy comparison workflow: source document loading, knowledge-base comparison documents, task creation, document comparison, result persistence, text matching, and highlight fallback.

### Full Regulation Compare Flow

Endpoint:

```text
GET /api/v1/regulations/tasks/{task_id}/workflow
```

Flow:

```text
source regulation document
  -> download or load source file
  -> load comparison documents from knowledge base
  -> create comparison task record
  -> extract PDF/DOCX/TXT text
  -> compare each document
  -> normalize risk items and clause differences
  -> save comparison result
  -> generate highlight metadata
```

Public demo behavior:

- Uses local mock documents and mock comparison results.
- Keeps a real-world-style workflow and response shape.
- Excludes knowledge-base APIs, object storage, and external comparison services.

### Single Document Compare Flow

Endpoint:

```text
GET /api/v1/regulations/tasks/{task_id}/single-document-compare?compare_file=rule-library-demo.pdf
```

Flow:

```text
one source document
  -> one comparison document
  -> extract both texts
  -> semantic comparison
  -> normalize clause, risk level, and suggestion
```

This mirrors the single compare unit used inside the full workflow.

### Text Match And Truncation Fallback

Endpoint:

```text
GET /api/v1/regulations/tasks/{task_id}/text-match-fallback
```

Flow:

```text
target text
  -> extract document paragraphs
  -> run fast similarity recall
  -> return perfect match when available
  -> otherwise return highest-similarity paragraph
  -> extend truncated cross-paragraph match
  -> generate page or paragraph highlight metadata
```

This demonstrates how the backend handles weak matches and truncated text snippets before the frontend renders highlights.

## Agent 3: Document Difference

Module path:

```text
backend/app/agents/document_diff/service.py
backend/app/api/endpoints/document_diff.py
```

This agent models a document-diff workflow: create comparison task, save history, poll task status, request preview authorization, load diff detail, and run a local line-level fallback diff.

### Create Comparison Task

Endpoint:

```text
POST /api/v1/document_diff/compare-documents
```

Flow:

```text
standard document and comparison documents
  -> validate file metadata
  -> create comparison task
  -> save history record
  -> return task id and processing state
```

The public version creates an in-memory mock task.

### Status Polling

Endpoint:

```text
GET /api/v1/document_diff/history/{task_id}/status
```

Flow:

```text
task id
  -> query task status
  -> sync history state
  -> load diff detail when completed
```

This mirrors asynchronous SaaS task polling without requiring a real worker or external comparator.

### Preview Authorization

Endpoint:

```text
GET /api/v1/document_diff/history/{task_id}/preview
```

Flow:

```text
task id
  -> request preview grant
  -> build preview URL
```

The demo returns a local preview URL shape.

### Local Line Diff

Endpoint:

```text
GET /api/v1/document_diff/history/{task_id}/local-line-diff
```

Flow:

```text
left document text
  -> right document text
  -> line-level diff
  -> similarity score
  -> added/deleted line counts
```

This is the public-safe local fallback for inspecting document differences without external services.

## Public Release Boundary

This repository is suitable as a public backend workflow demo if these boundaries are kept:

- Keep all data as mock/sample data.
- Do not commit real files, real accounts, private URLs, keys, credentials, or logs.
- Keep `.env`, `logs/`, `data/`, `dist/`, `node_modules/`, `.venv/`, Python caches, and local tool caches ignored.
- Treat the frontend as an operational demo surface, not a polished product UI.
- Replace mock adapters with real storage, queues, OCR, model gateway, and database only in controlled deployments.
