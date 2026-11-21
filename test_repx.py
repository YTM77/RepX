# test_repx.py
# Automatic tests for every part. Run with: pytest

from angles import Smoother, calculate_angle, get_angles
from coach import next_hold, next_weight, readiness, use_tool
from fake_athlete import FakeAthlete
from form_checker import FormChecker
from hold_timer import HoldTimer
from planner import make_plan
from rep_counter import RepCounter
from chatbot import reply
from database import add_athlete, connect, get_athlete, get_sets, save_set, start_workout
from jump_tracker import JumpTracker, fake_jump_ankle
from onboarding import EXAMPLE_ATHLETE, check_profile, safety_check
from progress import summary
from wearables import adjust_session, fake_watch_days, sync_watch, todays_readiness


# Helper
def run(exercise, seconds, **options):
    athlete = FakeAthlete(exercise, seed=1, **options)
    smoother = Smoother()
    return athlete, [smoother.smooth(get_angles(p)) for p in athlete.frames(seconds)]


# Angles
def test_right_angle():
    assert round(calculate_angle((0, 1), (0, 0), (1, 0))) == 90


def test_straight_line():
    assert round(calculate_angle((0, 0), (1, 0), (2, 0))) == 180


# Reps and form
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
    checker = FormChecker("squat")
    checker.update({"knee": 120, "trunk_lean": 20})
    score, tip, problems = checker.finish_rep()
    assert tip == "Go lower"
    assert score == 70


def test_good_squat():
    checker = FormChecker("squat")
    checker.update({"knee": 90, "trunk_lean": 20})
    assert checker.finish_rep() == (100, "Good rep!", [])


def test_push_up_body_line_rule():
    checker = FormChecker("push_up")
    checker.update({"elbow": 90, "hip": 140})
    score, tip, problems = checker.finish_rep()
    assert tip == "Keep your body straight"
    assert score == 70


# Hold timer
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


# Planner and coach
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


# Database
def test_save_and_load_athlete():
    db = connect(":memory:")
    athlete_id = add_athlete(db, EXAMPLE_ATHLETE)
    assert get_athlete(db, athlete_id)["sport"] == "soccer"
    workout_id = start_workout(db, athlete_id, "Lower body")
    save_set(db, workout_id, "Goblet squat", reps=8, form_score=90)
    assert get_sets(db, athlete_id)[0]["reps"] == 8


# Onboarding
def test_profile_checks():
    assert check_profile(EXAMPLE_ATHLETE) == []
    bad = dict(EXAMPLE_ATHLETE, sport="chess", days_per_week=7)
    assert len(check_profile(bad)) == 2


def test_safety_check():
    assert safety_check([False, False, False])[0]
    assert not safety_check([False, True, False])[0]


# Jumps
def test_jump_height():
    tracker = JumpTracker()
    for y in fake_jump_ankle(40):
        tracker.update(y)
    assert abs(tracker.best() - 40) < 3


# Smartwatch
def test_bad_night_means_lighter_day():
    db = connect(":memory:")
    athlete_id = add_athlete(db, EXAMPLE_ATHLETE)
    sync_watch(db, athlete_id, fake_watch_days(bad_last_night=True))
    score, advice = todays_readiness(db, athlete_id)
    assert score < 40
    assert adjust_session([("Goblet squat", "4 x 5")], score) == [("Goblet squat", "3 x 5")]


# Chat coach
def test_chat_swaps_exercise():
    answer, session = reply("Can I swap Goblet squat for Box squat?", ["Goblet squat"], EXAMPLE_ATHLETE)
    assert session == ["Box squat"]


def test_chat_never_trains_through_pain():
    answer, session = reply("my shoulder hurts", ["Push-up"], EXAMPLE_ATHLETE)
    assert "doctor" in answer


# Progress
def test_progress_summary():
    db = connect(":memory:")
    athlete_id = add_athlete(db, EXAMPLE_ATHLETE)
    workout_id = start_workout(db, athlete_id, "Lower body")
    save_set(db, workout_id, "Goblet squat", reps=8, form_score=60)
    save_set(db, workout_id, "Plank", hold_seconds=30, form_score=90)
    info = summary(db, athlete_id)
    assert info["reps"] == 8 and info["average_form"] == 75 and info["needs_work"] == "Goblet squat"
