import numpy as np
from ui.live_hud import render_dashboard


def test_dashboard_expands_frame_without_mutating_source():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    before = frame.copy()
    result = {"metrics": {"knee_angle": 95, "reps": 2, "state": "standing"},
              "feedback": {"message": "Keep going", "status": "good"}}
    output = render_dashboard(frame, {}, result, fps=24)
    assert output.shape[0] >= 480
    assert output.shape[1] > 640
    np.testing.assert_array_equal(frame, before)


def test_dashboard_handles_missing_data():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    assert render_dashboard(frame, None, None).shape[1] > 640
