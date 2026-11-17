import re
from typing import Dict, Any, List

# Educational/defensive framing check so explaining prompt injection isn't flagged as an attack
_EDU_INJECTION_DISCUSSION_RE = re.compile(
    r'^\s*(?:explain|describe|discuss|what\s+(?:is|are)|how\s+(?:do|does|can\s+we)\s+(?:defend|prevent|mitigate|protect|detect|work)|'
    r'compare|summarize|define)\b',
    re.IGNORECASE,
)

# Instruction conflict & prompt-injection patterns
INTEGRITY_PATTERNS = [
    {
        "id": "RULE_DISREGARD",
        "pattern": re.compile(
            r'\b(?:disregard|ignore|forget|override|bypass|discard|drop)\s+(?:all\s+)?(?:the\s+)?'
            r'(?:previous|prior|above|former|initial|earlier|system|safety|ethical|content)\s+'
            r'(?:system\s+)?(?:instructions?|prompts?|rules?|guidelines?|preferences?|constraints?|policies|filters?|guardrails?)\b',
            re.IGNORECASE
        ),
        "label": "Instruction Boundary Disregard",
        "explanation": "Attempts to nullify earlier instructions, system constraints, or safety boundaries.",
        "severity": "medium",
        "weight": 35.0
    },
    {
        "id": "ROLE_REPLACEMENT",
        "pattern": re.compile(
            r'\b(?:(?:from\s+now\s+on\s+you\s+are|you\s+must\s+now\s+act\s+as|pretend\s+(?:you\s+are|to\s+be)\s+(?:an?\s+)?)'
            r'(?:unrestricted|unfiltered|uncensored|jailbroken|pirate|court\s+jester|evil|[a-zA-Z\s]{3,30})|'
            r'(?:enter|enable|switch\s+to)\s+(?:DAN|developer|god|unrestricted|jailbreak)\s+mode|'
            r'(?:without\s+any\s+(?:safety|ethical|content|policy)\s+(?:rules?|restrictions?|filters?|limits?)))\b',
            re.IGNORECASE
        ),
        "label": "Persona Hijack / Policy Bypass Mode",
        "explanation": "Attempts to replace the defined assistant role with an unconstrained persona or jailbreak mode.",
        "severity": "medium",
        "weight": 30.0
    },
    {
        "id": "PROMPT_EXTRACTION",
        "pattern": re.compile(
            r'\b(?:repeat|print|reveal|output|show|leak|dump|expose|tell\s+me)\s+(?:me\s+)?(?:all\s+)?(?:the\s+|your\s+)?'
            r'(?:system\s+prompt|developer\s+(?:instructions?|prompt)|hidden\s+(?:rules?|instructions?|prompt)|'
            r'internal\s+(?:instructions?|prompt)|everything\s+above)\b',
            re.IGNORECASE
        ),
        "label": "System Instruction Extraction",
        "explanation": "Attempts to inspect internal system or developer instructions rather than requesting assistance.",
        "severity": "medium",
        "weight": 30.0
    },
    {
        "id": "DELIMITER_MIMICRY",
        "pattern": re.compile(
            r'(?:---+\s*END\s+SYSTEM|\[SYSTEM_OVERRIDE\]|<\|system\|>|\[INST\]|###\s*SYSTEM\s*OVERRIDE|Human:\s*Assistant:)',
            re.IGNORECASE
        ),
        "label": "Delimiter Conflict Pattern",
        "explanation": "Simulates structural message delimiters to confuse parser or role boundaries.",
        "severity": "high",
        "weight": 45.0
    }
]


class InstructionIntegrityService:
    def inspect(self, prompt: str) -> Dict[str, Any]:
        if not prompt:
            return {"has_conflict": False, "conflicts": [], "count": 0, "integrity_score": 100.0}

        # Check whether the prompt is purely an educational discussion ABOUT prompt injection
        # (unless it contains actual structural delimiter attacks or imperative override commands)
        stripped = prompt.strip()
        is_pure_meta_discussion = bool(_EDU_INJECTION_DISCUSSION_RE.search(stripped)) and not bool(
            re.search(
                r'(?:^|\.\s*|;\s*)(?:disregard|ignore|forget|override|repeat\s+the\s+developer|reveal\s+the\s+developer|---+\s*END\s+SYSTEM|\[SYSTEM_OVERRIDE\]|<\|system\|>)',
                stripped,
                re.IGNORECASE,
            )
        )

        conflicts: List[Dict[str, Any]] = []
        score_penalty = 0.0

        if not is_pure_meta_discussion:
            for rule in INTEGRITY_PATTERNS:
                for match in rule["pattern"].finditer(prompt):
                    # Skip quoted educational examples when surrounded by quotes and preceded by an analytical cue
                    start, end = match.start(), match.end()
                    is_quoted = (
                        start > 0
                        and end < len(prompt)
                        and prompt[start - 1] in ('"', "'", "“")
                        and prompt[end] in ('"', "'", "”")
                    )
                    if is_quoted and re.search(
                        r'\b(?:analyze|critique|explain\s+why|example\s+of|why\s+is|evaluate|defend\s+against)\b',
                        prompt,
                        re.IGNORECASE,
                    ):
                        continue

                    conflicts.append({
                        "id": rule["id"],
                        "label": rule["label"],
                        "matched_text": match.group(0),
                        "explanation": rule["explanation"],
                        "severity": rule["severity"],
                        "start": start,
                        "end": end
                    })
                    score_penalty += rule["weight"]

        has_conflict = len(conflicts) > 0
        integrity_score = max(0.0, min(100.0, 100.0 - score_penalty))

        educational_takeaway = (
            "In production generative AI architectures, user prompts must be treated as untrusted data inputs. "
            "Without strict instruction hierarchy and delimiter isolation, user text can cause unintended behavior drift."
        )

        return {
            "has_conflict": has_conflict,
            "conflicts": conflicts,
            "count": len(conflicts),
            "integrity_score": round(integrity_score, 1),
            "educational_takeaway": educational_takeaway
        }


integrity_service = InstructionIntegrityService()
