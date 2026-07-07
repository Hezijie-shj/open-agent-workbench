const API_PREFIX = "/api/v1";

export interface AgentCard {
  id: number;
  name: string;
  description: string;
  department: string;
  scene: string;
  views: number;
  favorites: number;
  likes: number;
  route: string;
}

export interface ProjectItem {
  id: number;
  name: string;
  date_range: string;
  amount: string;
  created_at: string;
  creator: string;
  status: string;
}

export interface TransactionItem {
  id: number;
  date: string;
  type: string;
  amount: string;
  balance: string;
  source_ids?: string[];
  bbox?: [number, number, number, number];
  confidence?: number;
  issue?: string;
  counterparty?: string;
}

export interface RegulationTask {
  id: number;
  name: string;
  standard: string;
  uploaded_at: string;
  status: string;
  risk_count: number;
  summary: string;
}

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_PREFIX}${url}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });
  if (!response.ok) {
    throw new Error(`request failed: ${response.status}`);
  }
  const result = await response.json();
  return result.data as T;
}

export function getAgents() {
  return request<AgentCard[]>("/market/agents");
}

export function getProjects() {
  return request<{ items: ProjectItem[]; total: number }>("/bank_statement/projects");
}

export function createDemoProject() {
  return request<ProjectItem>("/bank_statement/projects/demo", { method: "POST" });
}

export function reviewProject(projectId: number) {
  return request<ProjectItem>(`/bank_statement/projects/${projectId}/reviewed`, { method: "POST" });
}

export function removeProject(projectId: number) {
  return request<ProjectItem>(`/bank_statement/projects/${projectId}`, { method: "DELETE" });
}

export function getAnalysisResult(projectId: string, page = 1) {
  return request<{ project: ProjectItem; file_name: string; page: number; total_pages: number; items: TransactionItem[] }>(
    `/bank_statement/projects/${projectId}/analysis-result?page=${page}`
  );
}

export function getFullPdfRecognition(projectId: string) {
  return request<any>(`/bank_statement/projects/${projectId}/full-pdf-recognition`);
}

export function getSinglePageRecognition(projectId: string, page = 1) {
  return request<any>(`/bank_statement/projects/${projectId}/single-page-recognition?page=${page}`);
}

export function getSensitiveFallback(projectId: string, page = 1) {
  return request<any>(`/bank_statement/projects/${projectId}/sensitive-fallback?page=${page}`);
}

export function getReport(projectId: string) {
  return request<any>(`/bank_statement/projects/${projectId}/report`);
}

export function getReportDetails(projectId: string, label: string) {
  return request<any[]>(`/bank_statement/projects/${projectId}/report/details?label=${encodeURIComponent(label)}`);
}

export function getRegulationTasks() {
  return request<{ items: RegulationTask[]; total: number }>("/regulations/tasks");
}

export function getRegulationTask(taskId: number) {
  return request<any>(`/regulations/tasks/${taskId}`);
}

export function getRegulationMatches(taskId: number) {
  return request<any>(`/regulations/tasks/${taskId}/matches`);
}

export function getRegulationWorkflow(taskId: number) {
  return request<any>(`/regulations/tasks/${taskId}/workflow`);
}

export function getRegulationSingleDocumentCompare(taskId: number, compareFile = "rule-library-demo.pdf") {
  return request<any>(`/regulations/tasks/${taskId}/single-document-compare?compare_file=${encodeURIComponent(compareFile)}`);
}

export function getRegulationTextMatchFallback(taskId: number) {
  return request<any>(`/regulations/tasks/${taskId}/text-match-fallback`);
}

export function createRegulationTask() {
  return request<RegulationTask>("/regulations/tasks/demo", { method: "POST" });
}

export function uploadRegulationDemo() {
  return request<RegulationTask>("/regulations/tasks/upload-demo", { method: "POST" });
}

export function getDocumentDiffHistory() {
  return request<{ items: any[]; total: number }>("/document_diff/history");
}

export function getDocumentDiffDetail(taskId: string) {
  return request<any>(`/document_diff/history/${taskId}`);
}

export function createDocumentDiffDemo() {
  return request<any>("/document_diff/history/demo", { method: "POST" });
}

export function compareDocumentDiffDemo() {
  return request<any>("/document_diff/compare-documents", { method: "POST" });
}

export function getDocumentDiffStatus(taskId: string) {
  return request<any>(`/document_diff/history/${taskId}/status`);
}

export function getDocumentDiffPreview(taskId: string) {
  return request<any>(`/document_diff/history/${taskId}/preview`);
}

export function getDocumentDiffLocalLineDiff(taskId: string) {
  return request<any>(`/document_diff/history/${taskId}/local-line-diff`);
}
