import ipaddress
import re
from typing import Dict, Any, List

WELL_KNOWN_PUBLIC_INFRA_IPS = {
    "8.8.8.8",
    "8.8.4.4",
    "1.1.1.1",
    "1.0.0.1",
    "9.9.9.9",
    "208.67.222.222",
    "208.67.220.220",
}

DOC_TEST_NETWORKS = [
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
]

_EDU_OR_DEFENSIVE_NET_RE = re.compile(
    r'\b(?:explain|what\s+is|how\s+does|how\s+can\s+i\s+(?:secure|protect|harden|configure)|'
    r'secure\s+my|protect\s+my|harden\s+my|subnet|subnetting|cidr|routing|dns|nat|dhcp|'
    r'firewall\s+rules?|rfc\s*1918|networking\s+example|tutorial|textbook|diagram)\b',
    re.IGNORECASE,
)

_OPERATIONAL_SECRET_OR_CONNECT_RE = re.compile(
    r'\b(?:connect\s+to|log\s*in\s+to|ssh\s+into|database\s+host|administrative\s+credentials|'
    r'admin\s+credentials|root\s+password|my\s+server|production\s+host|my\s+home\s+ip|'
    r'my\s+ip\s+address|user\s+ip|client\s+ip|track\s+(?:this|the)\s+ip|trace\s+ip)\b',
    re.IGNORECASE,
)

_UNAUTHORIZED_TARGET_NET_RE = re.compile(
    r'\b(?:without\s+permission|someone\s+else\'?s|hack|break\s+into|compromise|exploit|ddos|'
    r'scan\s+ports?\s+on\s+(?:their|someone)|attack)\b',
    re.IGNORECASE,
)

PII_PATTERNS = {
    "email": {
        "pattern": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'),
        "severity": "high",
        "label": "Email Address"
    },
    "phone": {
        "pattern": re.compile(r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{4,5}\b'),
        "severity": "high",
        "label": "Phone Number"
    },
    "credit_card": {
        "pattern": re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'),
        "severity": "critical",
        "label": "Payment Card"
    },
    "api_key": {
        "pattern": re.compile(
            r'\b(?:sk-[a-zA-Z0-9_-]{20,60}|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|'
            r'AIza[0-9A-Za-z-_]{35}|AQ\.[0-9A-Za-z_-]{30,80}|'
            r'(?:api[_-]?key|secret[_-]?token|access[_-]?token)[\s:=]+["\']?([a-zA-Z0-9._-]{16,80})["\']?)\b',
            re.IGNORECASE
        ),
        "severity": "critical",
        "label": "API Key / Secret Token"
    },
    "aadhaar_id": {
        "pattern": re.compile(r'\b[2-9]{1}[0-9]{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b'),
        "severity": "critical",
        "label": "National ID (Aadhaar/Resident)"
    },
    "ssn": {
        "pattern": re.compile(r'\b(?!000|666|9\d{2})\d{3}[-\s](?!00)\d{2}[-\s](?!0000)\d{4}\b'),
        "severity": "critical",
        "label": "Social Security Number (SSN)"
    },
    "ip_address": {
        "pattern": re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'),
        "severity": "medium",
        "label": "IP Address"
    }
}


def classify_ip_address(ip_str: str) -> str:
    """Classify an IPv4 address into documentation/loopback, well-known DNS, private LAN, or public."""
    if ip_str in WELL_KNOWN_PUBLIC_INFRA_IPS:
        return "well_known_public_dns"
    try:
        ip_obj = ipaddress.ip_address(ip_str)
    except ValueError:
        return "invalid"
    if ip_obj.is_loopback or ip_obj.is_unspecified or ip_obj.is_multicast:
        return "documentation_or_loopback"
    if any(ip_obj in net for net in DOC_TEST_NETWORKS):
        return "documentation_or_loopback"
    if ip_obj.is_private or ip_obj.is_link_local:
        return "private_lan"
    if ip_obj.is_reserved:
        return "documentation_or_loopback"
    return "public"


def luhn_valid(num_str: str) -> bool:
    digits = [int(c) for c in re.sub(r'\D', '', num_str)]
    if len(digits) < 13:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = d * 2
            checksum += (doubled - 9) if doubled > 9 else doubled
        else:
            checksum += d
    return (checksum % 10) == 0


class PrivacyShieldService:
    def detect_pii(self, text: str) -> Dict[str, Any]:
        if not text:
            return {"has_pii": False, "findings": [], "count": 0, "ip_observations": []}

        findings: List[Dict[str, Any]] = []
        ip_observations: List[Dict[str, Any]] = []
        seen_spans = set()

        is_edu_or_defensive_net = bool(_EDU_OR_DEFENSIVE_NET_RE.search(text))
        is_operational_connect = bool(_OPERATIONAL_SECRET_OR_CONNECT_RE.search(text))
        is_unauthorized_net = bool(_UNAUTHORIZED_TARGET_NET_RE.search(text))

        priority_order = ["email", "api_key", "credit_card", "ssn", "aadhaar_id", "ip_address", "phone"]

        for entity_type in priority_order:
            cfg = PII_PATTERNS[entity_type]
            pattern = cfg["pattern"]
            for m in pattern.finditer(text):
                start, end = m.start(), m.end()
                val = m.group(0).strip()

                if any(start >= s and end <= e for (s, e) in seen_spans):
                    continue

                if entity_type == "credit_card" and not luhn_valid(val):
                    continue

                if entity_type == "phone":
                    digits = re.sub(r'\D', '', val)
                    if len(digits) < 10 or len(digits) > 15:
                        continue
                    if "." in val and re.match(r'^\d+\.\d+\.\d+', val):
                        continue

                if entity_type == "ip_address":
                    ip_scope = classify_ip_address(val)
                    ip_observations.append({
                        "ip": val,
                        "scope": ip_scope,
                        "start": start,
                        "end": end,
                    })
                    seen_spans.add((start, end))

                    # Never classify loopback, RFC 5737 test ranges, or public DNS resolvers (e.g., 8.8.8.8) as PII
                    if ip_scope in ("documentation_or_loopback", "well_known_public_dns", "invalid"):
                        continue

                    # Private RFC 1918 LAN IPs (e.g., 192.168.1.1) are NOT personal data in educational or
                    # self-owned defensive router configuration queries; flag only when paired with operational
                    # host/credential exposure.
                    if ip_scope == "private_lan":
                        if is_edu_or_defensive_net and not is_operational_connect:
                            continue
                        if not is_operational_connect:
                            continue
                        findings.append({
                            "entity_type": "ip_address",
                            "label": "Internal Infrastructure IP (Operational Context)",
                            "severity": "medium",
                            "matched_text": val,
                            "ip_scope": ip_scope,
                            "start": start,
                            "end": end
                        })
                        continue

                    # Public routable IP: if part of an educational example without personal exposure, skip PII.
                    # If part of an unauthorized attack prompt, cybersecurity analyzer handles the severe risk.
                    if ip_scope == "public":
                        if is_edu_or_defensive_net and not is_operational_connect:
                            continue
                        if is_unauthorized_net and not is_operational_connect:
                            continue
                        findings.append({
                            "entity_type": "ip_address",
                            "label": "Public IP Address",
                            "severity": "medium",
                            "matched_text": val,
                            "ip_scope": ip_scope,
                            "start": start,
                            "end": end
                        })
                        continue

                seen_spans.add((start, end))
                findings.append({
                    "entity_type": entity_type,
                    "label": cfg["label"],
                    "severity": cfg["severity"],
                    "matched_text": val,
                    "start": start,
                    "end": end
                })

        findings.sort(key=lambda x: x["start"])
        return {
            "has_pii": len(findings) > 0,
            "findings": findings,
            "count": len(findings),
            "ip_observations": ip_observations,
        }

    def redact(self, text: str, mode: str = "placeholder") -> Dict[str, Any]:
        detection = self.detect_pii(text)
        if not detection["has_pii"]:
            return {
                "original_text": text,
                "sanitized_text": text,
                "detected_count": 0,
                "entity_map": {},
                "findings": [],
                "ip_observations": detection.get("ip_observations", []),
            }

        findings = detection["findings"]
        entity_counters: Dict[str, int] = {}
        entity_map: Dict[str, str] = {}
        sanitized_chars = list(text)

        for item in sorted(findings, key=lambda x: x["start"], reverse=True):
            ent = item["entity_type"]
            start, end = item["start"], item["end"]
            raw_val = text[start:end]

            entity_counters[ent] = entity_counters.get(ent, 0) + 1
            idx = entity_counters[ent]

            if mode == "placeholder":
                replacement = f"[{ent.upper()}_{idx}]"
            elif mode == "mask":
                replacement = f"[REDACTED: {ent.upper()}]"
            else:
                replacement = "[REDACTED]"

            entity_map[replacement] = self._make_preview(raw_val, ent)
            sanitized_chars[start:end] = list(replacement)

        sanitized_text = "".join(sanitized_chars)
        return {
            "original_text": text,
            "sanitized_text": sanitized_text,
            "detected_count": len(findings),
            "entity_map": entity_map,
            "findings": findings,
            "ip_observations": detection.get("ip_observations", []),
        }

    def _make_preview(self, val: str, entity_type: str) -> str:
        if entity_type == "email":
            parts = val.split("@")
            if len(parts) == 2:
                name, dom = parts
                return f"{name[0]}***@{dom}"
        elif entity_type in ("credit_card", "aadhaar_id", "ssn", "phone"):
            clean = re.sub(r'\D', '', val)
            last4 = clean[-4:] if len(clean) >= 4 else "XXXX"
            return f"***-***-{last4}"
        return val[:2] + "****" if len(val) > 2 else "****"


privacy_service = PrivacyShieldService()
