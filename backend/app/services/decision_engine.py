"""
Layer C: Deterministic Policy Decision Engine & Calibrated Risk Scoring.

Combines Layer A (Local Policy Rules) and Layer B (Gemini Structured Semantic
Classification) without allowing high-severity findings to be diluted or
overridden by unrelated low-risk or educational signals.
"""
from typing import Dict, Any, List, Optional
from app.services.taxonomy import (
    CATEGORY_DEFINITIONS,
    SEVERITY_RANK,
    SEVERITY_BASE_SCORE,
    BLOCKING_CATEGORIES,
    SCORING_METHODOLOGY,
)
from app.services.semantic_classifier import SemanticClassificationResult


class DeterministicDecisionEngine:
    def decide(
        self,
        prompt: str,
        local_res: Dict[str, Any],
        semantic_res: Optional[SemanticClassificationResult],
        semantic_model: Optional[str] = None,
        semantic_error: Optional[str] = None,
    ) -> Dict[str, Any]:
        has_semantic = semantic_res is not None
        analysis_mode = "hybrid" if has_semantic else "local"
        reduced_semantic_coverage = not has_semantic

        local_findings: List[Dict[str, Any]] = list(local_res.get("findings", []))
        merged_findings: List[Dict[str, Any]] = []

        # 1. Start with local findings (keeping track of which are pure PII vs behavioral risks)
        for lf in local_findings:
            merged_findings.append(dict(lf))

        # 2. Merge semantic findings (Layer B)
        if has_semantic and semantic_res is not None:
            is_semantic_benign_approved = (
                semantic_res.recommended_decision == "APPROVED"
                and semantic_res.overall_severity in ("none", "low")
                and semantic_res.intent in (
                    "educational_explanation",
                    "defensive_safety",
                    "ethical_analysis_quote",
                    "hypothetical_discussion",
                    "benign_general",
                )
            )
            for sf in semantic_res.risk_categories:
                cat = sf.category
                if cat == "benign_educational":
                    continue
                # Ignore low-severity topical tags when the semantic model explicitly approved a benign/educational prompt
                if is_semantic_benign_approved and sf.severity == "low":
                    continue
                # Avoid duplicate PII-only semantic finding if local PII already captured exact spans
                if cat == "privacy_surveillance" and local_res.get("has_pii") and sf.severity in ("low", "medium"):
                    # Keep local span findings, enrich only if semantic notes covert surveillance
                    if not any(w in sf.rationale.lower() for w in ("surveillance", "stalk", "spy", "dox", "covert", "track")):
                        continue
                merged_findings.append({
                    "category": cat,
                    "severity": sf.severity,
                    "description": sf.rationale,
                    "matched_text": sf.evidence or None,
                    "start": None,
                    "end": None,
                    "source": "semantic",
                })

            # If semantic resolved an ambiguous local dual-use signal as clearly defensive/educational
            # with high confidence (and no severe local finding exists), drop ONLY the local ambiguous signal.
            if (
                semantic_res.recommended_decision == "APPROVED"
                and semantic_res.intent in ("educational_explanation", "defensive_safety", "ethical_analysis_quote", "hypothetical_discussion")
                and semantic_res.confidence >= 0.80
                and not any(f["severity"] in ("high", "critical") and f.get("source") == "local" for f in local_findings)
                and not local_res.get("has_pii")
                and not local_res.get("instruction_conflict")
            ):
                ambiguous_set = {
                    (a["category"], a["description"]) for a in local_res.get("ambiguous_signals", [])
                }
                merged_findings = [
                    f for f in merged_findings
                    if (f["category"], f["description"]) not in ambiguous_set
                ]

        # 3. Determine consolidated intent & authorization indicator
        if has_semantic and semantic_res is not None:
            intent = semantic_res.intent
            auth_indicator = semantic_res.authorization_indicator
            # Preserve local unauthorized detection if semantic missed it
            if local_res.get("authorization_indicator") == "unauthorized_third_party":
                auth_indicator = "unauthorized_third_party"
            # Preserve harmful_instruction if local detected a critical/high blocking harm
            if any(
                f["category"] in BLOCKING_CATEGORIES and f["severity"] in ("high", "critical")
                for f in local_findings
            ):
                intent = "harmful_instruction"
        else:
            intent = local_res.get("intent", "benign_general")
            auth_indicator = local_res.get("authorization_indicator", "not_applicable")

        # 4. Aggregate per-category max severity & source provenance
        category_severities: Dict[str, str] = {}
        category_sources: Dict[str, set] = {}
        for f in merged_findings:
            cat = f["category"]
            sev = f.get("severity", "medium")
            if cat not in category_severities or SEVERITY_RANK.get(sev, 0) > SEVERITY_RANK.get(category_severities[cat], 0):
                category_severities[cat] = sev
            category_sources.setdefault(cat, set()).add(f.get("source", "local"))

        # Identify whether there are severe behavioral (non-PII) findings
        has_critical = any(f.get("severity") == "critical" for f in merged_findings)
        has_blocking_high = any(
            f.get("severity") in ("high", "critical")
            and (
                f["category"] in BLOCKING_CATEGORIES
                or (f["category"] == "privacy_surveillance" and f.get("subcategory") != "pii_exposure")
            )
            for f in merged_findings
        )
        non_pii_medium_cats = {
            f["category"]
            for f in merged_findings
            if f.get("severity") == "medium" and f.get("subcategory") != "pii_exposure"
        }

        has_pii = bool(local_res.get("has_pii"))
        instruction_conflict = bool(local_res.get("instruction_conflict")) or (
            "instruction_integrity" in category_severities
        )

        # 5. Compute severity-anchored monotonic raw risk score
        if category_severities:
            ranked_scores = sorted(
                (SEVERITY_BASE_SCORE.get(sev, 20.0) for sev in category_severities.values()),
                reverse=True,
            )
            raw_score = ranked_scores[0]
            for sec_score in ranked_scores[1:]:
                raw_score += min(12.0, round(0.25 * sec_score, 1))
            # Mildly boost high-sensitivity PII (API keys, SSN, Aadhaar, payment cards) inside CAUTION band
            if has_pii and any(
                f.get("raw_pii_severity") == "critical" for f in local_findings
            ) and not has_blocking_high:
                raw_score = max(raw_score, 52.0)
            raw_score = min(100.0, round(raw_score, 1))
        else:
            # Zero matched rules never equals absolute zero uncertainty
            if has_semantic and semantic_res is not None:
                raw_score = round(min(14.0, max(2.0, (1.0 - semantic_res.confidence) * 20.0)), 1)
            else:
                raw_score = 6.0

        # 6. Deterministic Policy Decision Rules (Layer C)
        semantic_recommends_block = (
            has_semantic
            and semantic_res is not None
            and semantic_res.recommended_decision == "BLOCKED"
        )
        semantic_recommends_review = (
            has_semantic
            and semantic_res is not None
            and semantic_res.recommended_decision == "NEEDS_REVIEW"
        )
        semantic_recommends_caution = (
            has_semantic
            and semantic_res is not None
            and semantic_res.recommended_decision == "CAUTION"
        )

        if (
            has_critical
            or has_blocking_high
            or (semantic_recommends_block and semantic_res.confidence >= 0.65)
        ):
            decision = "BLOCKED"
            min_floor = 88.0 if has_critical else 76.0
            final_risk = round(min(100.0, max(min_floor, raw_score)), 1)
        elif (
            semantic_recommends_review
            or (semantic_recommends_block and semantic_res.confidence < 0.65)
            or (intent == "ambiguous_context" and (len(merged_findings) > 0 or auth_indicator == "unspecified"))
            or len(non_pii_medium_cats) >= 2
        ):
            decision = "NEEDS_REVIEW"
            final_risk = round(min(74.0, max(52.0, raw_score)), 1)
        elif (
            has_pii
            or instruction_conflict
            or semantic_recommends_caution
            or len(category_severities) > 0
        ):
            decision = "CAUTION"
            final_risk = round(min(59.0, max(28.0, raw_score)), 1)
        else:
            decision = "APPROVED"
            final_risk = round(min(20.0, max(0.0, raw_score)), 1)

        # 7. Build detected_categories list and backward-compatible categories list
        detected_categories: List[Dict[str, Any]] = []
        ordered_cats = sorted(
            category_severities.keys(),
            key=lambda c: SEVERITY_RANK.get(category_severities[c], 0),
            reverse=True,
        )
        for cat in ordered_cats:
            meta = CATEGORY_DEFINITIONS.get(cat, {})
            sources = sorted(category_sources.get(cat, {"local"}))
            detected_categories.append({
                "category": cat,
                "label": meta.get("label", cat.replace("_", " ").title()),
                "severity": category_severities[cat],
                "source": "hybrid" if len(sources) > 1 else sources[0],
            })

        is_educational = intent in (
            "educational_explanation",
            "defensive_safety",
            "ethical_analysis_quote",
            "hypothetical_discussion",
        )
        categories_list = list(ordered_cats)
        if decision == "APPROVED" and is_educational and "benign_educational" not in categories_list:
            categories_list.append("benign_educational")
            detected_categories.append({
                "category": "benign_educational",
                "label": CATEGORY_DEFINITIONS["benign_educational"]["label"],
                "severity": "none",
                "source": analysis_mode,
            })
            category_severities["benign_educational"] = "none"

        # 8. Calibrate Confidence & Uncertainty Representation
        if has_semantic and semantic_res is not None:
            local_flagged = len(local_findings) > 0
            sem_flagged = len(semantic_res.risk_categories) > 0 or semantic_res.recommended_decision != "APPROVED"
            if local_flagged == sem_flagged:
                confidence = round(min(0.98, max(0.70, (semantic_res.confidence + 0.92) / 2.0)), 2)
            else:
                confidence = round(min(0.85, max(0.58, semantic_res.confidence * 0.85)), 2)
            uncertainty_level = "low" if confidence >= 0.80 else "moderate"
            uncertainty_notice = (
                f"Evaluated in hybrid mode (local policy rules + verified {semantic_model} semantic analysis). "
                "Automated risk scores remain heuristic estimates and do not replace human judgment."
            )
        else:
            if decision == "BLOCKED" and (has_critical or has_blocking_high):
                confidence = 0.84
                uncertainty_level = "moderate"
                uncertainty_notice = (
                    "Explicit high-severity local policy rule triggered. Semantic AI classification was unavailable "
                    f"({semantic_error or 'local fallback mode'}), so contextual nuance may have reduced coverage."
                )
            elif decision in ("CAUTION", "NEEDS_REVIEW"):
                confidence = 0.72
                uncertainty_level = "moderate"
                uncertainty_notice = (
                    "Flagged by local policy rules. Semantic AI classification was unavailable "
                    f"({semantic_error or 'local fallback mode'}); contextual review is advised."
                )
            else:
                confidence = 0.55
                uncertainty_level = "high"
                uncertainty_notice = (
                    "Reduced semantic coverage: no local policy rule matched, and live semantic AI classification "
                    "was unavailable. A low score in local-only mode does not guarantee the prompt is completely safe."
                )

        # 9. Build clear, context-aware explanation
        explanation = self._build_explanation(
            decision=decision,
            ordered_cats=ordered_cats,
            intent=intent,
            auth_indicator=auth_indicator,
            semantic_res=semantic_res,
            has_pii=has_pii,
            instruction_conflict=instruction_conflict,
            reduced_semantic_coverage=reduced_semantic_coverage,
        )

        # 10. Collect deduplicated evidence snippets & ethical principles
        evidence_snippets: List[str] = []
        seen_ev = set()
        for f in merged_findings:
            snippet = (f.get("matched_text") or "").strip()
            if snippet and snippet.lower() not in seen_ev:
                seen_ev.add(snippet.lower())
                evidence_snippets.append(snippet[:200])

        principles: List[str] = []
        for cat in ordered_cats or ["benign_educational"]:
            for p in CATEGORY_DEFINITIONS.get(cat, {}).get("principles", []):
                if p not in principles:
                    principles.append(p)

        model_version = (
            f"{semantic_model} + local-policy-v2"
            if has_semantic and semantic_model
            else "local-policy-v2 (semantic fallback)"
        )

        return {
            "overall_decision": decision,
            "assessment": decision,  # Backward-compatible field aligned with overall_decision
            "risk_score": final_risk,
            "confidence": confidence,
            "uncertainty_level": uncertainty_level,
            "uncertainty_notice": uncertainty_notice,
            "analysis_mode": analysis_mode,
            "reduced_semantic_coverage": reduced_semantic_coverage,
            "intent": intent,
            "authorization_indicator": auth_indicator,
            "categories": categories_list,
            "detected_categories": detected_categories,
            "category_severities": category_severities,
            "findings": merged_findings,
            "evidence_snippets": evidence_snippets,
            "explanation": explanation,
            "relevant_ethical_principles": principles,
            "semantic_safer_alternative": (
                semantic_res.safer_alternative.strip()
                if has_semantic and semantic_res and semantic_res.safer_alternative
                else None
            ),
            "has_pii": has_pii,
            "is_educational": is_educational,
            "instruction_conflict": instruction_conflict,
            "model_version": model_version,
            "scoring_methodology": SCORING_METHODOLOGY,
        }

    def _build_explanation(
        self,
        decision: str,
        ordered_cats: List[str],
        intent: str,
        auth_indicator: str,
        semantic_res: Optional[SemanticClassificationResult],
        has_pii: bool,
        instruction_conflict: bool,
        reduced_semantic_coverage: bool,
    ) -> str:
        if semantic_res and semantic_res.explanation:
            base = semantic_res.explanation.strip()
            if decision == "BLOCKED" and "block" not in base.lower() and "restrict" not in base.lower():
                return f"{base} Submission is blocked under SafePrompt AI policy."
            return base

        labels = [
            str(CATEGORY_DEFINITIONS.get(c, {}).get("label", c))
            for c in ordered_cats
        ]
        label_str = ", ".join(labels)

        if decision == "BLOCKED":
            return (
                f"Blocked by SafePrompt AI policy due to high-severity risk ({label_str}). "
                "The prompt requests actionable harmful, unauthorized, discriminatory, or deceptive outcomes."
            )
        if decision == "NEEDS_REVIEW":
            return (
                f"Flagged for contextual review ({label_str or 'sensitive domain'}). "
                "Intent or authorization context is ambiguous and requires verification before execution."
            )
        if decision == "CAUTION":
            parts = []
            if has_pii:
                parts.append("unmasked personal identifiers (sanitization recommended)")
            if instruction_conflict:
                parts.append("instruction-boundary conflict patterns")
            if not parts and label_str:
                parts.append(label_str.lower())
            return f"Caution advised: prompt contains {', '.join(parts)}."

        if reduced_semantic_coverage:
            return (
                "No local policy violations were matched, and phrasing appears consistent with legitimate inquiry. "
                "Note: semantic AI classification is currently unavailable (local fallback mode), so subtle risks may not be fully evaluated."
            )
        return (
            "Prompt appears aligned with responsible AI guidelines with legitimate educational, defensive, or general intent."
        )


decision_engine = DeterministicDecisionEngine()
