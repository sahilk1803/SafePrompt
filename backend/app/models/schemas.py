from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    prompt: str = Field(..., max_length=10000, description="The user prompt to analyze")
    user_id: Optional[str] = "student_demo"

class FindingDetail(BaseModel):
    category: str
    severity: str
    description: str
    matched_text: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    source: Optional[str] = "local"

class CategoryAssessment(BaseModel):
    category: str
    label: str
    severity: str
    source: str

class EthicalValueScore(BaseModel):
    value: str
    score: int
    status: str
    explanation: str

class AnalyzeResponse(BaseModel):
    # Canonical v2 structured response fields
    analysis_id: str
    overall_decision: str  # APPROVED, CAUTION, NEEDS_REVIEW, BLOCKED
    risk_score: float  # 0 to 100
    confidence: float  # 0.0 to 1.0
    uncertainty_level: str  # low, moderate, high
    uncertainty_notice: str
    analysis_mode: str  # local, semantic, hybrid
    reduced_semantic_coverage: bool
    intent: str
    authorization_indicator: str
    detected_categories: List[CategoryAssessment]
    category_severities: Dict[str, str]
    evidence_snippets: List[str]
    relevant_ethical_principles: List[str]
    recommended_safer_alternative: str
    model_version: str
    scoring_methodology: str

    # Preserved backward-compatible fields
    assessment: str  # APPROVED, CAUTION, NEEDS_REVIEW, BLOCKED
    categories: List[str]
    explanation: str
    relevant_values: List[EthicalValueScore]
    findings: List[FindingDetail]
    suggested_rewrite: str
    has_pii: bool
    is_educational: bool
    instruction_conflict: bool
    policy_version: str
    latency_ms: float

class RedactRequest(BaseModel):
    text: str
    mode: Optional[str] = "placeholder"  # placeholder, mask, hash

class RedactResponse(BaseModel):
    original_text: str
    sanitized_text: str
    detected_count: int
    entity_map: Dict[str, str]
    findings: List[Dict[str, Any]]

class RewriteRequest(BaseModel):
    prompt: str

class RewriteResponse(BaseModel):
    original_prompt: str
    rewritten_prompt: str
    strategy: str
    diff_html: str
    modifications: List[str]

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    bypass_approval: Optional[bool] = False

class ChatResponse(BaseModel):
    reply: str
    assessment: str
    is_demo_mode: bool
    model_name: str
    latency_ms: float
    safety_notes: Optional[str] = None

class ReviewRequest(BaseModel):
    analysis_id: str
    reviewer: str
    outcome: str  # approved, rejected, modified
    comments: str

class ReviewResponse(BaseModel):
    review_id: str
    status: str
    message: str

class EvaluationRunResponse(BaseModel):
    total_samples: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    category_metrics: Dict[str, Any]
    confusion_matrix: Dict[str, int]
    error_count: Optional[int] = 0
    errors: Optional[List[Dict[str, Any]]] = []
    evaluation_mode: Optional[str] = "local_deterministic_rules"
    report_timestamp: str

class DashboardResponse(BaseModel):
    total_prompts: int
    approved_count: int
    caution_count: int
    needs_review_count: int
    not_approved_count: int
    pii_detections: int
    avg_latency_ms: float
    recent_activity: List[Dict[str, Any]]
    category_distribution: Dict[str, int]
    demo_mode: bool

class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    course: str
    institution: str
    demo_mode: bool
    active_model: Optional[str] = None
    semantic_classifier_available: bool = False
    semantic_status: str = "unconfigured_demo"
    analysis_mode_default: str = "local"
