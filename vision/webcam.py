"""Webcam capture utilities for the AR Sports Coach application."""

import cv2
import sys


class WebcamError(RuntimeError):
    """Raised when the webcam cannot be used."""


class WebcamCamera:
    """Manage webcam initialization, frame capture, and cleanup."""

    def __init__(self, camera_index: int = 0) -> None:
        if not isinstance(camera_index, int) or isinstance(camera_index, bool):
            raise ValueError("camera_index must be an integer")
        if camera_index < 0:
            raise ValueError("camera_index must be non-negative")

        self.camera_index = camera_index
        self._capture = None

    @property
    def is_open(self) -> bool:
        """Return whether the webcam is open."""
        return self._capture is not None and self._capture.isOpened()

    def open(self) -> None:
        """Open the webcam or raise WebcamError."""
        if self.is_open:
            return

        if self._capture is not None:
            self._capture.release()
            self._capture = None

        # Windows DirectShow works with webcams that fail using the default backend.
        # Fall back to the default backend for portability.
        capture = cv2.VideoCapture(
            self.camera_index,
            cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY,
        )
        if not capture.isOpened() and sys.platform == "win32":
            capture.release()
            capture = cv2.VideoCapture(self.camera_index)

        if not capture.isOpened():
            capture.release()
            raise WebcamError(
                f"Could not open webcam at index {self.camera_index}"
            )

        self._capture = capture

    def read(self):
        """Return (True, frame) or (False, None) if capture fails."""
        if not self.is_open:
            raise WebcamError("Webcam is not open. Call open() first.")

        success, frame = self._capture.read()

        if not success or frame is None:
            return False, None

        if getattr(frame, "size", 0) == 0:
            return False, None

        return True, frame

    def release(self) -> None:
        """Release webcam resources."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.release()
