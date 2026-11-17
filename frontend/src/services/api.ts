import {
  AnalyzeResponse,
  RedactResponse,
  RewriteResponse,
  DashboardResponse,
  EvaluationRunResponse,
  SustainabilityMetrics,
  ScenarioDetail
} from '../types';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {})
    }
  });
  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`API Error (${response.status}): ${errText}`);
  }
  return response.json();
}

export const api = {
  getHealth: () => fetchJson<{
    status: string;
    app: string;
    version: string;
    course: string;
    institution: string;
    demo_mode: boolean;
    active_model?: string;
    semantic_classifier_available?: boolean;
    semantic_status?: string;
    analysis_mode_default?: string;
  }>('/health'),

  analyzePrompt: (prompt: string) =>
    fetchJson<AnalyzeResponse>('/analyze', {
      method: 'POST',
      body: JSON.stringify({ prompt, user_id: 'student_user' })
    }),

  redactPii: (text: string, mode: string = 'placeholder') =>
    fetchJson<RedactResponse>('/redact', {
      method: 'POST',
      body: JSON.stringify({ text, mode })
    }),

  rewritePrompt: (prompt: string) =>
    fetchJson<RewriteResponse>('/rewrite', {
      method: 'POST',
      body: JSON.stringify({ prompt })
    }),

  chat: (message: string, bypassApproval: boolean = false) =>
    fetchJson<{ reply: string; assessment: string; is_demo_mode: boolean; model_name: string; latency_ms: number; safety_notes?: string }>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, history: [], bypass_approval: bypassApproval })
    }),

  getDashboard: () => fetchJson<DashboardResponse>('/dashboard'),

  getAudit: (limit: number = 50) =>
    fetchJson<{ count: number; records: any[]; data_minimization_notice: string }>(`/audit?limit=${limit}`),

  runEvaluation: () =>
    fetchJson<EvaluationRunResponse>('/evaluate', {
      method: 'POST'
    }),

  getEvaluationCsv: () => fetchJson<{ filename: string; csv: string }>('/evaluate/dataset'),

  getSustainability: (region: string = 'India (National Avg)') =>
    fetchJson<SustainabilityMetrics>(`/sustainability?region=${encodeURIComponent(region)}`),

  getScenarios: () => fetchJson<ScenarioDetail[]>('/scenarios'),

  getSocietal: () => fetchJson<{ topics: any[]; educational_cards: any[] }>('/societal'),

  getSyllabus: () => fetchJson<{ course: string; course_name: string; institution: string; units: any[] }>('/syllabus'),

  submitReview: (analysisId: string, reviewer: string, outcome: string, comments: string) =>
    fetchJson('/reviews', {
      method: 'POST',
      body: JSON.stringify({ analysis_id: analysisId, reviewer, outcome, comments })
    })
};
