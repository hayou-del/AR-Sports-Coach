
import unittest

from analysis.angle_smoother import AngleSmoother


class TestAngleSmoother(unittest.TestCase):

    def test_averages_measurements(self):
        smoother = AngleSmoother(window_size=3)

        self.assertAlmostEqual(smoother.update(90), 90)
        self.assertAlmostEqual(smoother.update(96), 93)
        self.assertAlmostEqual(smoother.update(93), 93)

    def test_old_measurements_are_removed(self):
        smoother = AngleSmoother(window_size=3)

        smoother.update(90)
        smoother.update(90)
        smoother.update(90)

        result = smoother.update(120)

        self.assertAlmostEqual(result, 100)

    def test_invalid_measurement_is_ignored(self):
        smoother = AngleSmoother(window_size=3)
        smoother.update(90)

        self.assertIsNone(smoother.update(None))
        self.assertIsNone(smoother.update(200))

        self.assertAlmostEqual(smoother.update(90), 90)

    def test_reset_clears_history(self):
        smoother = AngleSmoother(window_size=3)
        smoother.update(90)
        smoother.reset()

        self.assertAlmostEqual(smoother.update(120), 120)


if __name__ == "__main__":
    unittest.main()

