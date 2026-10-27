# AR Sports Coach — Final Architecture

## Data flow

```text
WebcamCamera (vision/webcam.py)
   -> PoseDetector (vision/pose_detector.py)
   -> live_demo.py (select visible hip/knee/ankle landmarks)
   -> CoachingPipeline (integration/pipeline.py)
        -> SquatAnalyzer (analysis/exercise_analyzer.py)
             -> AngleSmoother (analysis/angle_smoother.py)
        -> CoachingEngine (ai/coaching_engine.py)
             -> feedback_rules (ai/feedback_rules.py)
   -> result: {metrics, feedback}
   -> render_dashboard (ui/live_hud.py)
        -> AR skeleton/overlay (ar/overlay.py)
        -> dashboard UI components (ui/dashboard.py, ui/components.py)
   -> OpenCV full-screen window

Workout setup (ui/workout_setup.py) -> WorkoutGoals (ui/workout.py)
WorkoutAudio (ui/audio.py) -> generated sports music / notification
```

## Directory map

| Path | Responsibility |
|---|---|
| `vision/` | Camera frames and MediaPipe pose landmarks |
| `analysis/` | Knee angles, smoothing, squat movement states and repetitions |
| `ai/` | Rule-based coaching feedback |
| `integration/` | Unify analysis and coaching results |
| `ar/` | Skeleton and visual overlay |
| `ui/` | Neon dashboard, workout setup, goal tracking, synthesized audio |
| `config/` | Shared configuration package |
| `assets/` | Model and icon asset directories |
| `docs/` | Detailed module interface references |
| `tests/` | Automated tests and manual webcam check |
| `live_demo.py` | Actual live application and keyboard controls |
| `main.py` | Sample non-camera integration example |

## Core contracts

- `PoseDetector.detect(frame)` supplies detection status and named image landmarks with `x`, `y`, and `visibility`.
- `SquatAnalyzer.update_from_landmarks(hip, knee, ankle)` tracks squat state and repetitions; `calculate_angle` computes the knee angle.
- `CoachingPipeline.process_landmarks(hip, knee, ankle)` returns `{"metrics": {"knee_angle": ..., "reps": ..., "state": ...}, "feedback": {"message": ..., "status": ...}}`.
- `render_dashboard(frame, landmarks, result, ...)` draws the live view and metrics; it does not calculate exercise repetitions.
- `ui/workout.py` handles session goals and illustrative calorie estimates; `ui/audio.py` handles locally generated music.

## Limitations and verification

This prototype supports **squats only** and estimates form from a single webcam view. Camera angle and occlusion affect accuracy. Calorie values are illustrative, not measured. Run `python -m pytest -q`; verify the actual camera with `python -m tests.manual_pose_webcam` on Windows.
