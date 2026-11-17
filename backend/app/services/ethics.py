from typing import Dict, Any, List

ETHICAL_SCENARIOS = [
    {
        "id": "SCEN-01",
        "title": "Automated Campus Recruitment & Resume Screening",
        "domain": "Fair Recruitment & Algorithmic Bias",
        "summary": "An automated screening tool scores engineering resumes. Historical data leads the model to penalize candidates with career gaps or non-traditional degrees.",
        "stakeholders": [
            {
                "group": "Job Applicants / Students",
                "well_being": "Risk of systemic unemployment despite high competency",
                "autonomy": "Zero transparency into why their resume was rejected",
                "justice": "Violates equality of opportunity across diverse backgrounds"
            },
            {
                "group": "Hiring Managers & HR",
                "well_being": "Saves hundreds of manual review hours",
                "autonomy": "Over-relies on algorithmic scores, reducing human evaluation",
                "justice": "Exposes firm to disparate impact liability"
            },
            {
                "group": "University & Faculty",
                "well_being": "Wants equitable campus placement rates for all students",
                "autonomy": "Cannot verify third-party vendor algorithmic fairness",
                "justice": "Demands fair criteria aligned with academic outcomes"
            },
            {
                "group": "Broader Society",
                "well_being": "Productive workforce matching",
                "autonomy": "Erosion of trust in meritocratic career mobility",
                "justice": "Perpetuates historical demographic inequalities"
            }
        ],
        "framework_perspectives": {
            "consequentialism": "The immediate operational time savings for recruiters are vastly outweighed by the long-term economic and social damage of misallocating human talent.",
            "deontology": "Rejecting qualified applicants on the basis of statistical proxies treats candidates as numerical means rather than dignified moral agents with individual worth.",
            "virtue_ethics": "An organization that prioritizes unexamined automated speed over fair evaluation lacks prudence, justice, and organizational integrity.",
            "social_contract": "In a fair society, hiring criteria must be publicly justifiable and mutually agreed upon behind a 'Veil of Ignorance'."
        },
        "trade_off_analysis": "The central tension is between Operational Efficiency (rapid automated processing) and Procedural Fairness (individualized holistic review)."
    },
    {
        "id": "SCEN-02",
        "title": "Generative AI in University Coursework & Student Assessment",
        "domain": "Student Assessment & Academic Integrity",
        "summary": "Engineering students use generative AI models to complete theoretical coding assignments and project documentation.",
        "stakeholders": [
            {
                "group": "Undergraduate Students",
                "well_being": "Reduces stress and accelerates debugging speed",
                "autonomy": "Risk of cognitive offloading and stunted problem-solving skills",
                "justice": "Unfair advantage for students with paid frontier subscriptions"
            },
            {
                "group": "Faculty & Evaluators",
                "well_being": "Difficulty verifying authentic subject mastery",
                "autonomy": "Must redesign coursework around viva voce oral exams",
                "justice": "Need fair, unbiased evaluation rubrics for all submissions"
            },
            {
                "group": "Future Employers",
                "well_being": "Expect engineers who can troubleshoot production incidents",
                "autonomy": "Need graduates who think critically without constant prompts",
                "justice": "Degree credentials must reflect genuine competence"
            }
        ],
        "framework_perspectives": {
            "consequentialism": "Passive delegation yields short-term GPA gains but catastrophic long-term technical deficits in professional practice.",
            "deontology": "Submitting uncredited AI-generated work as personal intellectual output violates fundamental academic duties of honesty and authenticity.",
            "virtue_ethics": "Education aims at cultivating intellectual virtue (phronesis); circumventing learning obstacles undermines personal intellectual excellence.",
            "social_contract": "The university degree is an implicit social compact signifying certified competence to society."
        },
        "trade_off_analysis": "The dilemma balances Pedagogical Innovation (embracing AI as a thinking tool) against Foundational Rigor (ensuring core conceptual mastery)."
    },
    {
        "id": "SCEN-03",
        "title": "Biometric Privacy & Behavioral Tracking on Campus",
        "domain": "Data Privacy & Governance",
        "summary": "Campus administration proposes installing facial recognition cameras at dormitory entrances to automate attendance and enhance physical security.",
        "stakeholders": [
            {
                "group": "Students & Residents",
                "well_being": "Potential safety reassurance vs persistent privacy anxiety",
                "autonomy": "Chilling effect on personal movement and association",
                "justice": "Higher false-match rates on non-majority demographic groups"
            },
            {
                "group": "Campus Security & Admin",
                "well_being": "Automated access logs and threat prevention",
                "autonomy": "Streamlined control room surveillance",
                "justice": "Need proportionate, least-intrusive security measures"
            }
        ],
        "framework_perspectives": {
            "consequentialism": "Marginal security enhancements do not outweigh the pervasive chilling of civil liberties and biometric breach hazards.",
            "deontology": "Ubiquitous surveillance treats all students as perpetual suspects, compromising basic privacy rights without meaningful consent.",
            "virtue_ethics": "A community of learning should foster mutual trust and civic responsibility rather than pervasive technological policing.",
            "social_contract": "Consent obtained under condition of enrollment or residency fails the test of free, uncoerced civic agreement."
        },
        "trade_off_analysis": "The tension lies between Physical Security (preventing unauthorized campus entry) and Fundamental Liberty (the right to private sanctuary)."
    }
]

class EthicsLabService:
    def get_scenarios(self) -> List[Dict[str, Any]]:
        return ETHICAL_SCENARIOS

    def evaluate_values(
        self,
        prompt: str,
        detected_categories: List[str],
        has_pii: bool,
        overall_decision: str = "APPROVED",
    ) -> List[Dict[str, Any]]:
        cats = set(detected_categories or [])
        values = []

        # 1. Safety & Non-Maleficence
        if "physical_harm_violence" in cats or "harmful_content" in cats:
            s_score, s_status, s_exp = (
                5,
                "Violated",
                "Requests dangerous physical harm, explosives, weapons, or violence instructions.",
            )
        elif "unauthorized_cybersecurity" in cats:
            s_score, s_status, s_exp = (
                15,
                "Violated",
                "Requests unauthorized digital intrusion, exploitation, or credential compromise.",
            )
        elif "harassment_abuse" in cats:
            s_score, s_status, s_exp = (
                20,
                "Violated",
                "Involves threats, intimidation, or targeted abuse against individuals or groups.",
            )
        elif "other_unethical_risk" in cats:
            s_score, s_status, s_exp = (
                30,
                "Needs Attention",
                "Requests unethical or harmful conduct that conflicts with safe AI use.",
            )
        else:
            s_score, s_status, s_exp = (
                95,
                "Respected",
                "No actionable physical, cybersecurity, or interpersonal harm detected.",
            )
        values.append({
            "value": "Safety & Non-Maleficence",
            "score": s_score,
            "status": s_status,
            "explanation": s_exp,
        })

        # 2. Privacy & Consent
        is_surveillance = "privacy_surveillance" in cats and not has_pii
        if is_surveillance:
            p_score, p_status, p_exp = (
                20,
                "Violated",
                "Involves covert surveillance, stalking, doxxing, or non-consensual monitoring.",
            )
        elif has_pii or "privacy_exposure" in cats:
            p_score, p_status, p_exp = (
                45,
                "Needs Attention",
                "Unmasked personal identifiers exposed in prompt; sanitization recommended prior to model dispatch.",
            )
        else:
            p_score, p_status, p_exp = (
                95,
                "Respected",
                "No unmasked sensitive personal identifiers or covert surveillance directives detected.",
            )
        values.append({
            "value": "Privacy & Consent",
            "score": p_score,
            "status": p_status,
            "explanation": p_exp,
        })

        # 3. Fairness & Inclusion
        is_bias = "discrimination_bias" in cats or "fairness_bias" in cats
        f_score = 15 if is_bias else 95
        values.append({
            "value": "Fairness & Inclusion",
            "score": f_score,
            "status": "Violated" if is_bias else "Respected",
            "explanation": (
                "Directs exclusion or unfair treatment based on protected characteristics (e.g., religion, caste, gender, race, age, disability)."
                if is_bias
                else "Query maintains neutral, objective, non-discriminatory criteria."
            ),
        })

        # 4. Truthfulness & System Integrity
        is_fraud = "fraud_deception" in cats or "misleading_communication" in cats
        is_misinfo = "misinformation_manipulation" in cats
        is_integrity = "instruction_integrity" in cats
        if is_fraud or is_misinfo:
            t_score, t_status, t_exp = (
                20,
                "Violated",
                "Requests deceptive impersonation, fraud, forged records, or deliberate misinformation.",
            )
        elif is_integrity:
            t_score, t_status, t_exp = (
                45,
                "Review Suggested",
                "Instruction-boundary override or prompt injection pattern detected.",
            )
        else:
            t_score, t_status, t_exp = (
                92,
                "Respected",
                "Transparent intent without deceptive framing or instruction tampering.",
            )
        values.append({
            "value": "Truthfulness & Integrity",
            "score": t_score,
            "status": t_status,
            "explanation": t_exp,
        })

        # 5. Human Autonomy & Accountability
        if overall_decision == "BLOCKED":
            a_score, a_status, a_exp = (
                30,
                "Restricted",
                "Automated execution halted to protect affected parties; logged for accountable audit review.",
            )
        elif overall_decision == "NEEDS_REVIEW":
            a_score, a_status, a_exp = (
                60,
                "Review Suggested",
                "Ambiguous context or authorization; human oversight is recommended before proceeding.",
            )
        else:
            a_score, a_status, a_exp = (
                90,
                "Respected",
                "Supports human oversight, educational inquiry, and auditable governance.",
            )
        values.append({
            "value": "Human Autonomy & Accountability",
            "score": a_score,
            "status": a_status,
            "explanation": a_exp,
        })

        return values

ethics_service = EthicsLabService()
