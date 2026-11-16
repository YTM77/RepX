# progress.py
# Progress screen: totals for the week, average form score, best hold, and which
# exercise needs work. Reads everything from the database.

from database import get_sets


# Weekly summary
def summary(db, athlete_id):
    sets = get_sets(db, athlete_id)
    if not sets:
        return None
    scores = [s["form_score"] for s in sets if s["form_score"] is not None]
    by_exercise = {}
    for s in sets:
        if s["form_score"] is not None:
            by_exercise.setdefault(s["exercise"], []).append(s["form_score"])
    worst = None
    if by_exercise:
        worst = min(by_exercise, key=lambda name: sum(by_exercise[name]) / len(by_exercise[name]))
    return {
        "workouts": len(set(s["workout_id"] for s in sets)),
        "sets": len(sets),
        "reps": sum(s["reps"] for s in sets),
        "half_reps": sum(s["half_reps"] for s in sets),
        "hold_seconds": round(sum(s["hold_seconds"] for s in sets), 1),
        "average_form": round(sum(scores) / len(scores)) if scores else None,
        "needs_work": worst,
    }


# Printing
def print_summary(info):
    if info is None:
        print("No workouts yet.")
        return
    print("Workouts:", info["workouts"], "  Sets:", info["sets"])
    print("Reps:", info["reps"], "  Half reps:", info["half_reps"])
    print("Total hold time:", info["hold_seconds"], "s")
    print("Average form score:", info["average_form"])
    if info["needs_work"]:
        print("Needs the most work:", info["needs_work"])
