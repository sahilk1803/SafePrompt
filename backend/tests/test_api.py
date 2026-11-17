import pytest
from app.api.routes import (
    health_check, analyze_prompt, redact_pii, rewrite_prompt,
    chat_endpoint, get_dashboard, get_audit_trail,
    run_evaluation, get_sustainability, get_syllabus
)
from app.models.schemas import (
    AnalyzeRequest, RedactRequest, RewriteRequest, ChatRequest
)

def test_health_endpoint():
    res = health_check()
    assert res.status == "healthy"
    assert res.course == "23CIE734"

def test_analyze_endpoint():
    res = analyze_prompt(AnalyzeRequest(prompt="Explain supervised learning with a practical example."))
    assert res.overall_decision == "APPROVED"
    assert res.assessment == "APPROVED"
    assert res.analysis_id.startswith("ANL-")
    assert res.analysis_mode in ("local", "semantic", "hybrid")
    assert "benign_educational" in res.categories
    assert len(res.relevant_ethical_principles) >= 1
    assert res.policy_version.startswith("2026")

def test_redact_endpoint():
    res = redact_pii(RedactRequest(text="Contact student@msrit.edu or call +91-98765-43210", mode="placeholder"))
    assert res.detected_count == 2
    assert "[EMAIL_1]" in res.sanitized_text
    assert "[PHONE_1]" in res.sanitized_text

def test_rewrite_endpoint():
    res = rewrite_prompt(RewriteRequest(prompt="Filter out female candidates during hiring."))
    assert "competency-based" in res.rewritten_prompt.lower() or "objective" in res.rewritten_prompt.lower()

def test_chat_endpoint_demo():
    res = chat_endpoint(ChatRequest(message="Explain supervised learning"))
    assert res.assessment == "APPROVED"
    assert len(res.reply) > 20

def test_dashboard_endpoint():
    res = get_dashboard()
    assert res.total_prompts >= 5
    assert isinstance(res.recent_activity, list)

def test_audit_endpoint():
    res = get_audit_trail(limit=10)
    assert res["count"] >= 1
    assert "data_minimization_notice" in res

def test_evaluate_endpoint():
    res = run_evaluation()
    assert res.total_samples >= 100
    assert res.accuracy >= 85.0
    assert res.f1_score >= 88.0

def test_sustainability_endpoint():
    res = get_sustainability(region="India (National Avg)")
    assert "estimated_energy_kwh" in res
    assert "assumptions_disclaimer" in res

def test_syllabus_endpoint():
    res = get_syllabus()
    assert len(res["units"]) == 5
