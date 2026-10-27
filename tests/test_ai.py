import unittest

from ai.coaching_engine import CoachingEngine


class TestCoachingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CoachingEngine()

    def test_empty_metrics(self):
        result = self.engine.generate_feedback({})
        self.assertEqual(result["status"], "general")

    def test_missing_angle(self):
        result = self.engine.generate_feedback({
            "repetitions": 2,
        })
        self.assertEqual(result["status"], "general")
        self.assertEqual(result["repetitions"], 2)

    def test_standing_feedback(self):
        result = self.engine.generate_feedback({
            "movement_state": "standing",
            "angles": {"mean_knee": 170},
        })
        self.assertEqual(result["status"], "standing")

    def test_low_knee_angle_gives_tip(self):
        result = self.engine.generate_feedback({
            "movement_state": "standing",
            "angles": {"mean_knee": 120},
        })
        self.assertEqual(result["status"], "standing")
        self.assertTrue(result["tips"])

    def test_invalid_angle_is_not_assessed(self):
        result = self.engine.generate_feedback({
            "movement_state": "standing",
            "valid_measurement": False,
            "angles": {"mean_knee": 200},
        })
        self.assertEqual(
            result["status"],
            "measurement_unavailable",
        )


if __name__ == "__main__":
    unittest.main()