import pytest
from app.services.privacy import privacy_service

def test_detect_email_and_phone():
    text = "Please reach out to student.demo@msrit.edu or call +91-98765-43210 for project updates."
    res = privacy_service.detect_pii(text)
    assert res["has_pii"] is True
    assert res["count"] >= 2
    types = [f["entity_type"] for f in res["findings"]]
    assert "email" in types
    assert "phone" in types

def test_redact_placeholder_mode():
    text = "Send credentials to admin@example.com."
    redacted = privacy_service.redact(text, mode="placeholder")
    assert "[EMAIL_1]" in redacted["sanitized_text"]
    assert "admin@example.com" not in redacted["sanitized_text"]
    assert redacted["detected_count"] == 1

def test_clean_text_no_pii():
    text = "Explain the difference between supervised and unsupervised learning algorithms."
    res = privacy_service.detect_pii(text)
    assert res["has_pii"] is False
    assert res["count"] == 0
