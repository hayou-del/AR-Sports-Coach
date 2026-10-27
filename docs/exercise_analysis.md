
# Member 3 — Exercise Analysis Module

## Purpose
Calculate knee angles, track squat stages, count repetitions,
and generate basic coaching feedback.

## Files
- `exercise_analyzer.py`: main squat analysis logic
- `angle_smoother.py`: moving-average filter
- `test_exercise_analyzer.py`: analyzer tests
- `test_angle_smoother.py`: smoother tests

## Public API

### calculate_angle(a, b, c)
Calculates the angle at point b using three coordinate points.
Returns an angle in degrees, or None for degenerate geometry.

### SquatAnalyzer.update(knee_angle)
Processes a knee angle and returns:
(repetition_count, state_or_message)

### SquatAnalyzer.update_from_landmarks(hip, knee, ankle)
Calculates a knee angle from three coordinate points, smooths
the measurement, and updates the squat analyzer.

### SquatAnalyzer.get_feedback(knee_angle)
Returns a coaching-feedback string.

### SquatAnalyzer.reset()
Resets the repetition count, movement state, and smoothing history.

## Prototype thresholds
- Below 140 degrees: begin descending.
- Below 100 degrees while descending: reach bottom.
- Above 160 degrees while descending: return to standing without counting.
- Above 160 degrees while at bottom: complete a repetition.

These thresholds are initial prototype values and may need calibration.

## Integration questions
- What landmark format does Member 2 provide?
- Should the left or right knee be analyzed?
- How should Member 4 receive repetitions, state, and feedback?
- Which module will call the exercise analyzer?
