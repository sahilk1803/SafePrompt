export type AssessmentType = 'APPROVED' | 'CAUTION' | 'NEEDS_REVIEW' | 'BLOCKED' | 'NOT_APPROVED';

export interface EthicalValueScore {
  value: string;
  score: number;
  status: string;
  explanation: string;
}

export interface FindingDetail {
  category: string;
  severity: string;
  description: string;
  matched_text?: string;
  start?: number;
  end?: number;
  source?: string;
}

export interface CategoryAssessment {
  category: string;
  label: string;
  severity: string;
  source: string;
}

export interface AnalyzeResponse {
  analysis_id: string;
  overall_decision: AssessmentType;
  assessment: AssessmentType;
  risk_score: number;
  confidence: number;
  uncertainty_level: string;
  uncertainty_notice: string;
  analysis_mode: 'local' | 'semantic' | 'hybrid' | string;
  reduced_semantic_coverage: boolean;
  intent: string;
  authorization_indicator: string;
  categories: string[];
  detected_categories: CategoryAssessment[];
  category_severities: Record<string, string>;
  evidence_snippets: string[];
  explanation: string;
  relevant_ethical_principles: string[];
  relevant_values: EthicalValueScore[];
  findings: FindingDetail[];
  suggested_rewrite: string;
  recommended_safer_alternative: string;
  has_pii: boolean;
  is_educational: boolean;
  instruction_conflict: boolean;
  model_version: string;
  policy_version: string;
  scoring_methodology: string;
  latency_ms: number;
}

export interface RedactResponse {
  original_text: string;
  sanitized_text: string;
  detected_count: number;
  entity_map: Record<string, string>;
  findings: Array<{
    entity_type: string;
    label: string;
    severity: string;
    matched_text: string;
    start: number;
    end: number;
  }>;
}

export interface RewriteResponse {
  original_prompt: string;
  rewritten_prompt: string;
  strategy: string;
  diff_html: string;
  modifications: string[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  assessment?: AssessmentType;
  timestamp: string;
  safety_notes?: string;
}

export interface DashboardResponse {
  total_prompts: number;
  approved_count: number;
  caution_count: number;
  needs_review_count: number;
  not_approved_count: number;
  pii_detections: number;
  avg_latency_ms: number;
  recent_activity: Array<{
    id: string;
    timestamp: string;
    snippet: string;
    assessment: AssessmentType;
    risk_score: number;
    categories: string[];
    policy_version: string;
  }>;
  category_distribution: Record<string, number>;
  demo_mode: boolean;
}

export interface EvaluationRunResponse {
  total_samples: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  category_metrics: Record<string, { total: number; correct: number; accuracy: number }>;
  confusion_matrix: {
    true_positives: number;
    false_positives: number;
    true_negatives: number;
    false_negatives: number;
  };
  error_count: number;
  errors: Array<{
    id: number;
    prompt: string;
    expected: string;
    predicted: string;
    category: string;
  }>;
  report_timestamp: string;
}

export interface SustainabilityMetrics {
  total_requests: number;
  estimated_tokens: number;
  estimated_energy_kwh: number;
  estimated_carbon_gco2e: number;
  estimated_water_ml: number;
  region: string;
  grid_intensity: number;
  green_tips: Array<{ title: string; text: string }>;
  historical_usage: Array<{ hour: string; requests: number; tokens: number; energy_wh: number }>;
  assumptions_disclaimer: string;
}

export interface ScenarioDetail {
  id: string;
  title: string;
  domain: string;
  summary: string;
  stakeholders: Array<{
    group: string;
    well_being: string;
    autonomy: string;
    justice: string;
  }>;
  framework_perspectives: {
    consequentialism: string;
    deontology: string;
    virtue_ethics: string;
    social_contract: string;
  };
  trade_off_analysis: string;
}
