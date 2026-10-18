# planner.py
# The program builder: scores every exercise for the athlete's sport and weak points, removes
# the ones they can't do (equipment, injuries) and fills a weekly plan.

# Exercise library
EXERCISES = [
    ("Back squat", "reps", {"strength": 3, "power": 1}, "squat", "barbell", "knee", []),
    ("Goblet squat", "reps", {"strength": 2, "core": 1}, "squat", "dumbbells", "knee", []),
    ("Box squat", "reps", {"strength": 2}, "squat", "none", "", []),
    ("Romanian deadlift", "reps", {"strength": 3, "speed": 1}, "hinge", "dumbbells", "back", []),
    ("Hip thrust", "reps", {"strength": 2, "speed": 1}, "hinge", "none", "", []),
    ("Nordic curl", "reps", {"strength": 2, "tendon": 2, "speed": 1}, "hinge", "none", "", ["soccer"]),
    ("Bulgarian split squat", "reps", {"strength": 2, "core": 1}, "single_leg", "none", "knee", []),
    ("Step-up", "reps", {"strength": 2}, "single_leg", "none", "", []),
    ("Wall sit", "hold", {"tendon": 2, "endurance": 1}, "leg_hold", "none", "", ["basketball"]),
    ("Copenhagen hold", "hold", {"core": 2, "tendon": 2}, "leg_hold", "none", "", ["soccer"]),
    ("Single-leg calf hold", "hold", {"tendon": 2}, "leg_hold", "none", "", ["tennis", "soccer", "basketball"]),
    ("Plank", "hold", {"core": 2, "endurance": 1}, "core", "none", "", []),
    ("Side plank", "hold", {"core": 3}, "core", "none", "", []),
    ("Hollow hold", "hold", {"core": 2}, "core", "none", "back", ["swimming"]),
    ("Countermovement jump", "reps", {"power": 3}, "jump", "none", "knee", ["basketball"]),
    ("Broad jump", "reps", {"power": 3, "speed": 1}, "jump", "none", "knee", []),
    ("Lateral bound", "reps", {"power": 2, "speed": 2}, "jump", "none", "knee", ["tennis", "basketball", "soccer"]),
    ("Med-ball rotational throw", "reps", {"power": 2, "core": 2}, "core", "medball", "back", ["tennis", "boxing"]),
    ("Sprint intervals", "timer", {"speed": 3, "endurance": 2}, "conditioning", "none", "", ["soccer"]),
    ("Shadow boxing rounds", "timer", {"endurance": 3, "speed": 1}, "conditioning", "none", "", ["boxing"]),
    ("Bike intervals", "timer", {"endurance": 3}, "conditioning", "none", "", ["swimming"]),
    ("Push-up", "reps", {"strength": 1, "endurance": 1, "core": 1}, "push", "none", "shoulder", []),
    ("Overhead press", "reps", {"strength": 2}, "push", "dumbbells", "shoulder", []),
    ("Pull-up", "reps", {"strength": 2, "endurance": 1}, "pull", "pullup_bar", "shoulder", ["swimming"]),
    ("Dumbbell row", "reps", {"strength": 2}, "pull", "dumbbells", "", []),
    ("Dead hang", "hold", {"endurance": 1, "tendon": 1}, "arm_hold", "pullup_bar", "", ["boxing", "swimming"]),
    ("Band shoulder hold", "hold", {"tendon": 2}, "arm_hold", "bands", "", ["tennis", "swimming"]),
    ("Mobility flow", "timer", {"mobility": 3}, "mobility", "none", "", []),
]

# Sport profiles
SPORTS = {
    "soccer": {"speed": 5, "power": 4, "endurance": 4, "strength": 3, "core": 3, "tendon": 3, "mobility": 2},
    "basketball": {"power": 5, "speed": 4, "tendon": 4, "strength": 3, "core": 3, "endurance": 3, "mobility": 2},
    "tennis": {"speed": 4, "core": 4, "endurance": 4, "power": 3, "tendon": 3, "mobility": 3, "strength": 2},
    "boxing": {"endurance": 5, "power": 4, "core": 4, "strength": 3, "speed": 3, "tendon": 2, "mobility": 2},
    "swimming": {"endurance": 4, "core": 4, "mobility": 4, "strength": 3, "tendon": 3, "power": 2, "speed": 2},
    "general": {"strength": 3, "endurance": 3, "core": 3, "mobility": 3, "power": 2, "speed": 2, "tendon": 2},
}


# Training days and season
DAY_TYPES = {
    "Lower body": ["squat", "hinge", "single_leg", "leg_hold", "core"],
    "Power": ["jump", "jump", "conditioning", "leg_hold", "core"],
    "Upper body": ["pull", "push", "core", "arm_hold", "core"],
    "Conditioning": ["conditioning", "mobility", "leg_hold", "core"],
}
WEEK = {2: ["Lower body", "Upper body"],
        3: ["Lower body", "Upper body", "Power"],
        4: ["Lower body", "Upper body", "Power", "Conditioning"]}


SEASON = {"off-season": "4 x 8", "pre-season": "4 x 5", "in-season": "2 x 5"}


# Filtering and scoring
def can_do(exercise, equipment, injuries):
    name, kind, qualities, group, needs, avoid, sports = exercise
    if needs != "none" and needs not in equipment:
        return False
    if avoid and avoid in injuries:
        return False
    return True


def score(exercise, sport, weak_points=()):
    name, kind, qualities, group, needs, avoid, sports = exercise
    total = 0
    for quality, amount in qualities.items():
        total += SPORTS[sport].get(quality, 0) * amount
        if quality in weak_points:
            total += 3 * amount
    if sport in sports:
        total += 4
    return total


# Weekly plan
def make_plan(sport, days=3, equipment=(), injuries=(), weak_points=(), season="off-season"):
    options = [e for e in EXERCISES if can_do(e, equipment, injuries)]
    options.sort(key=lambda e: score(e, sport, weak_points), reverse=True)

    plan = []
    used = set()
    for day_name in WEEK[days]:
        day = []
        for group in DAY_TYPES[day_name]:
            for exercise in options:
                name, kind = exercise[0], exercise[1]
                if exercise[3] == group and name not in used:
                    if kind == "reps":
                        dose = SEASON[season]
                    elif kind == "hold":
                        dose = "3 x 30 s"
                    else:
                        dose = "15 min"
                    day.append((name, dose))
                    used.add(name)
                    break
        plan.append((day_name, day))
    return plan


# Alternatives
def find_alternatives(name, sport, equipment=(), injuries=()):
    group = None
    for exercise in EXERCISES:
        if exercise[0].lower() == name.lower():
            group = exercise[3]
    options = [e for e in EXERCISES
               if e[3] == group and e[0].lower() != name.lower() and can_do(e, equipment, injuries)]
    options.sort(key=lambda e: score(e, sport), reverse=True)
    return [e[0] for e in options]


# Printing
def print_plan(plan):
    for day_name, exercises in plan:
        print(day_name)
        for name, dose in exercises:
            print("   -", name, dose)


# Example
if __name__ == "__main__":
    print_plan(make_plan("soccer", days=3, equipment=["dumbbells"], injuries=["knee"]))
