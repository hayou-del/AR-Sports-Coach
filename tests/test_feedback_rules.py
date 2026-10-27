import pytest

from ai.feedback_rules import FeedbackRuleEngine


def test_no_pose_returns_warning():
    result = FeedbackRuleEngine().evaluate({
        "detected": False
    })

    assert result["status"] == "no_pose"
    assert result["severity"] == "warning"
    assert "No pose detected" in result["message"]


def test_invalid_measurement_does_not_assess_posture():
    result = FeedbackRuleEngine().evaluate({
        "detected": True,
        "valid_measurement": False,
        "movement_state": "bottom",
        "angles": {"mean_knee": 90.0},
    })

    assert result["status"] == "measurement_unavailable"
    assert "cannot assess" in result["message"]


def test_descending_feedback():
    result = FeedbackRuleEngine().evaluate({
        "detected": True,
        "valid_measurement": True,
        "movement_state": "descending",
        "repetitions": 2,
    })

    assert result["status"] == "descending"
    assert "controlled" in result["message"].lower()
    assert any("2" in tip for tip in result["tips"])


def test_bottom_feedback_uses_knee_angle():
    result = FeedbackRuleEngine().evaluate({
        "movement_state": "bottom",
        "angles": {"mean_knee": 125.0},
    })

    assert result["status"] == "bottom"
    assert any(
        "depth" in tip.lower()
        for tip in result["tips"]
    )


def test_unknown_state_returns_general_feedback():
    result = FeedbackRuleEngine().evaluate({
        "movement_state": "unknown"
    })

    assert result["status"] == "general"
    assert result["message"]


def test_invalid_metrics_type_is_rejected():
    with pytest.raises(TypeError):
        FeedbackRuleEngine().evaluate(None)


def test_invalid_thresholds_are_rejected():
    with pytest.raises(ValueError):
        FeedbackRuleEngine(
            squat_bottom_max_knee_angle=160,
            squat_standing_min_knee_angle=150,
        )

