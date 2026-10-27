
import cv2
from vision.pose_detector import PoseDetector

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("Erreur : impossible d'ouvrir la webcam.")
    raise SystemExit(1)

try:
    with PoseDetector() as detector:
        print("Webcam active. Appuie sur Q pour quitter.")

        while True:
            success, frame = camera.read()

            if not success:
                print("Impossible de lire une image.")
                break

            result = detector.detect(frame)

            if result["detected"]:
                cv2.putText(
                    frame,
                    "Pose detected",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

                for point in result["image_landmarks"].values():
                    if point["visibility"] > 0.5:
                        cv2.circle(
                            frame,
                            (int(point["x"]), int(point["y"])),
                            4,
                            (0, 255, 0),
                            -1,
                        )
            else:
                cv2.putText(
                    frame,
                    "No pose detected",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("AR Sports Coach - Pose Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    camera.release()
    cv2.destroyAllWindows()
