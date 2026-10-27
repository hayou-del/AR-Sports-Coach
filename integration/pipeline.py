
"""Coordinate exercise analysis and AI coaching feedback."""

import math

from ai.coaching_engine import CoachingEngine
from analysis.exercise_analyzer import SquatAnalyzer, calculate_angle


_coaching_engine = CoachingEngine()


def _normalize_metrics(metrics: dict) -> dict:
    """Support both legacy and current exercise metric names."""
    normalized = metrics.copy()

    if "repetitions" not in normalized and "reps" in normalized:
        normalized["repetitions"] = normalized["reps"]

    if "movement_state" not in normalized and "state" in normalized:
        normalized["movement_state"] = normalized["state"]

    if "mean_knee" not in normalized and "angles" not in normalized:
        if "knee_angle" in normalized:
            normalized["mean_knee"] = normalized["knee_angle"]

    angle = normalized.get("mean_knee")
    if angle is None and isinstance(normalized.get("angles"), dict):
        angle = normalized["angles"].get("mean_knee")

    if angle is not None:
        valid_angle = (
            isinstance(angle, (int, float))
            and not isinstance(angle, bool)
            and math.isfinite(angle)
            and 0 < angle < 180
        )
        if not valid_angle:
            normalized["valid_measurement"] = False

    return normalized


def process_metrics(metrics: dict) -> dict:
    """Return original metrics and feedback generated from normalized metrics."""
    if not isinstance(metrics, dict):
        metrics = {}

    safe_metrics = metrics.copy()
    normalized = _normalize_metrics(safe_metrics)
    feedback = _coaching_engine.generate_feedback(normalized)

    return {
        "metrics": safe_metrics,
        "feedback": feedback,
    }


class CoachingPipeline:
    """Coordinate squat analysis and AI coaching."""

    def __init__(self):
        self.analyzer = SquatAnalyzer()

    def reset(self):
        """Reset the exercise analyzer."""
        self.analyzer.reset()

    def process_landmarks(self, hip, knee, ankle) -> dict:
        """Analyze landmarks and return metrics with coaching feedback."""
        reps, state = self.analyzer.update_from_landmarks(
            hip,
            knee,
            ankle,
        )

        knee_angle = None

        if hip is not None and knee is not None and ankle is not None:
            try:
                knee_angle = calculate_angle(hip, knee, ankle)
            except (TypeError, ValueError):
                knee_angle = None

        metrics = {
            "knee_angle": knee_angle,
            "reps": reps,
            "state": state,
        }

        if knee_angle is None:
            metrics["valid_measurement"] = False

        return process_metrics(metrics)
