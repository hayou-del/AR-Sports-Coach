
from collections import deque


class AngleSmoother:
    """Smooth angle measurements using a moving average."""

    def __init__(self, window_size=3):
        if window_size < 1:
            raise ValueError("window_size must be at least 1")

        self.angles = deque(maxlen=window_size)

    def update(self, angle):
        """Add a valid angle and return the current average."""

        if angle is None or not 0 <= angle <= 180:
            return None

        self.angles.append(float(angle))
        return sum(self.angles) / len(self.angles)

    def reset(self):
        """Clear stored measurements."""
        self.angles.clear()
