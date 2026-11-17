"""
SafePrompt AI Hybrid Prompt Analysis Orchestrator (Layers A -> B -> C -> D).

- Layer A: Local policy rules & context-aware PII/integrity/compositional checks
- Layer B: Structured Gemini semantic classification (Pydantic-validated) on PII-sanitized text
- Layer C: Deterministic policy decision engine & severity-anchored risk scoring
- Layer D: Explainability, ethical value alignment, and intent-preserving safer rewrites
"""
import time
import uuid
from typing import Dict, Any

from app import config
from app.services.local_rules import local_rules_engine
from app.services.semantic_classifier import semantic_classifier
from app.services.decision_engine import decision_engine
from app.services.ethics import ethics_service
from app.services.rewriter import rewriter_service
from app.services.taxonomy import SCORING_METHODOLOGY


class PromptAnalyzerService:
    def analyze(
        self,
        prompt: str,
        user_id: str = "student_demo",
        use_semantic: bool = True,
    ) -> Dict[str, Any]:
        start_time = time.time()
        analysis_id = f"ANL-{uuid.uuid4().hex[:8].upper()}"

        if not prompt or not prompt.strip():
            return self._empty_result(analysis_id)

        # Layer A: Local Policy Rules & Privacy Shield
        local_res = local_rules_engine.evaluate(prompt)
        sanitized_text = local_res["pii_result"].get("sanitized_text") or prompt

        # Layer B: Optional Structured Semantic Classification (Gemini)
        # Always send PII-sanitized text externally to uphold data minimization.
        semantic_res = None
        semantic_model = None
        semantic_error = None
        if use_semantic:
            semantic_res, semantic_model, semantic_error = semantic_classifier.classify(sanitized_text)
        else:
            semantic_error = "Semantic classification bypassed for deterministic local evaluation."

        # Layer C: Deterministic Policy Decision Engine & Calibrated Scoring
        decision_res = decision_engine.decide(
            prompt=prompt,
            local_res=local_res,
            semantic_res=semantic_res,
            semantic_model=semantic_model,
            semantic_error=semantic_error,
        )

        # Layer D: Explainability — Ethical Values & Safe Alternative Rewrite
        relevant_values = ethics_service.evaluate_values(
            prompt=prompt,
            detected_categories=decision_res["categories"],
            has_pii=decision_res["has_pii"],
            overall_decision=decision_res["overall_decision"],
        )

        rewrite_res = rewriter_service.rewrite(
            prompt=prompt,
            has_pii=decision_res["has_pii"],
            categories=decision_res["categories"],
            sanitized_text=sanitized_text,
            semantic_alternative=decision_res.get("semantic_safer_alternative"),
        )

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Clean findings to match FindingDetail schema cleanly
        formatted_findings = [
            {
                "category": f["category"],
                "severity": f["severity"],
                "description": f["description"],
                "matched_text": f.get("matched_text"),
                "start": f.get("start"),
                "end": f.get("end"),
                "source": f.get("source", "local"),
            }
            for f in decision_res["findings"]
        ]

        return {
            # New Requirement 7 structured fields
            "analysis_id": analysis_id,
            "overall_decision": decision_res["overall_decision"],
            "confidence": decision_res["confidence"],
            "uncertainty_level": decision_res["uncertainty_level"],
            "uncertainty_notice": decision_res["uncertainty_notice"],
            "analysis_mode": decision_res["analysis_mode"],
            "reduced_semantic_coverage": decision_res["reduced_semantic_coverage"],
            "intent": decision_res["intent"],
            "authorization_indicator": decision_res["authorization_indicator"],
            "detected_categories": decision_res["detected_categories"],
            "category_severities": decision_res["category_severities"],
            "evidence_snippets": decision_res["evidence_snippets"],
            "relevant_ethical_principles": decision_res["relevant_ethical_principles"],
            "recommended_safer_alternative": rewrite_res["rewritten_prompt"],
            "model_version": decision_res["model_version"],
            "scoring_methodology": decision_res["scoring_methodology"],

            # Preserved backward-compatible fields
            "assessment": decision_res["assessment"],
            "risk_score": decision_res["risk_score"],
            "categories": decision_res["categories"],
            "explanation": decision_res["explanation"],
            "relevant_values": relevant_values,
            "findings": formatted_findings,
            "suggested_rewrite": rewrite_res["rewritten_prompt"],
            "has_pii": decision_res["has_pii"],
            "is_educational": decision_res["is_educational"],
            "instruction_conflict": decision_res["instruction_conflict"],
            "policy_version": config.POLICY_VERSION,
            "latency_ms": latency_ms,
        }

    def _empty_result(self, analysis_id: str) -> Dict[str, Any]:
        return {
            "analysis_id": analysis_id,
            "overall_decision": "APPROVED",
            "assessment": "APPROVED",
            "risk_score": 0.0,
            "confidence": 1.0,
            "uncertainty_level": "low",
            "uncertainty_notice": "No prompt text provided.",
            "analysis_mode": "local",
            "reduced_semantic_coverage": False,
            "intent": "benign_general",
            "authorization_indicator": "not_applicable",
            "categories": [],
            "detected_categories": [],
            "category_severities": {},
            "evidence_snippets": [],
            "explanation": "No prompt entered.",
            "relevant_ethical_principles": [],
            "relevant_values": [],
            "findings": [],
            "suggested_rewrite": "",
            "recommended_safer_alternative": "",
            "has_pii": False,
            "is_educational": False,
            "instruction_conflict": False,
            "model_version": "local-policy-v2",
            "policy_version": config.POLICY_VERSION,
            "scoring_methodology": SCORING_METHODOLOGY,
            "latency_ms": 0.0,
        }


analyzer_service = PromptAnalyzerService()
