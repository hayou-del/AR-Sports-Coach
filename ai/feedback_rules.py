"""Rules for generating exercise coaching feedback."""

from typing import Any, Dict, List, Optional


def _as_number(value: Any) -> Optional[float]:
    """Return a finite number or None for invalid input."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None

    number = float(value)

    if number != number or number in (
        float("inf"),
        float("-inf"),
    ):
        return None

    return number


class FeedbackRuleEngine:
    """Generate simple coaching feedback from exercise metrics."""

    def __init__(
        self,
        squat_bottom_max_knee_angle: float = 110.0,
        squat_standing_min_knee_angle: float = 155.0,
    ):
        if not (
            0 < squat_bottom_max_knee_angle < 180
        ):
            raise ValueError(
                "Bottom knee angle must be between 0 and 180."
            )

        if not (
            0 < squat_standing_min_knee_angle < 180
        ):
            raise ValueError(
                "Standing knee angle must be between 0 and 180."
            )

        if (
            squat_bottom_max_knee_angle
            >= squat_standing_min_knee_angle
        ):
            raise ValueError(
                "Bottom threshold must be lower than "
                "standing threshold."
            )

        self.squat_bottom_max_knee_angle = (
            float(squat_bottom_max_knee_angle)
        )
        self.squat_standing_min_knee_angle = (
            float(squat_standing_min_knee_angle)
        )

    def evaluate(
        self,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Return a structured coaching feedback dictionary."""
        if not isinstance(metrics, dict):
            raise TypeError("metrics must be a dictionary.")

        repetitions = _as_number(metrics.get("repetitions"))

        if repetitions is not None and repetitions >= 0:
            repetitions = int(repetitions)
        else:
            repetitions = None

        if metrics.get("detected") is False:
            return self._result(
                message=(
                    "No pose detected. Move into view "
                    "of the camera."
                ),
                severity="warning",
                tips=[
                    "Make sure your body is visible "
                    "and lighting is adequate."
                ],
                status="no_pose",
                repetitions=repetitions,
            )

        if metrics.get("valid_measurement") is False:
            return self._result(
                message=(
                    "I cannot assess the movement "
                    "reliably right now."
                ),
                severity="warning",
                tips=[
                    "Adjust your position so the relevant "
                    "joints are visible."
                ],
                status="measurement_unavailable",
                repetitions=repetitions,
            )

        movement_state = metrics.get(
            "movement_state", "unknown"
        )

        if not isinstance(movement_state, str):
            movement_state = "unknown"

        movement_state = movement_state.lower()

        angles = metrics.get("angles")
        if not isinstance(angles, dict):
            angles = {}

        knee_angle = _as_number(
            angles.get("mean_knee")
        )

        if knee_angle is None:
            knee_angle = _as_number(
                metrics.get("mean_knee")
            )

        status = "general"
        severity = "info"
        tips: List[str] = []

        if movement_state == "descending":
            status = "descending"
            message = "Lower yourself in a controlled way."
            tips.append(
                "Keep your movement smooth and balanced."
            )

        elif movement_state == "ascending":
            status = "ascending"
            message = "Drive upward with control."
            tips.append(
                "Keep your feet planted and your torso stable."
            )

        elif movement_state == "bottom":
            status = "bottom"
            message = "You are at the bottom of the movement."

            if knee_angle is not None:
                if (
                    knee_angle
                    > self.squat_bottom_max_knee_angle
                ):
                    tips.append(
                        "If comfortable, work toward a little "
                        "more depth while keeping control."
                    )
                else:
                    tips.append(
                        "Maintain balance and keep your "
                        "knees aligned with your feet."
                    )
            else:
                tips.append(
                    "Maintain balance and use a comfortable "
                    "range of motion."
                )

        elif movement_state == "standing":
            status = "standing"
            message = (
                "You are standing. Prepare for the next "
                "repetition when ready."
            )

            if (
                knee_angle is not None
                and knee_angle
                < self.squat_standing_min_knee_angle
            ):
                tips.append(
                    "Finish standing tall without forcing "
                    "your knees backward."
                )

        elif movement_state == "transition":
            status = "transition"
            message = (
                "Transition smoothly between movement phases."
            )
            tips.append(
                "Avoid rushing between positions."
            )

        else:
            message = (
                "Keep moving at a comfortable, controlled pace."
            )
            tips.append(
                "Use a range of motion that feels safe "
                "and comfortable."
            )

        if repetitions is not None:
            tips.append(
                f"Completed repetitions: {repetitions}."
            )

        return self._result(
            message=message,
            severity=severity,
            tips=tips,
            status=status,
            repetitions=repetitions,
        )

    @staticmethod
    def _result(
        message: str,
        severity: str,
        tips: List[str],
        status: str,
        repetitions: Optional[int],
    ) -> Dict[str, Any]:
        return {
            "message": message,
            "severity": severity,
            "tips": tips,
            "status": status,
            "repetitions": repetitions,
        }
