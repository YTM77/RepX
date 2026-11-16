# onboarding.py
# Asks the athlete the setup questions (sport, position, season, days, equipment, injuries)
# plus a short safety check, and makes sure every answer is valid before saving it.

from planner import SPORTS, SEASON

EQUIPMENT_OPTIONS = ["none", "dumbbells", "barbell", "bands", "pullup_bar", "medball"]
INJURY_OPTIONS = ["none", "knee", "back", "shoulder"]
QUALITIES = ["strength", "power", "speed", "endurance", "core", "tendon", "mobility"]
SAFETY_QUESTIONS = [
    "Has a doctor ever told you not to exercise?",
    "Do you feel chest pain when you exercise?",
    "Do you lose balance or feel dizzy when training?",
]


# Checking answers
def check_profile(athlete):
    problems = []
    if not athlete["name"].strip():
        problems.append("Name can't be empty")
    if athlete["age"] < 18:
        problems.append("RepX is for athletes 18 and older for now")
    if athlete["sport"] not in SPORTS:
        problems.append("Sport must be one of: " + ", ".join(SPORTS))
    if athlete["season"] not in SEASON:
        problems.append("Season must be one of: " + ", ".join(SEASON))
    if athlete["days_per_week"] not in [2, 3, 4]:
        problems.append("Training days must be 2, 3 or 4")
    for item in athlete["equipment"]:
        if item not in EQUIPMENT_OPTIONS:
            problems.append("Unknown equipment: " + item)
    for item in athlete["injuries"]:
        if item not in INJURY_OPTIONS:
            problems.append("Unknown injury: " + item)
    for item in athlete["weak_points"]:
        if item not in QUALITIES:
            problems.append("Unknown weak point: " + item)
    return problems


def safety_check(answers):
    if any(answers):
        return False, "Please talk to a doctor before starting. RepX will keep your plan very light."
    return True, "You're good to go!"


# Asking the questions
def ask(question, options=None):
    if options:
        question += " (" + "/".join(options) + ")"
    return input(question + ": ").strip().lower()


def ask_list(question, options):
    answer = ask(question + " - separate with commas", options)
    items = [a.strip() for a in answer.split(",") if a.strip() and a.strip() != "none"]
    return items


def run_onboarding():
    print("\nWelcome to RepX! Let's set up your profile.\n")
    while True:
        athlete = {
            "name": input("Your name: ").strip(),
            "age": int(ask("Your age") or 0),
            "sport": ask("Your sport", list(SPORTS)),
            "position": ask("Your position (or 'none')"),
            "season": ask("Part of the season", list(SEASON)),
            "days_per_week": int(ask("Training days per week", ["2", "3", "4"]) or 0),
            "equipment": ask_list("Equipment you have", EQUIPMENT_OPTIONS),
            "injuries": ask_list("Any injuries", INJURY_OPTIONS),
            "weak_points": ask_list("What do you want to improve", QUALITIES),
        }
        problems = check_profile(athlete)
        if not problems:
            break
        print("\nPlease fix these:")
        for p in problems:
            print(" -", p)

    print("\nQuick safety check (yes/no):")
    answers = [ask(q) == "yes" for q in SAFETY_QUESTIONS]
    ok, message = safety_check(answers)
    print(message)
    athlete["safe"] = ok
    return athlete


# Example athlete for the demo
EXAMPLE_ATHLETE = {
    "name": "Omar", "age": 20, "sport": "soccer", "position": "winger", "season": "pre-season",
    "days_per_week": 3, "equipment": ["dumbbells"], "injuries": ["back"], "weak_points": ["power"],
}
