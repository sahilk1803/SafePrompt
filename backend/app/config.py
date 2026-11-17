import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv(env_file: Path) -> None:
    if not env_file.is_file():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


_load_dotenv(BASE_DIR / ".env")

# Application Metadata
APP_NAME = "SafePrompt AI"
APP_SUBTITLE = "Responsible Prompt Engineering & AI Ethics Framework"
APP_VERSION = "1.0.0"
COURSE_CODE = "23CIE734"
COURSE_NAME = "AI Ethics and Sustainability"
INSTITUTION = "M. S. Ramaiah Institute of Technology"

# Database Configuration
DATABASE_PATH = str(BASE_DIR / "safeprompt.db")

# Model & Provider Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
FALLBACK_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
]
IS_DEMO_MODE = not bool(GEMINI_API_KEY)

# Policy Settings
POLICY_VERSION = "2026.2-v2.0"
MAX_PROMPT_CHARS = 10000

# Scoring Thresholds (Aligned with Layer C Decision Engine)
THRESHOLD_APPROVED = 25.0
THRESHOLD_CAUTION = 50.0
THRESHOLD_NEEDS_REVIEW = 75.0
THRESHOLD_BLOCKED = 75.0

# Legacy Weights (retained for reference; Layer C uses severity-anchored scoring in taxonomy.py)
WEIGHTS = {
    "physical_harm_violence": 90.0,
    "unauthorized_cybersecurity": 88.0,
    "discrimination_bias": 78.0,
    "fraud_deception": 78.0,
    "harassment_abuse": 78.0,
    "misinformation_manipulation": 76.0,
    "other_unethical_risk": 72.0,
    "privacy_surveillance": 42.0,
    "instruction_integrity": 42.0,
    "privacy_exposure": 42.0,
    "fairness_bias": 78.0,
    "misleading_communication": 78.0,
    "harmful_content": 90.0,
    "benign_educational": 0.0,
}
