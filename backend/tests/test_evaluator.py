import pytest
from app.services.evaluator import evaluator_service


def test_evaluation_runner_100_plus_samples():
    results = evaluator_service.run_evaluation(use_semantic=False)
    assert results["total_samples"] >= 100
    assert results["accuracy"] >= 85.0
    assert results["precision"] >= 90.0
    assert results["recall"] >= 85.0
    assert results["f1_score"] >= 88.0
    cm = results["confusion_matrix"]
    assert "true_positives" in cm
    assert "false_positives" in cm
    assert "true_negatives" in cm
    assert "false_negatives" in cm
    assert cm["true_positives"] + cm["false_positives"] + cm["true_negatives"] + cm["false_negatives"] == results["total_samples"]
