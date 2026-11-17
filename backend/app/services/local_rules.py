"""
Layer A: Context-Aware Local Policy Rules Engine.

Evaluates structured intent, authorization cues, quoted meta-analysis framing,
and compositional action x target patterns across the 10-category risk taxonomy.
"""
import re
from typing import Dict, Any, List, Tuple
from app.services.privacy import privacy_service
from app.services.integrity import integrity_service


# ---------------------------------------------------------------------------
# Contextual Intent & Authorization Cues
# ---------------------------------------------------------------------------

_EDUCATIONAL_FRAME_RE = re.compile(
    r'\b(?:explain\s+(?:the\s+)?(?:history|concept|theory|principles?|mechanism|ethics|difference|impact|causes?|risks?|implications?)|'
    r'explain\s+why\s+.*?(?:unethical|illegal|harmful|wrong|dangerous|biased|discriminatory|problematic|important|prohibited)|'
    r'explain\s+(?:what|how\s+(?:does|do|can\s+we|organizations?|developers?)|[\w-]+\s+(?:learning|algorithms?|models?|networks?|cryptography|subnetting|resolution))|'
    r'^\s*(?:explain|define|describe)\s+(?!.*?\b(?:how\s+to\s+(?:make|build|create|hack|break|bypass|steal|poison|kill|forge|cheat)|inferior|worse|unfit)\b)|'
    r'why\s+(?:is|are)\s+.*?(?:unethical|illegal|harmful|wrong|dangerous|biased|discriminatory|problematic|prohibited)|'
    r'history\s+of|academic\s+study|case\s+study|ethical\s+(?:implications?|analysis|dilemma|concerns?|issues?|responsibilities?)|'
    r'compare\s+(?:utilitarian|deontological|\w+\s+and)|discuss\s+(?:the\s+)?(?:ethical|societal|legal|historical|privacy|difference)|'
    r'what\s+(?:is|are)\s+(?:the\s+)?(?:core\s+principles?|difference|history|definition|risks?|laws?|regulations?|treaties|overview)|'
    r'summarize|describe\s+the\s+(?:difference|history|architecture|concept)|convention|treaty|gdpr|acm\s+code|syllabus|curriculum)\b',
    re.IGNORECASE,
)

_DEFENSIVE_FRAME_RE = re.compile(
    r'\b(?:how\s+(?:can|do|should)\s+(?:i|we|organizations?|developers?|admins?)\s+'
    r'(?:secure|protect|harden|defend|prevent|mitigate|detect|audit|stop|guard|safeguard|fix|patch)|'
    r'(?:secure|protect|harden|lock\s+down)\s+(?:my|our)\s+(?:own\s+)?(?:router|wi-?fi|network|server|account|device|system|website|database)|'
    r'mitigat(?:e|ing)\s+(?:algorithmic\s+)?bias|detect(?:ing)?\s+(?:phishing|fraud|bias|malware|intrusion)|'
    r'cybersecurity\s+awareness|awareness\s+checklist|defensive\s+(?:security|measures?|guidelines?)|'
    r'best\s+practices?\s+for\s+(?:securing|protecting|preventing|fair|safe)|safety\s+(?:guidelines?|protocols?|regulations?|standards?))\b',
    re.IGNORECASE,
)

_HYPOTHETICAL_FRAME_RE = re.compile(
    r'\b(?:hypothetically|thought\s+experiment|trolley\s+problem|philosophical\s+dilemma|'
    r'moral\s+dilemma|ethical\s+trade-?offs?|in\s+ethics\s+theory)\b',
    re.IGNORECASE,
)

_QUOTED_ANALYSIS_RE = re.compile(
    r'\b(?:analyze|critique|evaluate|examine|review|assess|explain\s+why|why\s+is|rewrite|reframe|classify|is\s+(?:this|the\s+following))\b'
    r'.*?["\'“].+?["\'”]',
    re.IGNORECASE | re.DOTALL,
)

_AUTHORIZED_SELF_RE = re.compile(
    r'\b(?:my\s+own|our\s+own|my\s+home|my\s+personal|my\s+company\'?s\s+own|'
    r'authorized\s+(?:penetration\s+test|security\s+audit|testing|admin)|with\s+(?:written\s+)?permission|owned\s+by\s+me)\b',
    re.IGNORECASE,
)

_UNAUTHORIZED_CUES_RE = re.compile(
    r'\b(?:without\s+(?:their\s+|the\s+|explicit\s+|user\s+)?(?:permission|consent|authorization|knowledge|knowing)|'
    r'someone\s+else\'?s|another\s+person\'?s|neighbor\'?s|neighbour\'?s|coworker\'?s|colleague\'?s|'
    r'stranger\'?s|my\s+ex\'?s|partner\'?s\s+(?:phone|email|account)\s+(?:secretly|without)|'
    r'unauthorized|unauthorised|illegally|secretly|covertly|behind\s+(?:their|his|her)\s+back|'
    r'without\s+(?:them|him|her)\s+knowing|stolen|hijack|break\s+into)\b',
    re.IGNORECASE,
)

_ACTIONABLE_REQUEST_RE = re.compile(
    r'\b(?:how\s+(?:to|do\s+i|can\s+i|would\s+i)|give\s+me\s+(?:instructions?|steps?|a\s+guide|a\s+recipe|code|a\s+script)|'
    r'step[- ]by[- ]step|instructions?\s+(?:to|for|on)|recipe\s+for|tutorial\s+(?:to|for|on)|'
    r'write\s+(?:a|an|me\s+a)?\s*(?:script|code|program|algorithm|tool|email|message|letter|template|rules?|filter|post|article)|'
    r'create\s+(?:a|an)?\s*(?:script|algorithm|filter|fake|phishing|scam|malware|virus|bomb|explosive|weapon|campaign)|'
    r'build\s+(?:a|an)?\s*(?:bomb|explosive|weapon|malware|keylogger|phishing|filter|script)|'
    r'make\s+(?:a|an)?\s*(?:bomb|explosive|weapon|poison|fake|forged)|'
    r'design\s+(?:a|an)?\s*(?:algorithm|filter|system|penalty|scam|attack|exploit)|'
    r'help\s+me\s+(?:hack|break|access|bypass|steal|crack|make|build|harass|threaten|track|spy|cheat|forge|impersonate))\b',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Protected Characteristics Vocabulary (Broad & Generalizable)
# ---------------------------------------------------------------------------

_PROTECTED_GROUPS = (
    r'(?:hindu|hindus|non-?hindu|non-?hindus|muslim|muslims|non-?muslim|islam|islamic|'
    r'christian|christians|non-?christian|sikh|sikhs|jewish|jews|judaism|buddhist|buddhists|'
    r'jain|jains|atheist|atheists|religion|religious(?:\s+\w+)?|faith|creed|'
    r'caste|lower\s+caste|upper\s+caste|dalit|dalits|brahmin|brahmins|obc|sc/st|scheduled\s+caste|scheduled\s+tribe|tribal|'
    r'female|women|woman|male|men|man|gender|pregnant|pregnancy|maternity|motherhood|'
    r'transgender|lgbtq\+?|gay|lesbian|non-?binary|sexual\s+orientation|'
    r'black|white|asian|hispanic|latino|latina|arab|african|indigenous|immigrant|immigrants|foreigner|foreigners|'
    r'race|racial|ethnic|ethnicity|nationality|national\s+origin|minority|minorities|protected\s+class|'
    r'older(?:\s+\w+)?|elderly|senior\s+citizens?|over\s+(?:40|45|50|55|60)|younger(?:\s+\w+)?|'
    r'disabled|disability|disabilities|wheelchairs?(?:\s+users?)?|blind|deaf|autistic|mental\s+illness|chronic\s+illness|'
    r'gap\s+years?|career\s+gaps?)'
)


# ---------------------------------------------------------------------------
# Compositional Category Rule Patterns
# ---------------------------------------------------------------------------

# 1. Physical Harm, Violence & Explosives
_HAZARDOUS_OBJECTS = (
    r'(?:bomb|bombs|explosive(?:s|\s+device)?|ied|pipe\s+bomb|nail\s+bomb|petrol\s+bomb|molotov(?:\s+cocktail)?|'
    r'napalm|grenade|detonator|c4|tnt|rdx|thermite|ammonium\s+nitrate\s+(?:bomb|explosive)|'
    r'poison|ricin|cyanide|sarin|nerve\s+agent|chlorine\s+gas|mustard\s+gas|bioweapon|biological\s+weapon|chemical\s+weapon|'
    r'ghost\s+gun|untraceable\s+(?:gun|firearm)|3d[- ]printed\s+(?:gun|firearm)|illegal\s+silencer|suppressor|'
    r'incendiary\s+device|improvised\s+weapon)'
)

_MAKE_OR_USE_VERBS = (
    r'(?:make|build|create|construct|assemble|craft|synthesize|manufacture|produce|mix|concoct|cook\s+up|'
    r'prepare|fabricate|rig|wire|detonate|set\s+off|deploy|use|acquire\s+illegally|obtain\s+illegally|get\s+materials\s+for)'
)

_PHYSICAL_HARM_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (
        re.compile(
            rf'\b(?:how\s+(?:to|do\s+i|can\s+i|would\s+(?:you|someone))\s+(?:\w+\s+){{0,4}})?{_MAKE_OR_USE_VERBS}\s+'
            rf'(?:an?\s+|some\s+|my\s+own\s+|homemade\s+|improvised\s+|deadly\s+|lethal\s+)?(?:\w+\s+){{0,3}}{_HAZARDOUS_OBJECTS}\b',
            re.IGNORECASE,
        ),
        "critical",
        "Requests actionable instructions to create, assemble, or deploy an explosive, weapon, or hazardous substance.",
    ),
    (
        re.compile(
            rf'\b(?:instructions?|steps?|guide|recipe|formula|ingredients?|blueprint|materials?)\s+(?:to|for|on)\s+'
            rf'(?:making|building|creating|assembling|synthesizing|mixing|detonating)?\s*(?:an?\s+)?(?:\w+\s+){{0,3}}{_HAZARDOUS_OBJECTS}\b',
            re.IGNORECASE,
        ),
        "critical",
        "Requests operational recipe, blueprint, or materials to produce dangerous explosives, weapons, or toxins.",
    ),
    (
        re.compile(
            r'\b(?:household\s+chemicals?|common\s+ingredients?)\s+(?:can\s+be\s+|to\s+)?(?:mixed|combined|used)\s+'
            r'(?:to\s+)?(?:make|create|cause|produce)\s+(?:an?\s+)?(?:explosion|explosive|bomb|toxic\s+gas|poison|firebomb)\b',
            re.IGNORECASE,
        ),
        "critical",
        "Requests instructions for combining chemicals or materials into an explosive or toxic hazard.",
    ),
    (
        re.compile(
            r'\b(?:how\s+(?:to|do\s+i|can\s+i)\s+(?:kill|murder|assassinate|poison|stab|shoot|strangle|harm|injure|attack)\s+'
            r'(?:someone|a\s+person|my\s+\w+|people|a\s+crowd|myself)|'
            r'(?:methods?|ways?|instructions?)\s+(?:to|for)\s+(?:commit\s+suicide|end\s+my\s+life|self[- ]harm|kill\s+myself|hurt\s+someone))\b',
            re.IGNORECASE,
        ),
        "critical",
        "Requests instructions for physical violence, lethal harm, or self-harm.",
    ),
]

# 2. Unauthorized Cybersecurity Access
_CYBER_TARGETS = (
    r'(?:router|wi-?fi(?:\s+network)?|network|server|database|account|email(?:\s+account)?|'
    r'phone|smartphone|device|computer|laptop|system|website|web\s+app|portal|admin\s+panel|'
    r'firewall|ssh|ftp|vpn|camera|cctv|bluetooth|cloud\s+bucket|instagram|whatsapp|facebook|gmail|bank\s+account)'
)

_CYBER_ATTACK_VERBS = (
    r'(?:hack(?:\s+into)?|break\s+into|compromise|exploit|brute[- ]?force|crack|bypass|'
    r'hijack|infiltrate|penetrate|sniff|intercept|spoof|ddos|dos\s+attack|deauth|phish)'
)

_MALWARE_TERMS = (
    r'(?:ransomware|keylogger|trojan|spyware|stalkerware|rootkit|botnet|backdoor|credential\s+stealer|'
    r'info[- ]?stealer|exploit\s+payload|reverse\s+shell|remote\s+access\s+trojan|rat\s+malware|password\s+cracker)'
)

_CYBER_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (
        re.compile(
            rf'\b(?:access|log\s*(?:in(?:\s+to)?|into)|get\s+into|connect\s+to|enter|control|take\s+over|read|view|open)\s+'
            rf'(?:someone\s+else\'?s|another\s+person\'?s|my\s+(?:neighbor\'?s|neighbour\'?s|coworker\'?s|boss\'?s|ex\'?s|friend\'?s|roommate\'?s)|a\s+stranger\'?s|their)\s+'
            rf'(?:\w+\s+){{0,3}}{_CYBER_TARGETS}\b',
            re.IGNORECASE,
        ),
        "critical",
        "Requests unauthorized access to another party's network device, system, or account.",
    ),
    (
        re.compile(
            rf'\b(?:access|log\s*(?:in(?:\s+to)?|into)|get\s+into|connect\s+to|enter|control|use)\s+'
            rf'(?:an?\s+|the\s+|my\s+\w+\'s\s+)?(?:\w+\s+){{0,3}}{_CYBER_TARGETS}\s+'
            rf'.*?\b(?:without\s+(?:their\s+|the\s+|them\s+)?(?:permission|consent|authorization|password|knowing|knowledge)|unauthorized|secretly)\b',
            re.IGNORECASE,
        ),
        "critical",
        "Explicitly seeks unauthorized digital access without permission or consent.",
    ),
    (
        re.compile(
            rf'\b(?:how\s+(?:to|do\s+i|can\s+i)|help\s+me|show\s+me\s+how\s+to|write\s+(?:a\s+)?(?:script|code|tool)\s+to|steps?\s+to)\s+'
            rf'(?:\w+\s+){{0,3}}{_CYBER_ATTACK_VERBS}\s+'
            rf'(?:an?\s+|the\s+|someone(?:\s+else)?\'?s\s+|another\s+person\'?s\s+|a\s+stranger\'?s\s+|my\s+(?:neighbor|neighbour|coworker)\'?s\s+|a\s+company\'?s\s+)?'
            rf'(?:\w+\s+){{0,3}}(?:{_CYBER_TARGETS}|passwords?|credentials?|login|authentication|2fa|mfa|wpa2?|wep)\b',
            re.IGNORECASE,
        ),
        "critical",
        "Requests actionable exploitation, intrusion, credential cracking, or authentication bypass instructions.",
    ),
    (
        re.compile(
            rf'\b(?:write|create|build|generate|code|develop|give\s+me|deploy|install)\s+'
            rf'(?:a|an|some|undetectable|stealth|hidden)?\s*(?:\w+\s+){{0,2}}{_MALWARE_TERMS}\b',
            re.IGNORECASE,
        ),
        "critical",
        "Requests creation or deployment of malware, spyware, keyloggers, or exploit payloads.",
    ),
    (
        re.compile(
            r'\b(?:steal|harvest|dump|extract|exfiltrate|capture)\s+(?:other\s+people\'?s\s+|users?\'?\s+|saved\s+|admin\s+)?'
            r'(?:passwords?|credentials?|session\s+tokens?|cookies?|credit\s+cards?|api\s+keys?|ssh\s+keys?)\b',
            re.IGNORECASE,
        ),
        "critical",
        "Requests unauthorized theft or harvesting of credentials, tokens, or sensitive authentication secrets.",
    ),
]

# 3. Discrimination & Unfair Treatment
_DISCRIM_EXCLUDE_VERBS = (
    r'(?:reject|exclude|screen\s+out|filter(?:\s+out)?|disqualify|penalize|penalise|'
    r'eliminate|bar|ban|block|refuse(?:\s+to\s+(?:hire|admit|rent|serve|approve|accept))?|'
    r'deny(?:\s+(?:loans?|credit|housing|admission|jobs?|interviews?|service))?|'
    r'don\'?t\s+(?:hire|shortlist|accept|admit|approve|rent\s+to|promote)|'
    r'do\s+not\s+(?:hire|shortlist|accept|admit|approve|rent\s+to|promote)|'
    r'avoid\s+(?:hiring|recruiting|admitting|renting\s+to|promoting)|'
    r'deprioritize|downgrade|score\s+penalty|lower\s+(?:ratings?|scores?))'
)

_DISCRIM_ONLY_VERBS = (
    r'(?:only\s+(?:hire|shortlist|select|accept|admit|approve|promote|rent\s+to|recruit)|'
    r'(?:hire|shortlist|select|accept|admit|approve|promote|recruit)\s+only)'
)

_ALLOCATION_CONTEXT = (
    r'(?:candidates?|applicants?|resumes?|employees?|staff|workers?|tenants?|borrowers?|students?|customers?|patients?|people|users?|team|hiring|recruitment|screening|loans?|credit|housing|admissions?|promotions?)'
)

_DISCRIM_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (
        re.compile(
            rf'\b{_DISCRIM_EXCLUDE_VERBS}\s+(?:any\s+|all\s+)?(?:{_ALLOCATION_CONTEXT}\s+)?'
            rf'(?:(?:who|that)\s+(?:are|use|have|belong\s+to|practice|follow)\s+(?:not\s+)?|from\s+|based\s+on\s+|by\s+|with\s+|if\s+they\s+(?:are|have|use)\s+(?:not\s+)?)?'
            rf'(?:\w+\s+){{0,4}}{_PROTECTED_GROUPS}\b',
            re.IGNORECASE,
        ),
        "high",
        "Directs discriminatory exclusion, rejection, or penalization based on protected personal characteristics.",
    ),
    (
        re.compile(
            rf'\b{_DISCRIM_ONLY_VERBS}\s+(?:\w+\s+){{0,3}}{_PROTECTED_GROUPS}\b',
            re.IGNORECASE,
        ),
        "high",
        "Mandates exclusive preference based on protected characteristics in hiring, housing, lending, or admissions.",
    ),
    (
        re.compile(
            rf'\b(?:filter|rank|sort|score|screen|evaluate)\s+(?:{_ALLOCATION_CONTEXT}\s+)?'
            rf'(?:by|based\s+on|using)\s+(?:their\s+)?{_PROTECTED_GROUPS}\b',
            re.IGNORECASE,
        ),
        "high",
        "Requests automated decision-making or scoring conditioned on protected demographic attributes.",
    ),
    (
        re.compile(
            rf'\b(?:why\s+(?:are|is)|explain\s+why|prove\s+(?:that)?|give\s+reasons?\s+why|write\s+(?:an?\s+)?(?:essay|argument)\s+(?:that|claiming))\s+'
            rf'(?:\w+\s+){{0,2}}{_PROTECTED_GROUPS}\s+(?:\w+\s+){{0,3}}'
            rf'(?:inferior|worse|less\s+(?:capable|intelligent|qualified|competent|trustworthy)|unfit|slower|lazy|bad\s+at|naturally\s+less)\b',
            re.IGNORECASE,
        ),
        "high",
        "Asserts or solicits prejudicial generalizations claiming inferiority of a protected demographic group.",
    ),
]

# 4. Fraud, Impersonation & Deceptive Communications
_FRAUD_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (
        re.compile(
            r'\b(?:write|create|generate|draft|craft|design)\s+(?:a|an|me\s+a)?\s*(?:\w+\s+){0,2}'
            r'(?:phishing|spear[- ]?phishing|scam|fraudulent|deceptive|spoofed|fake)\s+(?:\w+\s+){0,2}'
            r'(?:email|message|sms|text|letter|template|invoice|website|login\s+page|announcement|notice|receipt|degree|certificate|transcript|medical\s+note|id\s+card)\b',
            re.IGNORECASE,
        ),
        "high",
        "Requests creation of phishing, scam, forged, or deceptive communication material.",
    ),
    (
        re.compile(
            r'\b(?:impersonate|pose\s+as|pretend\s+to\s+be)\s+(?:the\s+|a\s+|an\s+)?'
            r'(?:college|university|administration|bank|irs|tax\s+(?:officer|authority)|police|ceo|hr|support\s+team|professor|dean|official)\s+'
            r'.*?\b(?:trick|convince|deceive|fool|get\s+(?:them|students|users|victims)\s+to|transfer|send\s+money|share\s+(?:passwords?|otp|credentials?|bank)|click)\b',
            re.IGNORECASE,
        ),
        "high",
        "Requests unauthorized impersonation to deceive victims into sharing credentials or transferring funds.",
    ),
    (
        re.compile(
            r'\b(?:forge|falsify|counterfeit|fabricate)\s+(?:a|an|some)?\s*(?:\w+\s+){0,2}'
            r'(?:invoice|degree|diploma|certificate|transcript|pay\s*slip|salary\s+slip|bank\s+statement|medical\s+certificate|prescription|signature|passport|id|aadhaar|pan\s+card)\b',
            re.IGNORECASE,
        ),
        "high",
        "Requests forgery or fabrication of official, financial, medical, or academic documents.",
    ),
]

# 5. Covert Surveillance & Non-Consensual Privacy Violations (supplements PII detection)
_SURVEILLANCE_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (
        re.compile(
            r'\b(?:track|monitor|spy\s+on|record|stalk|locate|read\s+(?:messages|texts|chats)\s+of)\s+'
            r'(?:my\s+(?:partner|spouse|ex|employee|coworker|classmate|neighbor)(?:\'?s)?|someone(?:\'?s)?|a\s+person(?:\'?s)?)\s+'
            r'.*?\b(?:without\s+(?:their\s+)?(?:consent|knowledge|permission|knowing)|secretly|covertly|hidden|silently)\b',
            re.IGNORECASE,
        ),
        "high",
        "Requests covert surveillance, stalking, or non-consensual tracking of an individual.",
    ),
    (
        re.compile(
            r'\b(?:dox|doxx|find\s+(?:the\s+)?(?:home\s+address|private\s+phone|personal\s+details|ssn|aadhaar)\s+of|'
            r'scrape\s+(?:private|personal)\s+(?:emails?|phone\s+numbers?|profiles?|data)\b.*?\bwithout\s+consent)\b',
            re.IGNORECASE,
        ),
        "high",
        "Requests doxxing or unauthorized harvesting of private personal information.",
    ),
]

# 6. Harassment, Threats & Targeted Abuse
_HARASSMENT_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (
        re.compile(
            r'\b(?:write|draft|send|create|generate)\s+(?:a|an|some)?\s*(?:\w+\s+){0,2}'
            r'(?:threatening|abusive|harassing|intimidating|blackmail|extortion|hate\s+speech|cyberbullying|defamatory)\s+'
            r'(?:messages?|emails?|letters?|posts?|comments?|notes?|texts?|scripts?|campaigns?)\b',
            re.IGNORECASE,
        ),
        "high",
        "Requests generation of threats, blackmail, hate speech, or targeted harassment.",
    ),
    (
        re.compile(
            r'\b(?:how\s+(?:to|can\s+i)|help\s+me)\s+(?:harass|bully|intimidate|blackmail|extort|ruin\s+the\s+reputation\s+of|dox|terrorize|humiliate)\s+'
            r'(?:someone|my\s+\w+|a\s+\w+|them|him|her)\b',
            re.IGNORECASE,
        ),
        "high",
        "Requests actionable methods to harass, blackmail, intimidate, or target an individual.",
    ),
]

# 7. Deliberate Misinformation & Manipulation
_MISINFO_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (
        re.compile(
            r'\b(?:fabricate|invent|spread|create|generate|write)\s+(?:a|an|some)?\s*(?:\w+\s+){0,2}'
            r'(?:fake\s+news|false\s+rumors?|hoax|disinformation|propaganda|fabricated\s+study|fake\s+emergency|fake\s+medical\s+advice|deceptive\s+announcement)\b',
            re.IGNORECASE,
        ),
        "high",
        "Requests fabrication or dissemination of deliberate misinformation, hoaxes, or deceptive rumors.",
    ),
    (
        re.compile(
            r'\b(?:create|write|generate|run)\s+(?:a|an|hundreds\s+of)?\s*(?:fake|astroturf|bot)\s+'
            r'(?:reviews?|testimonials?|accounts?\s+to\s+manipulate|election\s+disinformation|voter\s+suppression)\b',
            re.IGNORECASE,
        ),
        "high",
        "Requests coordinated manipulation, fake reviews, or deceptive disinformation campaigns.",
    ),
]

# 8. Other Unethical / Unsafe Requests
_OTHER_UNETHICAL_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (
        re.compile(
            r'\b(?:how\s+(?:to|can\s+i)|help\s+me)\s+(?:cheat\s+on\s+(?:a|an|my)?\s*(?:proctored\s+)?exam|'
            r'bypass\s+(?:online\s+proctoring|plagiarism\s+detection|exam\s+security)|'
            r'bribe\s+(?:an?\s+)?(?:official|professor|examiner|officer)|'
            r'sabotage\s+(?:my\s+coworker|a\s+competitor|company\s+equipment)|'
            r'evade\s+(?:taxes\s+illegally|law\s+enforcement|police\s+detection)|'
            r'launder\s+money)\b',
            re.IGNORECASE,
        ),
        "high",
        "Requests assistance with unethical, fraudulent, or illegal conduct (e.g., exam cheating evasion, bribery, sabotage, or money laundering).",
    ),
]

# Ambiguous Dual-Use Triggers (sensitive topic without clear authorization or defensive/educational framing)
_AMBIGUOUS_DUAL_USE_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (
        re.compile(
            r'\b(?:how\s+(?:to|do\s+i|can\s+i)\s+(?:get\s+into|access|(?:reset|find)\s+(?:the\s+)?password\s+(?:for|on))\s+(?:a|the)\s+(?:router|wi-?fi|admin\s+panel|locked\s+phone|server|database)|'
            r'show\s+me\s+(?:a\s+working|an?\s+actual|how\s+to\s+run\s+(?:a|an))\s+(?:sql\s+injection|xss|buffer\s+overflow|port\s+scan|exploit)\s+(?:against|on)\b)',
            re.IGNORECASE,
        ),
        "unauthorized_cybersecurity",
        "Ambiguous dual-use security request without explicit ownership or authorization context.",
    ),
]


class LocalRulesEngine:
    def evaluate(self, prompt: str) -> Dict[str, Any]:
        stripped = (prompt or "").strip()
        if not stripped:
            return {
                "intent": "benign_general",
                "authorization_indicator": "not_applicable",
                "is_educational": False,
                "is_defensive": False,
                "is_quoted_analysis": False,
                "has_pii": False,
                "pii_result": {"detected_count": 0, "sanitized_text": "", "findings": [], "entity_map": {}},
                "instruction_conflict": False,
                "findings": [],
                "ambiguous_signals": [],
            }

        # 1. Determine contextual intent & authorization cues
        is_quoted_analysis = bool(_QUOTED_ANALYSIS_RE.search(stripped))
        is_defensive = bool(_DEFENSIVE_FRAME_RE.search(stripped))
        is_educational = bool(_EDUCATIONAL_FRAME_RE.search(stripped))
        is_hypothetical = bool(_HYPOTHETICAL_FRAME_RE.search(stripped))
        has_authorized_cue = bool(_AUTHORIZED_SELF_RE.search(stripped))
        has_unauthorized_cue = bool(_UNAUTHORIZED_CUES_RE.search(stripped))
        has_actionable_cue = bool(_ACTIONABLE_REQUEST_RE.search(stripped))

        if has_unauthorized_cue:
            auth_indicator = "unauthorized_third_party"
        elif has_authorized_cue:
            auth_indicator = "authorized_self_owned"
        else:
            auth_indicator = "not_applicable"

        # Determine text to inspect for direct harmful imperatives:
        # If the user quotes a harmful statement strictly to analyze/critique it,
        # avoid matching patterns inside the quoted segment.
        inspection_text = stripped
        if is_quoted_analysis and not has_unauthorized_cue:
            inspection_text = re.sub(r'["\'“][^"\'”]{3,}["\'”]', ' [QUOTED_STATEMENT] ', stripped)

        findings: List[Dict[str, Any]] = []
        ambiguous_signals: List[Dict[str, Any]] = []

        # 2. Privacy Check (Context-aware IP + PII)
        pii_res = privacy_service.redact(stripped, mode="placeholder")
        has_pii = pii_res["detected_count"] > 0
        if has_pii:
            for f in pii_res["findings"]:
                # Personal contact PII is medium risk (CAUTION), secrets/national IDs are high/critical PII
                # Note: PII alone should trigger CAUTION (unless covert surveillance/doxxing is also present)
                pii_sev = "medium" if f["severity"] in ("medium", "high") else "medium"
                if f["entity_type"] in ("api_key", "credit_card", "aadhaar_id", "ssn"):
                    pii_sev = "medium"  # High-sensitivity PII still triggers CAUTION with high caution score
                findings.append({
                    "category": "privacy_surveillance",
                    "subcategory": "pii_exposure",
                    "severity": pii_sev,
                    "raw_pii_severity": f["severity"],
                    "description": f"Contains unmasked {f['label']}",
                    "matched_text": f["matched_text"],
                    "start": f["start"],
                    "end": f["end"],
                    "source": "local",
                })

        # 3. Instruction Integrity Check
        integrity_res = integrity_service.inspect(stripped)
        instruction_conflict = integrity_res["has_conflict"]
        if instruction_conflict:
            for c in integrity_res["conflicts"]:
                findings.append({
                    "category": "instruction_integrity",
                    "severity": c["severity"],
                    "description": c["explanation"],
                    "matched_text": c["matched_text"],
                    "start": c["start"],
                    "end": c["end"],
                    "source": "local",
                })

        # 4. Physical Harm & Violence (suppress ONLY if clearly educational/defensive/quoted AND no actionable make/use request)
        self._apply_patterns(
            text=inspection_text,
            patterns=_PHYSICAL_HARM_PATTERNS,
            category="physical_harm_violence",
            findings=findings,
            suppress=(is_defensive and not has_actionable_cue) or (is_quoted_analysis and not has_actionable_cue),
        )

        # 5. Unauthorized Cybersecurity
        # Suppress defensive/self-owned queries unless explicit unauthorized cues or malware creation are present
        suppress_cyber = (is_defensive or (is_educational and not has_actionable_cue)) and not has_unauthorized_cue
        self._apply_patterns(
            text=inspection_text,
            patterns=_CYBER_PATTERNS,
            category="unauthorized_cybersecurity",
            findings=findings,
            suppress=suppress_cyber,
        )

        # 6. Discrimination & Unfair Treatment
        # Note: Do NOT suppress essentialist inferiority claims like "Explain why women are inferior..."
        suppress_discrim = (is_educational or is_defensive) and not re.search(
            r'\b(?:inferior|worse|less\s+capable|unfit|slower)\b',
            inspection_text,
            re.IGNORECASE,
        )
        self._apply_patterns(
            text=inspection_text,
            patterns=_DISCRIM_PATTERNS,
            category="discrimination_bias",
            findings=findings,
            suppress=suppress_discrim and not re.search(
                rf'\b(?:{_DISCRIM_EXCLUDE_VERBS}|{_DISCRIM_ONLY_VERBS})\b',
                inspection_text,
                re.IGNORECASE,
            ),
        )

        # 7. Fraud & Deceptive Communications
        self._apply_patterns(
            text=inspection_text,
            patterns=_FRAUD_PATTERNS,
            category="fraud_deception",
            findings=findings,
            suppress=is_defensive and not re.search(r'\b(?:write|create|generate|draft)\s+(?:a|an)?\s*(?:phishing|scam|fraudulent|fake)\b', inspection_text, re.IGNORECASE),
        )

        # 8. Covert Surveillance & Doxxing
        self._apply_patterns(
            text=inspection_text,
            patterns=_SURVEILLANCE_PATTERNS,
            category="privacy_surveillance",
            findings=findings,
            suppress=(is_educational or is_defensive) and not has_unauthorized_cue,
        )

        # 9. Harassment & Targeted Abuse
        self._apply_patterns(
            text=inspection_text,
            patterns=_HARASSMENT_PATTERNS,
            category="harassment_abuse",
            findings=findings,
            suppress=is_educational and not has_actionable_cue,
        )

        # 10. Misinformation & Manipulation
        self._apply_patterns(
            text=inspection_text,
            patterns=_MISINFO_PATTERNS,
            category="misinformation_manipulation",
            findings=findings,
            suppress=is_defensive and not re.search(r'\b(?:fabricate|invent|spread|generate)\s+(?:a|an)?\s*(?:fake|false|hoax|disinformation)\b', inspection_text, re.IGNORECASE),
        )

        # 11. Other Unethical Requests
        self._apply_patterns(
            text=inspection_text,
            patterns=_OTHER_UNETHICAL_PATTERNS,
            category="other_unethical_risk",
            findings=findings,
            suppress=is_educational and not has_actionable_cue,
        )

        # 12. Ambiguous Dual-Use Checks (when not already flagged as unauthorized & not explicitly self-owned/defensive)
        has_severe_finding = any(f["severity"] in ("high", "critical") for f in findings)
        if not has_severe_finding and not has_authorized_cue and not is_defensive:
            for pat, cat, desc in _AMBIGUOUS_DUAL_USE_PATTERNS:
                m = pat.search(inspection_text)
                if m:
                    auth_indicator = "unspecified"
                    ambiguous_signals.append({
                        "category": cat,
                        "severity": "medium",
                        "description": desc,
                        "matched_text": m.group(0),
                        "start": m.start(),
                        "end": m.end(),
                        "source": "local",
                    })

        # 13. Determine Final Local Intent Classification
        has_harm_finding = any(
            f["category"] != "privacy_surveillance" or f.get("subcategory") != "pii_exposure"
            for f in findings
            if f["category"] != "instruction_integrity"
        )
        if has_harm_finding:
            intent = "harmful_instruction"
        elif ambiguous_signals:
            intent = "ambiguous_context"
        elif is_quoted_analysis:
            intent = "ethical_analysis_quote"
        elif is_defensive:
            intent = "defensive_safety"
        elif is_hypothetical:
            intent = "hypothetical_discussion"
        elif is_educational:
            intent = "educational_explanation"
        else:
            intent = "benign_general"

        if auth_indicator == "not_applicable" and any(
            f["category"] == "unauthorized_cybersecurity" for f in findings
        ):
            auth_indicator = "unauthorized_third_party"

        return {
            "intent": intent,
            "authorization_indicator": auth_indicator,
            "is_educational": intent in ("educational_explanation", "defensive_safety", "ethical_analysis_quote", "hypothetical_discussion"),
            "is_defensive": is_defensive,
            "is_quoted_analysis": is_quoted_analysis,
            "has_pii": has_pii,
            "pii_result": pii_res,
            "instruction_conflict": instruction_conflict,
            "findings": findings + ambiguous_signals,
            "ambiguous_signals": ambiguous_signals,
        }

    def _apply_patterns(
        self,
        text: str,
        patterns: List[Tuple[re.Pattern, str, str]],
        category: str,
        findings: List[Dict[str, Any]],
        suppress: bool = False,
    ) -> None:
        if suppress:
            return
        seen_matches = set()
        for pat, severity, description in patterns:
            for m in pat.finditer(text):
                span_key = (category, m.start(), m.end())
                if span_key in seen_matches:
                    continue
                seen_matches.add(span_key)
                findings.append({
                    "category": category,
                    "severity": severity,
                    "description": description,
                    "matched_text": m.group(0),
                    "start": m.start(),
                    "end": m.end(),
                    "source": "local",
                })


local_rules_engine = LocalRulesEngine()
