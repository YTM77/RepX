# workout.py
# Runs today's workout from the plan. Exercises the camera can already track (squats,
# push-ups, wall sits, planks, jumps) are tracked automatically; the others are logged
# by hand for now. Every set is saved to the database.

import random

from database import save_set, start_workout
from fake_athlete import FakeAthlete
from jump_tracker import JumpTracker, fake_jump_ankle
from main import Coach

TRACKED = {
    "Back squat": "squat", "Goblet squat": "squat", "Box squat": "squat",
    "Push-up": "push_up", "Wall sit": "wall_sit", "Plank": "plank",
    "Countermovement jump": "jump", "Broad jump": "jump",
}


# One tracked set with a fake athlete
def track_set(model, exercise, seconds=20, seed=1):
    if exercise == "jump":
        tracker = JumpTracker()
        r = random.Random(seed)
        for i in range(3):
            for y in fake_jump_ankle(r.uniform(30, 45)):
                tracker.update(y)
        return {"reps": len(tracker.jumps), "half_reps": 0, "hold_seconds": 0,
                "form_score": None, "tip": "Best jump " + str(tracker.best()) + " cm"}

    coach = Coach(model, exercise)
    athlete = FakeAthlete(exercise, seed=seed, half_rep_chance=0.2, lean_chance=0.2, drift=1.0)
    scores, tips = [], []
    for points in athlete.frames(seconds):
        old_message = coach.message
        coach.update(points)
        if coach.counter and coach.message != old_message and "form" in coach.message:
            scores.append(int(coach.message.split("form ")[1].rstrip(")")))
            tips.append(coach.message)

    if coach.timer:
        return {"reps": 0, "half_reps": 0, "hold_seconds": round(coach.timer.seconds, 1),
                "form_score": coach.timer.score(), "tip": "Hold score " + str(coach.timer.score())}
    average = round(sum(scores) / len(scores)) if scores else None
    worst_tip = min(zip(scores, tips))[1] if scores else ""
    return {"reps": coach.counter.reps, "half_reps": coach.counter.half_reps, "hold_seconds": 0,
            "form_score": average, "tip": worst_tip}


# The whole workout
def run_workout(db, athlete_id, model, day_type, session, readiness=None, sets_each=2):
    workout_id = start_workout(db, athlete_id, day_type, readiness)
    print("\n=== " + day_type + " workout ===")
    for number, (name, dose) in enumerate(session):
        print("\n" + name + " (" + dose + ")")
        for s in range(sets_each):
            if name in TRACKED:
                result = track_set(model, TRACKED[name], seed=number * 10 + s)
                print("  set", s + 1, "->", result["reps"], "reps,", result["half_reps"], "half reps,",
                      result["hold_seconds"], "s hold | form", result["form_score"], "|", result["tip"])
            else:
                result = {"reps": 8, "half_reps": 0, "hold_seconds": 0, "form_score": None,
                          "tip": "logged by hand (camera tracking coming soon)"}
                print("  set", s + 1, "->", result["tip"])
            save_set(db, workout_id, name, result["reps"], result["half_reps"], result["hold_seconds"],
                     result["form_score"], result["tip"])
        print("  rest 90 seconds...")
    return workout_id
