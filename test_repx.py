# test_repx.py
# Automatic tests for every part. Run with: pytest

from angles import Smoother, calculate_angle, get_angles
from coach import next_hold, next_weight, readiness, use_tool
from fake_athlete import FakeAthlete
from form_checker import SquatChecker
from hold_timer import HoldTimer
from planner import make_plan
from rep_counter import RepCounter


# ---------- Helper ----------
def run(exercise, seconds, **options):
    athlete = FakeAthlete(exercise, seed=1, **options)
    smoother = Smoother()
    return athlete, [smoother.smooth(get_angles(p)) for p in athlete.frames(seconds)]


# ---------- Angles ----------
def test_right_angle():
    assert round(calculate_angle((0, 1), (0, 0), (1, 0))) == 90


def test_straight_line():
    assert round(calculate_angle((0, 0), (1, 0), (2, 0))) == 180


# ---------- Reps and form ----------
def test_counts_squats():
    athlete, angles = run("squat", 20)
    counter = RepCounter()
    for a in angles:
        counter.update(a["knee"])
    assert counter.reps >= 6
    assert counter.half_reps == 0


def test_half_reps_are_not_counted():
    athlete, angles = run("squat", 20, half_rep_chance=1.0)
    counter = RepCounter()
    for a in angles:
        counter.update(a["knee"])
    assert counter.reps == 0
    assert counter.half_reps >= 6


def test_go_lower_tip():
    checker = SquatChecker()
    checker.update({"knee": 120, "trunk_lean": 20})
    score, tip, problems = checker.finish_rep()
    assert tip == "Go lower"
    assert score == 70


# ---------- Hold timer ----------
def test_wall_sit_timer():
    athlete, angles = run("wall_sit", 15)
    timer = HoldTimer(90, 10)
    for a in angles:
        timer.update(a["knee"])
    assert 12 < timer.seconds < 15
    assert timer.score() > 50


def test_timer_stops_when_you_stand_up():
    timer = HoldTimer(90, 10)
    for i in range(90):
        timer.update(170)
    assert timer.seconds == 0


# ---------- Planner and coach ----------
def test_plan_follows_injuries():
    plan = make_plan("soccer", days=3, injuries=["knee"])
    names = [name for day, exercises in plan for name, dose in exercises]
    assert "Countermovement jump" not in names
    assert "Nordic curl" in names


def test_progression():
    assert next_weight(60, [8, 8, 8], (6, 8), 90) == (65, "All sets done, add weight")
    assert next_weight(60, [8, 8, 8], (6, 8), 60)[0] == 57.0
    assert next_hold(30, 85) == 35


def test_readiness_low_after_bad_night():
    score, advice = readiness(40, [60, 62, 58, 61, 59], 68, [55, 56, 54, 55, 57], 5)
    assert score < 40


def test_coach_cannot_add_unknown_exercise():
    athlete = {"sport": "soccer", "equipment": [], "injuries": ["knee"]}
    ok, message, session = use_tool("replace_exercise", {"old": "Box squat", "new": "Laser squat"},
                                    ["Box squat"], athlete)
    assert not ok
    ok, message, session = use_tool("replace_exercise", {"old": "Box squat", "new": "Step-up"},
                                    ["Box squat"], athlete)
    assert ok and session == ["Step-up"]
