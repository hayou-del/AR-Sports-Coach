"""Workout goals and session state; no camera or UI dependencies."""
from dataclasses import dataclass

@dataclass(frozen=True)
class WorkoutGoals:
    repetitions: int = 12
    minutes: int = 5
    calorie_target: float = 0.0

    def __post_init__(self):
        if not 1 <= self.repetitions <= 1000:
            raise ValueError('Repetition goal must be between 1 and 1000')
        if not 1 <= self.minutes <= 180:
            raise ValueError('Duration must be between 1 and 180 minutes')
        if not 0 <= self.calorie_target <= 1000:
            raise ValueError('Calorie target must be between 0 and 1000')


def estimated_calories(active_seconds):
    """Illustrative non-personalized display estimate, NOT measured energy use."""
    return max(0.0, active_seconds) / 60 * 3.0


def goal_status(goals, reps, elapsed):
    calories = estimated_calories(elapsed)
    reached = {
        'repetitions': reps >= goals.repetitions,
        'duration': elapsed >= goals.minutes * 60,
    }
    if goals.calorie_target > 0:
        reached['calories'] = calories >= goals.calorie_target
    return reached
