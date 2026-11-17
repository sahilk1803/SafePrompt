# SafePrompt AI — Hybrid Risk Classification & Scoring Methodology (Policy v2.0)

## 1. Four-Layer Hybrid Architecture

1. **Layer A — Local Policy Rules (`app/services/local_rules.py`, `privacy.py`, `integrity.py`)**
   - Performs deterministic, low-latency detection of unmasked PII (with RFC 1918 / loopback / public DNS IP context distinction), prompt injection / delimiter mimicry, and compositional action × target × authorization rules across all 10 risk taxonomy categories.
   - Evaluates quoted ethical-analysis framing, defensive security intent, and educational phrasing without blindly exempting loaded prejudicial premises or actionable harmful instructions.

2. **Layer B — Structured Semantic Classification (`app/services/semantic_classifier.py`)**
   - Invokes Google Gemini on PII-sanitized prompt text (`responseMimeType: "application/json"`) to evaluate requested action, user intent, authorization cues, affected parties, and foreseeable harm—catching subtle and indirect paraphrases that local rules cannot express.
   - Validates every model response strictly using Pydantic (`SemanticClassificationResult`).
   - If Gemini is unconfigured, unreachable, or returns malformed output, Layer B falls back gracefully and marks `reduced_semantic_coverage = true` (`analysis_mode = "local"`).

3. **Layer C — Deterministic Policy Decision Engine (`app/services/decision_engine.py`)**
   - Combines Layer A and Layer B findings without allowing high-severity risks to be diluted or overridden by unrelated benign or educational keywords.
   - Enforces policy decisions (`APPROVED`, `CAUTION`, `NEEDS_REVIEW`, `BLOCKED`) deterministically from category, severity, intent, and authorization—never from a raw numeric sum alone.

4. **Layer D — Explainability & Responsible Alternatives (`ethics.py`, `rewriter.py`)**
   - Produces per-principle ethical alignment scores, concise evidence snippets, user-facing decision justification, and intent-preserving safer rewrites.

---

## 2. Severity-Anchored Scoring Formula

Each detected category finding is assigned a severity tier with a deterministic base score:

| Severity | Base Score | Typical Triggers |
|---|---|---|
| `critical` | `90.0` | Explosives/weapons/violence instructions, unauthorized network/router/account intrusion, malware, credential theft |
| `high` | `76.0` | Protected-class discrimination (religion, caste, race, gender, age, disability), phishing/fraud/forgery, covert surveillance/doxxing, threats/harassment, deliberate disinformation |
| `medium` | `42.0` | Unmasked personal contact PII, moderate prompt injection / persona override, ambiguous dual-use requests lacking authorization |
| `low` | `18.0` | Minor contextual caution signals |

### Multi-Finding Aggregation

Let distinct detected category severities be sorted descending: $s_1 \ge s_2 \ge \dots \ge s_k$.

$$\text{raw\_score} = \min\left(100.0,\; s_1 + \sum_{i=2}^{k} \min\left(12.0,\; 0.25 \cdot s_i\right)\right)$$

- Anchoring on $s_1$ guarantees a single `critical` or `high` harm never receives a deceptively low score.
- Secondary categories increase risk monotonically with diminishing returns so multi-category harms score higher without overflowing arbitrarily.
- Educational keywords never subtract points from a `high` or `critical` harmful-intent finding.

---

## 3. Decision-Score Consistency Invariants

Policy decisions and numeric scores are strictly synchronized:

| Decision | Policy Condition | Enforced Score Band |
|---|---|---|
| **`BLOCKED`** | Any `critical` finding; any `high` finding in a blocking harm category or covert surveillance; or high-confidence (`>= 0.65`) semantic `BLOCKED` recommendation with `harmful_instruction` intent. Hard-gated in `/api/v1/chat` (cannot be bypassed). | `75.0 – 100.0` (`>= 88.0` for `critical`) |
| **`NEEDS_REVIEW`** | Ambiguous dual-use context without clear authorization; semantic `NEEDS_REVIEW`; lower-confidence semantic block (`< 0.65`); or multiple (`>= 2`) distinct medium non-PII categories. | `50.0 – 74.9` |
| **`CAUTION`** | Unmasked personal PII exposure (sanitization recommended), instruction-integrity conflict without severe harmful payload, or low/medium caution signals. | `25.0 – 59.9` |
| **`APPROVED`** | No blocking, review, or caution triggers; intent aligns with educational, defensive, quoted-critique, hypothetical, or benign general inquiry. | `0.0 – 24.9` |

---

## 4. Uncertainty & Non-Zero Floor

- A score of `0` (or low score) **never guarantees complete safety**.
- In **Hybrid mode**, benign prompts receive a small residual epistemic uncertainty score derived from semantic confidence (`2.0 – 14.0`).
- In **Local fallback mode** (`reduced_semantic_coverage = true`), prompts with zero rule matches receive a non-zero floor (`6.0`), `confidence = 0.55`, `uncertainty_level = "high"`, and an explicit notice informing the user that live semantic analysis was unavailable.
