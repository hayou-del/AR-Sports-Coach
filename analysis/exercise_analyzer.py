
import numpy as np
from .angle_smoother import AngleSmoother


def calculate_angle(a, b, c):
    """
    Calculate angle ABC in degrees.

    Each point is an (x, y) or (x, y, z) coordinate.
    Point b is the joint being measured.
    Returns None if the angle cannot be calculated.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)

    ba = a - b
    bc = c - b

    denominator = np.linalg.norm(ba) * np.linalg.norm(bc)

    # Avoid division by zero if points overlap.
    if denominator < 1e-8:
        return None

    cosine = np.dot(ba, bc) / denominator
    cosine = np.clip(cosine, -1.0, 1.0)

    return float(np.degrees(np.arccos(cosine)))


class SquatAnalyzer:
    """Analyze knee angles and count completed squat repetitions."""

    def __init__(self):
        self.reps = 0
        self.state = "standing"
        self.smoother = AngleSmoother(window_size=2)

    def reset(self):
        """Reset repetitions, movement state, and smoothing history."""
        self.reps = 0
        self.state = "standing"
        self.smoother.reset()

    def update(self, knee_angle):
        """
        Process one knee-angle measurement.

        Returns:
            (reps, state_or_message)
        """
        # Handle missing measurements.
        if knee_angle is None:
            return self.reps, "Landmark unavailable"

        # Reject invalid angles.
        if not isinstance(knee_angle, (int, float, np.number)):
            return self.reps, "Invalid knee angle"

        if not np.isfinite(knee_angle) or not 0 <= knee_angle <= 180:
            return self.reps, "Invalid knee angle"

        # Direct angle inputs are processed without smoothing.
        # This keeps the state machine predictable and testable.

        # Standing -> descending.
        if self.state == "standing":
            if knee_angle < 140:
                self.state = "descending"

            return self.reps, self.state

        # Descending -> bottom, or return to standing.
        elif self.state == "descending":
            if knee_angle < 100:
                self.state = "bottom"
            elif knee_angle > 160:
                self.state = "standing"

            return self.reps, self.state

        # Bottom -> standing completes a repetition.
        elif self.state == "bottom":
            if knee_angle > 160:
                self.reps += 1
                self.state = "standing"
                return self.reps, "Rep completed"

            return self.reps, self.state

        # Defensive fallback if the state is ever corrupted.
        self.state = "standing"
        return self.reps, "standing"

    def update_from_landmarks(self, hip, knee, ankle):
        """
        Calculate the knee angle from hip, knee, and ankle coordinates,
        smooth the measurement, and update the squat analyzer.
        """
        if hip is None or knee is None or ankle is None:
            return self.reps, "Landmark unavailable"

        try:
            knee_angle = calculate_angle(hip, knee, ankle)
        except (TypeError, ValueError):
            return self.reps, "Invalid landmark coordinates"

        if knee_angle is None:
            return self.reps, "Landmark unavailable"

        # Smooth only angles calculated from landmarks.
        smoothed_angle = self.smoother.update(knee_angle)

        if smoothed_angle is None:
            return self.reps, "Landmark unavailable"

        return self.update(smoothed_angle)

    def get_feedback(self, knee_angle):
        """Return simple feedback about squat depth."""
        if knee_angle is None:
            return "Cannot assess: knee landmark unavailable"

        if not isinstance(knee_angle, (int, float, np.number)):
            return "Cannot assess: invalid knee angle"

        if not np.isfinite(knee_angle) or not 0 <= knee_angle <= 180:
            return "Cannot assess: invalid knee angle"

        if knee_angle < 100:
            return "Target squat depth reached"

        if knee_angle < 140:
            return "Bend your knees a little more"

        return "Stand upright or begin your squat"


if __name__ == "__main__":
    # Standalone demonstration using simulated angles.
    analyzer = SquatAnalyzer()
    test_angles = [175, 130, 95, 120, 165]

    print("Testing direct angle analysis:")

    for angle in test_angles:
        reps, state = analyzer.update(angle)
        print(f"Angle: {angle} | Reps: {reps} | State: {state}")

    print("\nTesting landmark-based analysis:")

    analyzer.reset()

    # These points form a 90-degree angle at the knee.
    hip = (0, 1)
    knee = (0, 0)
    ankle = (1, 0)

    reps, state = analyzer.update_from_landmarks(hip, knee, ankle)
    print(f"Reps: {reps} | State: {state}")

