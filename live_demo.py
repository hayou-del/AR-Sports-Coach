"""Interactive AR Sports Coach demonstration.

Q: quit, R: reset repetitions, P: pause, L: switch tracking leg.
"""
import argparse
import time
import cv2
from vision.webcam import WebcamCamera, WebcamError
from vision.pose_detector import PoseDetector
from integration.pipeline import CoachingPipeline
from ui.live_hud import render_dashboard
from ui.workout import WorkoutGoals, estimated_calories, goal_status
from ui.audio import WorkoutAudio

LANDMARK_NAMES = (
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
)


def run(camera_index=0, goals=None):
    pipeline = CoachingPipeline()
    goals = goals or WorkoutGoals()
    audio = WorkoutAudio()
    elapsed = 0.0
    completed = set()
    fullscreen = True
    window = "AR Sports Coach | Live Training"
    side = "left"
    paused = False
    last_frame = time.perf_counter()
    last_image = None
    print("AR Sports Coach | Q quit | R reset | P pause | L switch leg")
    try:
        with WebcamCamera(camera_index) as camera, PoseDetector() as detector:
            cv2.namedWindow(window, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(window, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            while True:
                success, frame = camera.read()
                if not success:
                    print("Camera stopped delivering frames.")
                    break
                now = time.perf_counter()
                fps = 1.0 / max(now - last_frame, 1e-6)
                delta = min(now - last_frame, 0.5)
                last_frame = now
                if not paused:
                    elapsed += delta
                if not paused or last_image is None:
                    detection = detector.detect(frame)
                    landmarks = {}
                    result = {
                        "metrics": {"knee_angle": None, "reps": pipeline.analyzer.reps if hasattr(pipeline.analyzer, 'reps') else 0, "state": "waiting"},
                        "feedback": {"message": "Stand in camera view", "status": "waiting"},
                    }
                    if detection["detected"]:
                        points = detection["image_landmarks"]
                        landmarks = {
                            name: (int(p["x"]), int(p["y"]))
                            for name in LANDMARK_NAMES
                            if (p := points.get(name)) and p.get("visibility", 0) >= 0.5
                        }
                        leg = [points.get(f"{side}_{part}") for part in ("hip", "knee", "ankle")]
                        if all(p and p.get("visibility", 0) >= 0.5 for p in leg):
                            result = pipeline.process_landmarks(*[(p["x"], p["y"]) for p in leg])
                        else:
                            result["feedback"]["message"] = f"Show your {side} hip, knee and ankle"
                    reps = result.get('metrics', {}).get('reps', 0)
                    status = goal_status(goals, reps, elapsed)
                    newly_completed = {name for name, reached in status.items() if reached} - completed
                    if newly_completed:
                        completed.update(newly_completed)
                        audio.notify()
                        print('GOAL ACHIEVED:', ', '.join(sorted(newly_completed)))
                    workout = {'goals': goals, 'elapsed': elapsed, 'reps': reps,
                               'calories': estimated_calories(elapsed), 'completed': bool(completed)}
                    last_image = render_dashboard(frame, landmarks, result, fps=fps, side=side, workout=workout, paused=paused)
                image = last_image.copy()
                if paused:
                    cv2.putText(image, "PAUSED", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 200, 255), 2)
                cv2.imshow(window, image)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                if key == ord("p"):
                    paused = not paused
                if key == ord("r"):
                    elapsed = 0.0
                    completed.clear()
                    pipeline.reset()
                    last_image = None
                if key == ord("m"):
                    audio.toggle()
                if key in (ord("f"), 27):
                    fullscreen = not fullscreen
                    cv2.setWindowProperty(window, cv2.WND_PROP_FULLSCREEN,
                                          cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL)
                if key == ord("l"):
                    side = "right" if side == "left" else "left"
                    pipeline.reset()  # Don't combine repetitions from two different legs.
                    last_image = None
    except (WebcamError, cv2.error) as error:
        print(f"Camera/display error: {error}")
        return 1
    except Exception as error:
        print(f"Demo error ({type(error).__name__}): {error}")
        return 1
    finally:
        audio.close()
        cv2.destroyAllWindows()
        print("AR Sports Coach stopped.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Live AR Sports Coach demo")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (default: 0)")
    parser.add_argument('--no-setup', action='store_true', help='Use default goals without setup window')
    args = parser.parse_args()
    if args.no_setup:
        goals = WorkoutGoals()
    else:
        from ui.workout_setup import choose_goals
        goals = choose_goals()
        if goals is None:
            return
    raise SystemExit(run(args.camera, goals))


if __name__ == "__main__":
    main()
