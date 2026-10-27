# AI Coaching Module ÔÇö Interface

## Responsibility

The ai/ module converts exercise metrics into understandable coaching
feedback.

It does not:
- Capture webcam frames.
- Detect body landmarks.
- Calculate joint angles.
- Count repetitions.
- Draw AR overlays.
- Manage the user interface.

These responsibilities belong to vision/, analysis/, ar/, and ui/.

## Public API

    from src.ai import CoachingEngine

    engine = CoachingEngine()
    feedback = engine.generate_feedback(metrics)

## Input metrics

The current implementation accepts these optional fields:

| Field | Type | Description |
|---|---|---|
| detected | bool | Whether a pose was detected |
| valid_measurement | bool | Whether the measurement is reliable |
| movement_state | str | Current movement phase |
| repetitions | int | Completed repetition count |
| angles.mean_knee | number | Mean knee angle in degrees |

The exact field names must be agreed with the analysis module.

## Output format

The coaching engine returns:

| Field | Type | Description |
|---|---|---|
| message | str | Main coaching message |
| severity | str | info or warning |
| tips | list[str] | Additional coaching suggestions |
| status | str | Coaching state |
| repetitions | int or null | Repetition count if available |

Example:

    {
        "message": "Lower yourself in a controlled way.",
        "severity": "info",
        "tips": ["Keep your movement smooth and balanced."],
        "status": "descending",
        "repetitions": 2
    }

## Integration

analysis/ produces the metrics.
ai/ converts them into feedback.
integration/ coordinates the modules.
ar/ and ui/ display the feedback.

## Limitations

The initial rules are squat-oriented and are not a medical assessment.
Thresholds should be validated against representative exercise recordings.
