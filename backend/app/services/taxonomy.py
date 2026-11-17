"""
Comprehensive Risk Taxonomy, Intent Definitions, and Scoring Methodology
for SafePrompt AI (Policy v2.0).
"""
from typing import Dict, List

# Canonical 10-category risk taxonomy
CATEGORY_DEFINITIONS: Dict[str, Dict[str, object]] = {
    "physical_harm_violence": {
        "label": "Physical Harm & Violence",
        "description": "Instructions or assistance involving explosives, weapons, violence, dangerous materials, or self-harm.",
        "default_severity": "critical",
        "principles": ["Safety & Non-Maleficence", "Human Life & Dignity"],
    },
    "unauthorized_cybersecurity": {
        "label": "Unauthorized Cybersecurity Access",
        "description": "Unauthorized access to systems, networks, routers, or accounts; credential theft; exploitation; or malware.",
        "default_severity": "critical",
        "principles": ["Security & Authorization", "Accountability"],
    },
    "discrimination_bias": {
        "label": "Discrimination & Unfair Bias",
        "description": "Exclusion, penalization, or prejudicial generalizations based on religion, caste, race, gender, age, disability, or other protected traits.",
        "default_severity": "high",
        "principles": ["Fairness & Inclusion", "Non-Discrimination"],
    },
    "fraud_deception": {
        "label": "Fraud & Deceptive Communication",
        "description": "Phishing, impersonation, credential harvesting, forged documents, or financial scams.",
        "default_severity": "high",
        "principles": ["Truthfulness & Honesty", "Trust & Integrity"],
    },
    "privacy_surveillance": {
        "label": "Privacy & Surveillance Risk",
        "description": "Exposure of unmasked personal information (PII), doxxing, covert tracking, or unauthorized surveillance.",
        "default_severity": "medium",
        "principles": ["Privacy & Consent", "Data Minimization"],
    },
    "harassment_abuse": {
        "label": "Harassment & Targeted Abuse",
        "description": "Threats, intimidation, blackmail, hate speech, cyberbullying, or targeted verbal abuse.",
        "default_severity": "high",
        "principles": ["Respect & Dignity", "Safety & Non-Maleficence"],
    },
    "misinformation_manipulation": {
        "label": "Misinformation & Manipulation",
        "description": "Deliberate fabrication of false news, rumors, propaganda, or covert manipulative campaigns.",
        "default_severity": "high",
        "principles": ["Truthfulness & Epistemic Integrity", "Human Autonomy"],
    },
    "instruction_integrity": {
        "label": "Instruction Integrity & Injection",
        "description": "Prompt injection, policy bypass attempts, persona hijacking, delimiter mimicry, or system prompt extraction.",
        "default_severity": "medium",
        "principles": ["Transparency & Oversight", "System Integrity"],
    },
    "other_unethical_risk": {
        "label": "Other Unethical or Unsafe Request",
        "description": "Unsafe, illegal, or unethical requests outside narrow categories (e.g., exam cheating evasion, sabotage, bribery).",
        "default_severity": "high",
        "principles": ["Accountability", "Responsible Conduct"],
    },
    "benign_educational": {
        "label": "Educational & Defensive Inquiry",
        "description": "Legitimate educational, scientific, defensive security, safety-oriented, or ethical analysis inquiry.",
        "default_severity": "none",
        "principles": ["Human Autonomy", "Responsible Inquiry"],
    },
}

ALL_RISK_CATEGORIES: List[str] = [
    k for k in CATEGORY_DEFINITIONS.keys() if k != "benign_educational"
]

ALL_CATEGORIES: List[str] = list(CATEGORY_DEFINITIONS.keys())

INTENT_TYPES: List[str] = [
    "harmful_instruction",
    "educational_explanation",
    "defensive_safety",
    "ethical_analysis_quote",
    "hypothetical_discussion",
    "ambiguous_context",
    "benign_general",
]

SEVERITY_RANK: Dict[str, int] = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

# Base risk score anchored to highest finding severity
SEVERITY_BASE_SCORE: Dict[str, float] = {
    "none": 0.0,
    "low": 18.0,
    "medium": 42.0,
    "high": 76.0,
    "critical": 90.0,
}

# Severe categories where a high/critical finding triggers an immediate BLOCKED policy decision
BLOCKING_CATEGORIES = {
    "physical_harm_violence",
    "unauthorized_cybersecurity",
    "discrimination_bias",
    "fraud_deception",
    "harassment_abuse",
    "misinformation_manipulation",
    "other_unethical_risk",
}

SCORING_METHODOLOGY = (
    "Calibrated Multi-Layer Policy Scoring (v2.0): "
    "Each risk finding carries a severity tier (low=18, medium=42, high=76, critical=90). "
    "The composite score anchors on the highest-severity finding (preventing high-severity harms from being diluted) "
    "and adds bounded diminishing increments (+25% of secondary category severities, capped at +12 per category, max 100). "
    "Policy decisions (APPROVED, CAUTION, NEEDS_REVIEW, BLOCKED) are enforced deterministically from category, severity, "
    "intent, and authorization context—not solely from the numeric score—and scores are clamped to match the decision tier "
    "(APPROVED <25, CAUTION 25-59.9, NEEDS_REVIEW 50-74.9, BLOCKED 75-100). "
    "A low or zero score never proves absolute safety, especially when semantic classification is unavailable."
)
