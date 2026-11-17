import os
import time
import requests
from typing import Dict, Any, List
from app import config
from app.services.analyzer import analyzer_service

class GeminiService:
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.is_demo_mode = config.IS_DEMO_MODE

    def chat(self, user_message: str, history: List[Dict[str, str]] = None, bypass_approval: bool = False) -> Dict[str, Any]:
        start_time = time.time()

        # Step 1: Pre-generation hybrid analysis (Layers A-D)
        analysis = analyzer_service.analyze(user_message)
        decision = analysis.get("overall_decision", analysis["assessment"])

        # Hard guardrail: BLOCKED prompts can NEVER be submitted to the downstream model,
        # even if bypass_approval=True is passed by a client.
        if decision in ("BLOCKED", "NOT_APPROVED"):
            latency_ms = round((time.time() - start_time) * 1000, 2)
            cat_labels = ", ".join(
                c["label"] for c in analysis.get("detected_categories", [])
                if c.get("category") != "benign_educational"
            ) or "Policy Violation"
            return {
                "reply": (
                    "🚫 **Prompt Blocked by SafePrompt AI Policy**\n\n"
                    f"**Detected Risk Categories:** {cat_labels}\n"
                    f"**Reason:** {analysis['explanation']}\n\n"
                    f"**Recommended Safer Alternative:**\n> {analysis['suggested_rewrite']}\n\n"
                    "Blocked prompts cannot be dispatched to the AI model. You may submit the responsible alternative above or review the assessment in Governance Logs."
                ),
                "assessment": "BLOCKED",
                "is_demo_mode": self.is_demo_mode,
                "model_name": "SafePrompt-Gatekeeper",
                "latency_ms": latency_ms,
                "safety_notes": (
                    f"Blocked ({analysis['analysis_mode']} mode, risk {analysis['risk_score']}/100). "
                    "Submission halted prior to model dispatch."
                ),
            }

        # Pause NEEDS_REVIEW prompts unless explicitly approved for contextual review
        if decision == "NEEDS_REVIEW" and not bypass_approval:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "reply": (
                    "⚠️ **Prompt Paused for Contextual Review**\n\n"
                    f"**Reason:** {analysis['explanation']}\n\n"
                    f"**Clarified Safer Alternative:**\n> {analysis['suggested_rewrite']}\n\n"
                    "Please clarify your educational or authorized context, or use the suggested alternative above."
                ),
                "assessment": "NEEDS_REVIEW",
                "is_demo_mode": self.is_demo_mode,
                "model_name": "SafePrompt-Gatekeeper",
                "latency_ms": latency_ms,
                "safety_notes": f"Paused for review ({analysis['analysis_mode']} mode, risk {analysis['risk_score']}/100).",
            }

        # Step 2: Sanitize unmasked PII before forwarding to external model
        outbound_message = user_message
        if analysis.get("has_pii"):
            from app.services.privacy import privacy_service
            outbound_message = privacy_service.redact(user_message, mode="placeholder")["sanitized_text"]

        # Step 3: Generate response (Live Gemini if key present, else Offline Academic Simulator)
        if not self.is_demo_mode and self.api_key:
            reply_text, model_used = self._call_gemini_api(outbound_message, history=history)
        else:
            reply_text = self._generate_offline_educational_response(outbound_message, decision)
            model_used = "SafePrompt Educational Simulator (Offline Classroom Mode)"

        latency_ms = round((time.time() - start_time) * 1000, 2)

        safety_note = (
            f"Pre-generation checks passed ({analysis['analysis_mode']} mode)."
            if decision == "APPROVED"
            else f"Caution flagged ({analysis['analysis_mode']} mode); PII sanitized before dispatch."
            if analysis.get("has_pii")
            else f"Caution flagged during pre-analysis ({analysis['analysis_mode']} mode)."
        )

        return {
            "reply": reply_text,
            "assessment": decision,
            "is_demo_mode": self.is_demo_mode,
            "model_name": model_used,
            "latency_ms": latency_ms,
            "safety_notes": safety_note,
        }

    def _call_gemini_api(self, prompt: str, history: List[Dict[str, str]] = None) -> tuple[str, str]:
        contents: List[Dict[str, Any]] = []
        for msg in (history or [])[-6:]:
            text = (msg.get("content") or "").strip()
            if not text:
                continue
            role = "model" if msg.get("role") in ("assistant", "model") else "user"
            contents.append({"role": role, "parts": [{"text": text}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        candidate_models = [config.DEFAULT_MODEL] + [
            m for m in config.FALLBACK_MODELS if m != config.DEFAULT_MODEL
        ]
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": contents,
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1024}
        }

        last_error = "unknown error"
        for model_name in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates") or []
                    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
                    text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
                    if text:
                        return text, f"Google {model_name} (Live API)"
                    last_error = f"empty response from {model_name}"
                else:
                    last_error = f"HTTP {resp.status_code}"
                    if resp.status_code not in (404, 429, 500, 503):
                        break
            except Exception as e:
                last_error = str(e)

        return (
            f"API notice: Live endpoint unavailable ({last_error}). "
            "Displaying offline academic analysis instead:\n\n" +
            self._generate_offline_educational_response(prompt, "APPROVED"),
            "Fallback Simulator"
        )

    def _generate_offline_educational_response(self, prompt: str, assessment: str) -> str:
        p_lower = prompt.lower()
        if "supervised" in p_lower or "learning" in p_lower:
            return (
                "### Supervised Learning & Ethical Considerations (Unit I)\n\n"
                "In supervised learning, models map labeled input features to target outputs using ground-truth training datasets.\n\n"
                "- **Practical Example**: Email spam filtering uses labeled emails (spam vs non-spam). "
                "The classifier calculates probability weights for specific keywords and headers.\n"
                "- **Ethical Implication**: If the training data reflects historical biases (e.g. flagging legitimate student organizational emails as suspicious), "
                "the model perpetuates representational harm. Responsible AI requires continuous data distribution audits."
            )
        elif "utilitarian" in p_lower or "deontological" in p_lower or "ethics" in p_lower:
            return (
                "### Comparative Ethical Theories in Autonomous Systems (Unit II)\n\n"
                "When addressing unavoidable moral dilemmas in automated systems (such as emergency trajectory planning):\n\n"
                "1. **Utilitarian Perspective (Bentham & Mill)**:\n"
                "   - Focuses strictly on consequences and aggregate welfare.\n"
                "   - Aims to minimize total casualties or physical injury, treating all affected persons as equal units in a utility calculus.\n\n"
                "2. **Deontological Perspective (Kant)**:\n"
                "   - Focuses on duties, universal rules, and human moral dignity.\n"
                "   - The Categorical Imperative dictates that humans must never be used purely as instruments. Active targeting of a bystander to spare others is impermissible under strict duty ethics.\n\n"
                "**Synthesis**: Real-world safety frameworks avoid moral absolutism and document explicit value trade-offs with public stakeholder oversight."
            )
        elif "privacy" in p_lower or "student" in p_lower or "biometric" in p_lower:
            return (
                "### Student Data Privacy & Governance (Unit I & IV)\n\n"
                "Deploying biometric and behavioral surveillance on university campuses raises critical governance questions:\n\n"
                "- **Proportionality Principle**: Security measures must be proportionate to actual verified threats rather than pervasive speculative monitoring.\n"
                "- **Consent Validity**: In hierarchical academic environments, student consent is rarely completely uncoerced.\n"
                "- **Data Minimization**: Best practice mandates edge-processing, immediate biometric template deletion, and strict prohibition of secondary commercial uses."
            )
        elif "automation" in p_lower or "labor" in p_lower or "employment" in p_lower:
            return (
                "### Societal & Labor Impacts of Generative AI (Unit V)\n\n"
                "Generative AI alters knowledge work across software engineering, legal drafting, and technical communication:\n\n"
                "- **Task Augmentation vs Job Displacement**: Routine coding and documentation tasks are accelerated, but junior engineers risk missing foundational debugging intuition.\n"
                "- **Transition Policies**: Economists recommend investing in universal lifelong retraining and shifting evaluation toward authentic human-in-the-loop oversight."
            )
        else:
            return (
                "### SafePrompt AI Response (Educational Demo Mode)\n\n"
                f"Your query: *\"{prompt[:80]}...\"*\n\n"
                "This response was evaluated through the SafePrompt AI governance gateway:\n"
                "- **Privacy Shield**: Scanned for unmasked PII and sensitive credentials.\n"
                "- **Instruction Integrity**: Verified instruction boundaries.\n"
                "- **Ethical Alignment**: Evaluated against fairness, transparency, and accountability standards.\n\n"
                "In a classroom environment, maintaining human critical thinking alongside AI assistance is the foundational goal of course 23CIE734."
            )

gemini_service = GeminiService()
