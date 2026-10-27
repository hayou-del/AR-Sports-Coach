import pytest
from ui.workout import WorkoutGoals, estimated_calories, goal_status


def test_goals_validate():
    with pytest.raises(ValueError):
        WorkoutGoals(repetitions=0)
    with pytest.raises(ValueError):
        WorkoutGoals(minutes=0)


def test_progress_and_estimate():
    goals = WorkoutGoals(repetitions=10, minutes=2, calorie_target=3)
    assert goal_status(goals, 9, 30) == {'repetitions': False, 'duration': False, 'calories': False}
    assert goal_status(goals, 10, 120) == {'repetitions': True, 'duration': True, 'calories': True}
    assert estimated_calories(-4) == 0
