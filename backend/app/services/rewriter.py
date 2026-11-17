import re
import difflib
from typing import Dict, Any, List, Optional


class PromptRewriterService:
    def rewrite(
        self,
        prompt: str,
        has_pii: bool,
        categories: List[str],
        sanitized_text: str,
        semantic_alternative: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not prompt or not prompt.strip():
            return {
                "original_prompt": "",
                "rewritten_prompt": "",
                "strategy": "Empty input",
                "diff_html": "",
                "modifications": []
            }

        cats = set(categories or [])
        target_text = sanitized_text or prompt
        modifications: List[str] = []
        strategy = "Educational Reframing"

        if has_pii:
            modifications.append("Replaced personal contact or credential identifiers with safe placeholders.")

        # Prefer high-quality semantic safer alternative when provided for risky prompts
        non_benign_risks = cats - {"benign_educational", "benign_general"}
        if semantic_alternative and non_benign_risks and not (non_benign_risks == {"privacy_surveillance"} and has_pii):
            target_text = semantic_alternative.strip()
            strategy = "Context-Aware Semantic Reframing"
            modifications.append("Reframed the request into a safe, ethical, educational, or defensive inquiry.")
        elif "physical_harm_violence" in cats or "harmful_content" in cats:
            target_text = (
                "Explain the historical background, regulatory safety frameworks, and engineering hazard-mitigation "
                "protocols associated with dangerous materials, without providing operational or construction instructions."
            )
            strategy = "Safety & Historical Framing"
            modifications.append("Removed requests for dangerous physical harm or explosive instructions and reframed around safety and history.")
        elif "unauthorized_cybersecurity" in cats:
            target_text = (
                "Explain common network and router security vulnerabilities conceptually, and outline defensive "
                "best practices for hardening a network or device that I am authorized to administer."
            )
            strategy = "Defensive Security Reframing"
            modifications.append("Replaced unauthorized access or exploitation request with authorized defensive security guidance.")
        elif "discrimination_bias" in cats or "fairness_bias" in cats or re.search(
            r'\b(?:reject|screen\s+out|filter(?:\s+out)?|disqualify|penalize)\s+.*?\b(?:female|women|older|candidates|minority|caste|religion|hindu|muslim|christian|disabled)\b',
            target_text,
            re.IGNORECASE,
        ):
            target_text = (
                "Develop an objective, competency-based evaluation framework focusing strictly on verifiable "
                "qualifications, role-relevant skills, and fair opportunity standards without regard to religion, "
                "caste, gender, age, disability, or other protected characteristics."
            )
            strategy = "Bias-to-Merit Reframing"
            modifications.append("Replaced discriminatory criteria with objective, competency-based fairness standards.")
        elif "fraud_deception" in cats or "misleading_communication" in cats:
            target_text = (
                "Design a cybersecurity and fraud-awareness checklist highlighting common indicators of phishing, "
                "impersonation, and forged notices, along with safe verification steps for recipients."
            )
            strategy = "Defensive Fraud Awareness"
            modifications.append("Converted deceptive or impersonation request into defensive verification guidance.")
        elif "harassment_abuse" in cats:
            target_text = (
                "Draft a professional, respectful communication addressing a disagreement constructively "
                "while upholding dignity, clear boundaries, and conflict-resolution principles."
            )
            strategy = "Constructive Communication Reframing"
            modifications.append("Replaced abusive or threatening framing with respectful conflict-resolution communication.")
        elif "misinformation_manipulation" in cats:
            target_text = (
                "Explain how misinformation spreads online and outline evidence-based fact-checking and "
                "media-literacy strategies for verifying public announcements."
            )
            strategy = "Media Literacy & Verification Reframing"
            modifications.append("Reframed deliberate misinformation request into fact-checking and verification literacy.")
        elif "privacy_surveillance" in cats and not has_pii:
            target_text = (
                "Discuss privacy-by-design principles, informed consent standards, and data-minimization "
                "safeguards required when evaluating digital monitoring technologies."
            )
            strategy = "Privacy-by-Design Reframing"
            modifications.append("Reframed covert surveillance or doxxing request into ethical privacy governance analysis.")
        elif "instruction_integrity" in cats:
            cleaned = re.sub(
                r'(?i)(?:disregard|ignore|forget|override)\s+(?:all\s+)?(?:previous|prior|system).*?[.!?]',
                '',
                target_text,
            ).strip()
            target_text = cleaned if cleaned and cleaned != target_text else (
                "Please provide a clear, structured, and accurate overview of the core educational topic."
            )
            strategy = "Boundary Realignment"
            modifications.append("Removed instruction-override or persona-hijack commands while preserving legitimate inquiry.")
        elif "other_unethical_risk" in cats:
            target_text = (
                "Explain the ethical principles, integrity standards, and legitimate study or compliance "
                "practices relevant to this situation."
            )
            strategy = "Integrity & Compliance Reframing"
            modifications.append("Reframed unethical or rule-evasion request into constructive ethical guidance.")

        if not modifications:
            target_text = prompt
            strategy = "Direct Alignment (No Changes Needed)"

        diff_html = self._build_diff(prompt, target_text)

        return {
            "original_prompt": prompt,
            "rewritten_prompt": target_text,
            "strategy": strategy,
            "diff_html": diff_html,
            "modifications": modifications
        }

    def _build_diff(self, original: str, rewritten: str) -> str:
        words1 = original.split()
        words2 = rewritten.split()
        matcher = difflib.SequenceMatcher(None, words1, words2)

        html_parts = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                html_parts.append(" ".join(words1[i1:i2]))
            elif tag == 'delete':
                html_parts.append(f'<span class="line-through text-rose-400 bg-rose-950/30 px-1 rounded">{" ".join(words1[i1:i2])}</span>')
            elif tag == 'insert':
                html_parts.append(f'<span class="text-emerald-400 bg-emerald-950/30 px-1 rounded font-medium">{" ".join(words2[j1:j2])}</span>')
            elif tag == 'replace':
                html_parts.append(f'<span class="line-through text-rose-400 bg-rose-950/30 px-1 rounded">{" ".join(words1[i1:i2])}</span> <span class="text-emerald-400 bg-emerald-950/30 px-1 rounded font-medium">{" ".join(words2[j1:j2])}</span>')

        return " ".join(html_parts)


rewriter_service = PromptRewriterService()
