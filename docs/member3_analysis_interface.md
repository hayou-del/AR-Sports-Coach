# Member 3 — Exercise Analysis Interface

## Purpose
Calculate joint angles, track squat stages, count repetitions,
and provide basic exercise-analysis feedback.

## Module files
- analysis/exercise_analyzer.py
- analysis/angle_smoother.py
- tests/test_exercise_analyzer.py
- tests/test_angle_smoother.py

## Public API

### calculate_angle(a, b, c)
Calculates the angle at point b from three coordinate points.
Returns an angle in degrees, or None for degenerate geometry.

### SquatAnalyzer.update(knee_angle)
Processes a knee angle and returns:
(repetition_count, state_or_message)

### SquatAnalyzer.update_from_landmarks(hip, knee, ankle)
Calculates a knee angle from coordinates, smooths the measurement,
and updates the squat analyzer.

### SquatAnalyzer.get_feedback(knee_angle)
Returns a coaching-feedback string.

### SquatAnalyzer.reset()
Resets repetition count, movement state, and smoothing history.

## Prototype thresholds
- Below 140 degrees: begin descending.
- Below 100 degrees while descending: reach bottom.
- Above 160 degrees while descending: return to standing without counting.
- Above 160 degrees while at bottom: complete a repetition.

These are prototype values and require calibration.

## Integration contract
The AI Coach currently accepts a metrics dictionary, for example:
{
    "knee_angle": 90.0,
    "reps": 3,
    "state": "standing"
}

The integration pipeline currently exposes:
process_metrics(metrics: dict) -> dict

Its result contains:
- metrics: a copy of the supplied metrics
- feedback: the AI Coach result dictionary

## Open decisions
- Confirm landmark format with the vision module owner.
- Agree which knee or body side to analyze.
- Confirm how the analyzer will be called by the integration pipeline.
- Coordinate any public API changes with the project leader.
