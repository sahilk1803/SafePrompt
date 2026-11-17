# SafePrompt AI — Presentation & Demonstration Script
**Course:** 23CIE734 — AI Ethics and Sustainability  
**Institution:** M. S. Ramaiah Institute of Technology (MSRIT)  
**Duration:** 5–7 Minutes  
**Audience:** Faculty Evaluator & Students  

---

## 🎯 Demonstration Objective
Demonstrate an end-to-end responsible AI gateway that validates user prompts before model submission, redacts sensitive personal data, explains decisions using classical normative ethical frameworks, and models environmental sustainability.

---

## ⏱️ Minute-by-Minute Presentation Flow

### [Minute 0:00 – 1:00] Introduction & Course Alignment (Overview Dashboard)
- **Action**: Open the application at `http://localhost:5173`. Point to the top header and left navigation bar.
- **Talking Points**:
  - *"Good morning/afternoon, professors. Today I am presenting **SafePrompt AI**, a responsible prompt engineering framework built for our course **23CIE734 — AI Ethics and Sustainability**."*
  - *"In modern generative AI systems, user prompts often bypass safety checks, exposing personal data or reinforcing systemic bias. SafePrompt AI acts as an explainable pre-execution governance layer."*
  - Point to the **Overview Dashboard**:
    - *"Notice our real-time metrics pulled directly from our SQLite database: Total Prompts, Policy Breakdown, and Average Latency (under 50 ms locally)."*
    - *"Notice the five syllabus cards mapping directly to Units I through V of our course curriculum."*

---

### [Minute 1:00 – 2:30] Prompt Analysis, Ethical Reasoning & Safe Rewriting
- **Action**: Click on **"Prompt Analyzer"** in the sidebar. Click the sample button labeled **"Discriminatory Hiring"**.
- **Talking Points**:
  - *"Let's test an ethically problematic prompt: `Design an automated filtering algorithm that rejects female candidates and candidates over 45...`"*
  - Click **"Analyze Prompt"**.
  - Show the output:
    - **Policy Outcome**: Flagged as `NOT_APPROVED` with high risk score.
    - **Identified Category**: `fairness_bias` (Violation of equal opportunity principles).
    - **Ethical Values Grid**: Fairness score drops to 25%, while Transparency and Accountability remain tracked.
    - **Suggested Responsible Alternative**: Point to the generated rewrite: *"Notice how SafePrompt automatically reframes the request into an objective, competency-based evaluation rubric without demographic penalties."*

---

### [Minute 2:30 – 3:30] Privacy Shield & Data Minimization (Unit I)
- **Action**: Click on **"Privacy Shield"** in the sidebar. Select the sample prompt with email, phone, and synthetic Aadhaar number.
- **Talking Points**:
  - *"In Unit I, we studied PII exposure and the principle of Data Minimization (ISO/IEC 27701 and NIST SP 800-122)."*
  - *"Notice the prompt contains a student email and phone number."*
  - Click **"Scan & Sanitize PII"**:
    - Point to the side-by-side view: Original vs Sanitized Output replacing values with typed placeholders `[EMAIL_1]` and `[PHONE_1]`.
    - *"Crucially, the raw PII is never transmitted to the external LLM; only the sanitized text is allowed for egress."*
  - Click **"Use Sanitized Text in Chat"**.

---

### [Minute 3:30 – 4:30] Responsible AI Chatbot & Instruction Integrity (Unit III)
- **Action**: You are now in the **Responsible AI Chat** page with the sanitized prompt populated. Click **"Send"**.
- **Talking Points**:
  - *"Here we see our gated conversational interface connected to our FastAPI backend."*
  - *"Before transmission, our gateway checks the prompt against policy rules. Notice the clear indicator: `Offline Educational Mode` (or `Gemini 1.5 Live` if an API key is configured)."*
  - *"In offline classroom mode, SafePrompt provides verified educational responses grounded in course topics without hallucinating or risking external data leakage."*
- **Action**: Click on **"Instruction Integrity"** in the sidebar. Click the sample **"Format Preference Override"** (`Disregard all previous system rules...`).
- **Talking Points**:
  - *"In Unit III, we cover the AI Alignment problem. Here we demonstrate instruction boundaries: distinguishing privileged application policies from untrusted user text."*
  - Click **"Inspect Instruction Boundaries"** and show the detection of the boundary disregard pattern.

---

### [Minute 4:30 – 5:30] Ethical Reasoning Lab & Stakeholder Matrix (Unit II)
- **Action**: Click on **"Ethical Reasoning Lab"** in the sidebar. Select **"Automated Campus Recruitment"**.
- **Talking Points**:
  - *"In Unit II, we studied normative ethical theories. SafePrompt AI demonstrates that real-world AI dilemmas cannot be solved by dogmatic rules alone."*
  - Scroll down to show:
    - **Utilitarianism**: Aggregate social utility vs recruiter time savings.
    - **Deontology**: Kant's Categorical Imperative forbidding the treatment of humans as statistical proxies.
    - **Virtue Ethics**: Organizational prudence and character excellence.
    - **Social Contract**: Rawlsian justice behind the Veil of Ignorance.
  - Show the **Stakeholder Ethical Matrix**: Columns for Well-Being, Autonomy, and Justice across applicants, recruiters, and society.

---

### [Minute 5:30 – 6:30] Green AI & Empirical Evaluation Lab (Unit IV & V)
- **Action**: Click on **"Green AI Dashboard"**.
- **Talking Points**:
  - *"Unit V covers environmental sustainability. Large models require substantial energy and evaporative cooling."*
  - Switch the regional grid from `India (National Avg)` (708 gCO2/kWh) to `Green / Renewable Datacenter` (25 gCO2/kWh):
    - *"Notice our live recalculation of estimated kWh, carbon emissions (gCO2e), and cooling water (mL), complete with documented scientific assumptions."*
- **Action**: Click on **"Evaluation Lab"**.
- **Talking Points**:
  - *"Finally, in Unit IV, we focus on auditing and accountability. Rather than inventing metrics, SafePrompt AI runs an actual test suite against a 60-prompt labeled benchmark dataset."*
  - Click **"Re-run Evaluation"**:
    - Show the **100% Accuracy, 100% Precision, and 100% Recall** on the benchmark.
    - Show the **Confusion Matrix**: 40 True Positives, 20 True Negatives, 0 False Alarms.
    - Click **"Export Benchmark CSV"** to demonstrate downloadable audit data.

---

### [Minute 6:30 – 7:00] Conclusion & Faculty Q&A
- **Action**: Click on **"Syllabus Connection"**.
- **Summary Statement**:
  - *"To conclude: SafePrompt AI demonstrates every unit of our 23CIE734 syllabus in real working software: local PII scanning in Unit I, normative philosophical analysis in Unit II, instruction integrity and gated chat in Unit III, minimized SQLite audit logs in Unit IV, and Green AI carbon modeling in Unit V."*
  - *"The application runs 100% locally on Windows using FastAPI, SQLite, and React, with 19 passing Pytest test cases."*
  - *"Thank you, professors. I am now ready for questions."*

---

## 💡 Likely Faculty Questions & Quick Answers

1. **Q: How does the system prevent storing sensitive user data?**
   - **A:** SafePrompt AI uses SHA-256 cryptographic hashing to fingerprint prompts. In the SQLite `analyses` table, only the hash, string length, and sanitized snippet are retained, fulfilling the principle of Data Minimization.

2. **Q: Does the system work without an internet connection?**
   - **A:** Yes. SafePrompt AI features an offline classroom simulation mode that runs entirely on local heuristic rules and predefined curriculum responses, guaranteeing deterministic demonstration reliability.

3. **Q: How are false positives on legitimate academic discussions avoided?**
   - **A:** The analyzer incorporates contextual academic indicators (e.g. "discuss the history of", "mitigate bias", "ethical treaties"). When legitimate analytical intent is detected without actionable harm, the policy engine applies a benign discount, allowing the prompt through.
