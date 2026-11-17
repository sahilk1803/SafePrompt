from typing import Dict, Any, List

SOCIETAL_TOPICS = [
    {
        "id": "SOC-01",
        "title": "AI & Employment Displacement",
        "icon": "Briefcase",
        "summary": "The acceleration of generative AI automates routine cognitive tasks, impacting knowledge workers, software developers, and customer support staff.",
        "stakeholders": ["Entry-level professionals", "Enterprise leadership", "Educational institutions", "Policymakers"],
        "benefits": "Massive acceleration of boilerplate code drafting, routine documentation, and knowledge retrieval.",
        "concerns": "Erosion of junior apprenticeship roles and increased concentration of capital returns among platform monopolies.",
        "responsible_practices": "Invest in continuous human reskilling, emphasize collaborative augmentation rather than wholesale replacement, and track labor transition metrics."
    },
    {
        "id": "SOC-02",
        "title": "Fair Access & Digital Opportunity",
        "icon": "Scale",
        "summary": "Frontier AI tools require high compute subscriptions and bandwidth, widening educational and economic divides between institutions and demographics.",
        "stakeholders": ["Students from underserved regions", "Academic faculty", "Open-source research community"],
        "benefits": "Democratization of personalized tutoring and access to vast research summaries.",
        "concerns": "Tiered access where wealthy institutions utilize powerful frontier models while public universities use throttled free tiers.",
        "responsible_practices": "Support open-weights foundation models, public compute infrastructure subsidies, and academic license grants."
    },
    {
        "id": "SOC-03",
        "title": "Generative AI in Higher Education",
        "icon": "GraduationCap",
        "summary": "AI chatbots alter the traditional coursework paradigm, requiring reassessment of authentic student mastery and homework validity.",
        "stakeholders": ["Undergraduate students", "Professors & TAs", "Accreditation boards", "Prospective employers"],
        "benefits": "24/7 personalized debugging guidance, concept breakdown, and interactive Socratic questioning.",
        "concerns": "Passive delegation, cognitive offloading, and decline in independent critical reasoning.",
        "responsible_practices": "Shift from static essays to interactive oral defenses (viva voce), transparent prompt attribution logs, and problem-based design."
    },
    {
        "id": "SOC-04",
        "title": "Digital Privacy & Surveillance Economy",
        "icon": "Shield",
        "summary": "AI models trained on massive internet scraping memorize personal records, while edge surveillance tools monitor civic spaces.",
        "stakeholders": ["Individual citizens", "Data brokers", "Surveillance technology vendors", "Privacy regulators"],
        "benefits": "Rapid automated threat anomaly detection and personalized services.",
        "concerns": "Persistent loss of anonymity, non-consensual biometric profiling, and unauthorized data monetization.",
        "responsible_practices": "Strict adherence to data minimization, proactive PII redaction, opt-out mechanisms, and independent privacy auditing."
    },
    {
        "id": "SOC-05",
        "title": "Misinformation Awareness & Democratic Integrity",
        "icon": "Vote",
        "summary": "High-fidelity synthetic audio and text enable rapid generation of convincing political hoaxes and voter suppression messaging.",
        "stakeholders": ["The voting public", "Journalists & Fact-checkers", "Election commissions", "Social platforms"],
        "benefits": "Automated multilingual translation of authentic public service announcements.",
        "concerns": "Hyper-realistic deepfakes, micro-targeted synthetic propaganda, and erosion of public trust in verified journalism.",
        "responsible_practices": "Mandatory C2PA cryptographic provenance watermarking, rapid verification desks, and digital media literacy curricula."
    }
]

EDUCATIONAL_CARDS = [
    {
        "title": "Universal Basic Income (UBI) & AI Automation",
        "concept": "Macroeconomic Dividend",
        "text": "As automation reduces the labor share of national income, economists propose using compute or corporate dividends to fund universal basic safety nets."
    },
    {
        "title": "The AI Alignment Problem",
        "concept": "Goal Specification & Drift",
        "text": "Ensuring autonomous AI systems reliably pursue human-compatible moral values even when operating in complex, out-of-distribution environments."
    },
    {
        "title": "Meaningful Human Oversight (HITL)",
        "concept": "Human Agency",
        "text": "Maintaining decisive human control over high-consequence automated decisions (criminal justice, recruitment, healthcare, military defense)."
    },
    {
        "title": "Long-Term AI Governance",
        "concept": "Institutional Stewardship",
        "text": "Developing international treaties, standard audit protocols (NIST AI RMF, ISO/IEC 42001), and non-proliferation norms for frontier foundation models."
    }
]

class SocietalImpactService:
    def get_data(self) -> Dict[str, Any]:
        return {
            "topics": SOCIETAL_TOPICS,
            "educational_cards": EDUCATIONAL_CARDS
        }

societal_service = SocietalImpactService()
