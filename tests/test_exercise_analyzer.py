
import unittest

from analysis.exercise_analyzer import SquatAnalyzer


class TestSquatAnalyzer(unittest.TestCase):


    def test_complete_squat_counts_one_rep(self):
        analyzer = SquatAnalyzer()

        for angle in [175, 130, 95, 120, 165]:
            reps, state = analyzer.update(angle)
            print(
                f"Angle: {angle}, Reps: {reps}, State: {state}",
                flush=True,
            )

        self.assertEqual(reps, 1)

    def test_partial_squat_does_not_count(self):
        analyzer = SquatAnalyzer()

        for angle in [175, 130, 120, 165]:
            reps, state = analyzer.update(angle)

        self.assertEqual(reps, 0)

    def test_missing_angle_preserves_state_and_count(self):
        analyzer = SquatAnalyzer()
        analyzer.update(130)

        old_state = analyzer.state
        old_reps = analyzer.reps

        analyzer.update(None)

        self.assertEqual(analyzer.state, old_state)
        self.assertEqual(analyzer.reps, old_reps)

    def test_invalid_angle_preserves_state_and_count(self):
        analyzer = SquatAnalyzer()
        analyzer.update(130)

        old_state = analyzer.state
        old_reps = analyzer.reps

        analyzer.update(200)

        self.assertEqual(analyzer.state, old_state)
        self.assertEqual(analyzer.reps, old_reps)

    def test_reset_clears_count_and_state(self):
        analyzer = SquatAnalyzer()

        for angle in [175, 130, 95, 165]:
            analyzer.update(angle)

        analyzer.reset()

        self.assertEqual(analyzer.reps, 0)
        self.assertEqual(analyzer.state, "standing")

    def test_update_from_landmarks_handles_missing_point(self):
        analyzer = SquatAnalyzer()

        reps, message = analyzer.update_from_landmarks(
            hip=(0, 0),
            knee=None,
            ankle=(1, 1),
        )

        self.assertEqual(reps, 0)
        self.assertEqual(message, "Landmark unavailable")
        self.assertEqual(analyzer.state, "standing")

    def test_update_from_landmarks_calculates_angle(self):
        analyzer = SquatAnalyzer()

        reps, state = analyzer.update_from_landmarks(
            hip=(0, 1),
            knee=(0, 0),
            ankle=(1, 0),
        )

        self.assertEqual(reps, 0)
        self.assertEqual(state, "descending")

    def test_counts_two_consecutive_squats(self):
        analyzer = SquatAnalyzer()

        angles = [
            175, 130, 95, 165,  # Squat 1
            175, 130, 95, 165,  # Squat 2
        ]

        for angle in angles:
            reps, state = analyzer.update(angle)

        self.assertEqual(reps, 2)
        self.assertEqual(analyzer.state, "standing")
    
    def test_feedback_for_squat_depth(self):
        analyzer = SquatAnalyzer()

        self.assertEqual(
            analyzer.get_feedback(90),
            "Target squat depth reached",
        )

        self.assertEqual(
            analyzer.get_feedback(120),
            "Bend your knees a little more",
        )

    def test_feedback_handles_invalid_measurements(self):
        analyzer = SquatAnalyzer()

        self.assertEqual(
            analyzer.get_feedback(None),
            "Cannot assess: knee landmark unavailable",
        )

        self.assertEqual(
            analyzer.get_feedback(200),
            "Cannot assess: invalid knee angle",
        )
    



if __name__ == "__main__":
    unittest.main()
