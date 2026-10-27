
"""Body pose detection using MediaPipe."""

from typing import Any, Dict, List, Optional

import cv2
import mediapipe as mp


class PoseDetector:
    """Detect body landmarks in webcam frames."""

    def __init__(
        self,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self._mp_pose = mp.solutions.pose
        self._pose = self._mp_pose.Pose(
            static_image_mode=False,
            model_complexity=model_complexity,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def detect(self, frame: Any) -> Dict[str, Any]:
        """Detect landmarks in a BGR OpenCV frame.

        Returns:
            A dictionary containing:
            - detected: whether a pose was detected
            - landmarks: named normalized landmark coordinates
            - image_landmarks: landmark coordinates in pixel space
        """
        if frame is None:
            return {
                "detected": False,
                "landmarks": {},
                "image_landmarks": {},
            }

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._pose.process(rgb_frame)

        if not results.pose_landmarks:
            return {
                "detected": False,
                "landmarks": {},
                "image_landmarks": {},
            }

        height, width = frame.shape[:2]
        landmarks: Dict[str, Dict[str, float]] = {}
        image_landmarks: Dict[str, Dict[str, float]] = {}

        for index, landmark in enumerate(
            results.pose_landmarks.landmark
        ):
            name = self._mp_pose.PoseLandmark(index).name.lower()

            landmarks[name] = {
                "x": float(landmark.x),
                "y": float(landmark.y),
                "z": float(landmark.z),
                "visibility": float(landmark.visibility),
            }

            image_landmarks[name] = {
                "x": float(landmark.x * width),
                "y": float(landmark.y * height),
                "z": float(landmark.z),
                "visibility": float(landmark.visibility),
            }

        return {
            "detected": True,
            "landmarks": landmarks,
            "image_landmarks": image_landmarks,
        }

    def close(self) -> None:
        """Release MediaPipe resources."""
        self._pose.close()

    def __enter__(self) -> "PoseDetector":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        self.close()
