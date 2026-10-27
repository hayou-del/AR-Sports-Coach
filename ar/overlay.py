"""Draw pose landmarks and coaching information over a video frame.

Landmark format:
    {
        "left_shoulder": (x, y),
        "left_elbow": (x, y),
        ...
    }

Coordinates are pixel positions: (x, y).
Missing landmarks may be omitted or set to None.

Analysis results may contain:
    knee_angle, reps, state, feedback

Feedback may be a dictionary containing message and status.
"""

from collections.abc import Mapping
from numbers import Real

import cv2
import numpy as np


# Skeleton connections use the names agreed in this module's interface.
SKELETON_CONNECTIONS = (
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
)

# OpenCV uses BGR, not RGB.
COLORS = {
    "good": (70, 200, 70),
    "warning": (0, 190, 255),
    "waiting": (180, 180, 180),
    "error": (60, 60, 230),
}


def _valid_point(point, width, height):
    """Return an integer pixel point if it is valid; otherwise None."""
    if not isinstance(point, (tuple, list, np.ndarray)) or len(point) != 2:
        return None

    x, y = point
    if (
        isinstance(x, bool)
        or isinstance(y, bool)
        or not isinstance(x, Real)
        or not isinstance(y, Real)
        or not np.isfinite(x)
        or not np.isfinite(y)
    ):
        return None

    x, y = int(round(x)), int(round(y))

    if not (0 <= x < width and 0 <= y < height):
        return None

    return x, y


def draw_overlay(frame, landmarks=None, results=None):
    """Return a copy of frame annotated with pose and coaching information.

    Args:
        frame: A non-empty OpenCV image (NumPy array).
        landmarks: Mapping from landmark names to pixel coordinates.
        results: Mapping containing knee_angle, reps, state and/or feedback.

    Returns:
        A new annotated image. The input frame is not modified.

    Raises:
        ValueError: If frame is empty or is not a color image.
        TypeError: If frame is not a NumPy array.
    """
    if not isinstance(frame, np.ndarray):
        raise TypeError("frame must be a NumPy array")

    if frame.size == 0 or frame.ndim != 3 or frame.shape[2] != 3:
        raise ValueError("frame must be a non-empty BGR color image")

    annotated = frame.copy()
    height, width = annotated.shape[:2]

    if landmarks is None:
        landmarks = {}
    elif not isinstance(landmarks, Mapping):
        landmarks = {}

    if results is None:
        results = {}
    elif not isinstance(results, Mapping):
        results = {}

    points = {
        name: _valid_point(point, width, height)
        for name, point in landmarks.items()
        if isinstance(name, str)
    }

    # Draw only connections whose two endpoints are available.
    for start_name, end_name in SKELETON_CONNECTIONS:
        start = points.get(start_name)
        end = points.get(end_name)

        if start is not None and end is not None:
            cv2.line(
                annotated, start, end, COLORS["good"], 3,
                lineType=cv2.LINE_AA,
            )

    # Draw the detected joints.
    for point in points.values():
        if point is not None:
            cv2.circle(annotated, point, 5, (255, 220, 70), -1)
            cv2.circle(annotated, point, 7, (255, 255, 255), 1)

    feedback = results.get("feedback", {})
    if not isinstance(feedback, Mapping):
        feedback = {}

    status = str(feedback.get("status", results.get("status", "waiting")))
    status = status.lower()
    color = COLORS.get(status, COLORS["waiting"])

    message = feedback.get("message", results.get("message", "Waiting for feedback"))
    if not isinstance(message, str):
        message = "Waiting for feedback"

    angle = results.get("knee_angle")
    if isinstance(angle, Real) and not isinstance(angle, bool) and np.isfinite(angle):
        angle_text = f"Knee angle: {angle:.1f} deg"
    else:
        angle_text = "Knee angle: --"

    reps = results.get("reps", 0)
    if (
        isinstance(reps, Real)
        and not isinstance(reps, bool)
        and np.isfinite(reps)
        and reps >= 0
    ):
        reps_text = f"Reps: {int(reps)}"
    else:
        reps_text = "Reps: --"

    state = results.get("state", "unknown")
    if isinstance(state, str) and state.strip():
        state_text = f"State: {state.capitalize()}"
    else:
        state_text = "State: Unknown"
    # Use a filled panel so text remains readable over changing backgrounds.
    panel_height = min(140, height)
    panel_width = min(width, max(320, int(width * 0.55)))
    cv2.rectangle(
        annotated, (0, 0), (panel_width - 1, panel_height - 1),
        (25, 25, 25), -1,
    )

    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = max(0.45, min(0.7, width / 1000))
    thickness = 2 if width >= 640 else 1

    cv2.putText(
        annotated, angle_text, (12, 25), font, scale,
        (255, 255, 255), thickness, cv2.LINE_AA,
    )
    cv2.putText(
        annotated, reps_text, (12, 50), font, scale,
        (255, 255, 255), thickness, cv2.LINE_AA,
    )
    cv2.putText(
        annotated, state_text, (12, 75), font, scale,
        (255, 255, 255), thickness, cv2.LINE_AA,
    )

    cv2.circle(annotated, (17, 103), 6, color, -1)

    max_chars = max(12, int((panel_width - 38) / (11 * scale)))
    display_message = message[:max_chars]
    cv2.putText(
        annotated, display_message, (30, 108), font, scale,
        color, thickness, cv2.LINE_AA,
    )

    return annotated

    
def draw_pipeline_overlay(frame, landmarks, pipeline_result):
    """Draw an integration pipeline result over a video frame.

    Args:
        frame: OpenCV BGR image.
        landmarks: Named landmark coordinates in pixel positions.
        pipeline_result: Dictionary returned by process_metrics().

    Returns:
        A new annotated frame.
    """
    if not isinstance(pipeline_result, Mapping):
        pipeline_result = {}

    metrics = pipeline_result.get("metrics", {})
    feedback = pipeline_result.get("feedback", {})

    if not isinstance(metrics, Mapping):
        metrics = {}

    if not isinstance(feedback, Mapping):
        feedback = {}

    results = dict(metrics)
    results["feedback"] = feedback

    return draw_overlay(frame, landmarks, results)