from ai.coaching_engine import CoachingEngine
from ai.feedback_rules import FeedbackRuleEngine


def test_engine_returns_expected_output():
    engine = CoachingEngine()

    result = engine.generate_feedback({
        "detected": True,
        "valid_measurement": True,
        "movement_state": "standing",
        "repetitions": 3,
        "angles": {"mean_knee": 170.0},
    })

    assert set(result) == {
        "message",
        "severity",
        "tips",
        "status",
        "repetitions",
    }

    assert isinstance(result["message"], str)
    assert isinstance(result["tips"], list)
    assert result["repetitions"] == 3


def test_generate_alias():
    engine = CoachingEngine()
    metrics = {"detected": False}

    assert engine.generate(metrics) == (
        engine.generate_feedback(metrics)
    )


def test_missing_metrics_returns_general_feedback():
    result = CoachingEngine().generate_feedback({})

    assert result["message"]
    assert result["tips"]
    assert result["status"] == "general"


def test_custom_rule_engine():
    rules = FeedbackRuleEngine()
    engine = CoachingEngine(rules=rules)

    result = engine.generate_feedback({
        "movement_state": "ascending"
    })

    assert result["status"] == "ascending"


