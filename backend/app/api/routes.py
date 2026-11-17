import json
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from app import config
from app.models.schemas import (
    AnalyzeRequest, AnalyzeResponse,
    RedactRequest, RedactResponse,
    RewriteRequest, RewriteResponse,
    ChatRequest, ChatResponse,
    DashboardResponse, HealthResponse,
    ReviewRequest, ReviewResponse,
    EvaluationRunResponse
)
from app.services.analyzer import analyzer_service
from app.services.privacy import privacy_service
from app.services.rewriter import rewriter_service
from app.services.gemini_service import gemini_service
from app.services.ethics import ethics_service
from app.services.sustainability import sustainability_service
from app.services.societal import societal_service
from app.services.evaluator import evaluator_service
from app.services.semantic_classifier import semantic_classifier
from app.database.db import db

router = APIRouter(prefix="/api/v1")

@router.get("/health", response_model=HealthResponse)
def health_check():
    sem_status = semantic_classifier.get_status(probe_if_stale=True)
    semantic_available = bool(sem_status["verified_available"])
    return HealthResponse(
        status="healthy",
        app=config.APP_NAME,
        version=config.APP_VERSION,
        course=config.COURSE_CODE,
        institution=config.INSTITUTION,
        demo_mode=config.IS_DEMO_MODE,
        active_model="local-demo-simulator" if config.IS_DEMO_MODE else (sem_status["active_model"] or config.DEFAULT_MODEL),
        semantic_classifier_available=semantic_available,
        semantic_status=sem_status["status"],
        analysis_mode_default="hybrid" if semantic_available else "local",
    )

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_prompt(payload: AnalyzeRequest):
    result = analyzer_service.analyze(payload.prompt, user_id=payload.user_id)
    pii_preview = privacy_service.redact(payload.prompt, mode="placeholder")["sanitized_text"]
    # Record analysis to SQLite database with matching analysis_id & minimized snippet
    db.record_analysis({
        "analysis_id": result["analysis_id"],
        "prompt": payload.prompt,
        "sanitized_snippet": pii_preview,
        "user_id": payload.user_id,
        "assessment": result["overall_decision"],
        "risk_score": result["risk_score"],
        "categories": result["categories"],
        "explanation": result["explanation"],
        "latency_ms": result["latency_ms"]
    })
    return AnalyzeResponse(**result)

@router.post("/redact", response_model=RedactResponse)
def redact_pii(payload: RedactRequest):
    result = privacy_service.redact(payload.text, mode=payload.mode or "placeholder")
    return RedactResponse(**result)

@router.post("/rewrite", response_model=RewriteResponse)
def rewrite_prompt(payload: RewriteRequest):
    # First analyze to identify risks and PII
    analysis = analyzer_service.analyze(payload.prompt)
    pii_res = privacy_service.redact(payload.prompt, mode="placeholder")
    result = rewriter_service.rewrite(
        payload.prompt,
        analysis["has_pii"],
        analysis["categories"],
        pii_res["sanitized_text"]
    )
    return RewriteResponse(**result)

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    history_dicts = [{"role": m.role, "content": m.content} for m in payload.history]
    result = gemini_service.chat(
        payload.message,
        history=history_dicts,
        bypass_approval=payload.bypass_approval
    )
    return ChatResponse(**result)

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard():
    metrics = db.get_dashboard_metrics()
    return DashboardResponse(**metrics)

@router.get("/audit")
def get_audit_trail(limit: int = Query(50, ge=1, le=200)):
    records = db.get_audit_records(limit=limit)
    return {
        "count": len(records),
        "records": records,
        "data_minimization_notice": "Original prompt text is not retained in routine audit records. Cryptographic SHA-256 hashes and minimized snippets are logged."
    }

@router.post("/evaluate", response_model=EvaluationRunResponse)
def run_evaluation():
    result = evaluator_service.run_evaluation()
    return EvaluationRunResponse(**result)

@router.get("/evaluate/dataset")
def get_evaluation_dataset_csv():
    csv_content = evaluator_service.get_dataset_csv()
    return {
        "filename": "safeprompt_evaluation_benchmark_60.csv",
        "csv": csv_content
    }

@router.get("/sustainability")
def get_sustainability(region: str = Query("India (National Avg)")):
    metrics = db.get_dashboard_metrics()
    return sustainability_service.get_metrics(metrics["total_prompts"], region=region)

@router.get("/scenarios")
def get_scenarios():
    return ethics_service.get_scenarios()

@router.get("/societal")
def get_societal():
    return societal_service.get_data()

@router.post("/reviews", response_model=ReviewResponse)
def submit_review(payload: ReviewRequest):
    return ReviewResponse(
        review_id="REV-" + payload.analysis_id[-6:],
        status="SUBMITTED",
        message=f"Faculty review recorded. Assessment outcome: {payload.outcome}."
    )

@router.get("/syllabus")
def get_syllabus():
    return {
        "course": config.COURSE_CODE,
        "course_name": config.COURSE_NAME,
        "institution": config.INSTITUTION,
        "units": [
            {
                "unit": "Unit I",
                "title": "Foundations of AI and Ethics",
                "topics": "AI definitions, ethical foundations, data quality, algorithmic bias, privacy vulnerabilities",
                "implementation": "Local PII Scanner, Privacy Shield, Synthetic Data Minimization, and heuristic uncertainty."
            },
            {
                "unit": "Unit II",
                "title": "Ethical Decision Making, Responsibility and Design for Values",
                "topics": "Utilitarianism, Deontology, Virtue Ethics, Social Contract, Value alignment, Stakeholder matrix",
                "implementation": "Interactive Ethical Reasoning Lab, 4-Lens philosophical breakdown, and 3-pillar ethical impact matrix."
            },
            {
                "unit": "Unit III",
                "title": "Trustworthy AI, Alignment, Moral Machines and Long-Term Ethics",
                "topics": "AI alignment, instruction integrity, jailbreak boundaries, human-in-the-loop oversight",
                "implementation": "Instruction Integrity Checker, Safe Prompt Rewriting, Gated Chatbot, and Pre-generation safety gates."
            },
            {
                "unit": "Unit IV",
                "title": "Governance and Responsible AI in Practice",
                "topics": "NIST AI RMF, EU AI Act, auditability, accountability, policy versioning, contestability",
                "implementation": "Governance & Audit Dashboard, minimized SQLite records, faculty review workflow, and CSV export."
            },
            {
                "unit": "Unit V",
                "title": "AI, Society and Socio-Economic Impacts",
                "topics": "Automation, workforce displacement, education, digital divides, sustainable AI and computational footprint",
                "implementation": "Societal Impact Explorer, Green AI Dashboard, regional grid carbon modeling, and Green Prompting tips."
            }
        ]
    }
