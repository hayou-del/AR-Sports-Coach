import cv2
import numpy as np
import pytest

from ar.overlay import draw_overlay
from ar.overlay import draw_pipeline_overlay


@pytest.fixture
def frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)


def test_returns_annotated_copy_without_changing_original(frame):
    original = frame.copy()

    result = draw_overlay(
        frame,
        {
            "left_shoulder": (200, 100),
            "left_elbow": (170, 180),
            "left_wrist": (150, 250),
        },
        {
            "knee_angle": 90,
            "reps": 3,
            "feedback": {
                "message": "Keep going!",
                "status": "good",
            },
        },
    )

    assert result is not frame
    assert result.shape == frame.shape
    assert np.array_equal(frame, original)
    assert not np.array_equal(result, frame)


def test_draws_skeleton_connection(frame):
    result = draw_overlay(
        frame,
        {
            "left_shoulder": (100, 100),
            "left_elbow": (200, 100),
        },
        {},
    )

    # The line between the shoulder and elbow should be drawn.
    assert np.any(result[100, 120:180] != 0)


def test_handles_missing_landmarks_and_results(frame):
    result = draw_overlay(frame)

    assert result.shape == frame.shape
    assert not np.array_equal(result, frame)


def test_handles_invalid_landmark_coordinates(frame):
    result = draw_overlay(
        frame,
        {
            "left_shoulder": None,
            "left_elbow": ("invalid", 100),
            "right_shoulder": (9999, 9999),
        },
        {"reps": 2},
    )

    assert result.shape == frame.shape


def test_rejects_non_array_frame():
    with pytest.raises(TypeError):
        draw_overlay(None)


@pytest.mark.parametrize(
    "invalid_frame",
    [
        np.array([]),
        np.zeros((480, 640), dtype=np.uint8),
        np.zeros((480, 640, 4), dtype=np.uint8),
    ],
)
def test_rejects_invalid_frame_shape(invalid_frame):
    with pytest.raises(ValueError):
        draw_overlay(invalid_frame)
def test_draw_pipeline_overlay_accepts_pipeline_result(frame):
    original = frame.copy()

    result = draw_pipeline_overlay(
        frame,
        {
            "left_shoulder": (200, 100),
            "left_elbow": (170, 180),
        },
        {
            "metrics": {
                "knee_angle": 90.0,
                "reps": 3,
                "state": "bottom",
            },
            "feedback": {
                "message": "Keep going!",
                "status": "good",
            },
        },
    )

    assert result.shape == frame.shape
    assert not np.array_equal(result, original)
    assert np.array_equal(frame, original)


def test_overlay_displays_state_without_modifying_input(frame):
    original = frame.copy()

    result = draw_overlay(
        frame,
        {},
        {"knee_angle": 90, "reps": 2, "state": "bottom"},
    )

    assert result.shape == frame.shape
    assert not np.array_equal(result, original)
    assert np.array_equal(frame, original)
