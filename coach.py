# coach.py
# The coach logic that doesn't need the language model: progression, readiness from
# smartwatch data, and the tools the chat AI is allowed to use (every request is checked).

import statistics

from planner import EXERCISES, can_do, find_alternatives


# ---------- Progression ----------
def next_weight(weight, reps_done, rep_range, form_score, upper_body=False):
    low, high = rep_range
    if form_score < 70:
        return round(weight * 0.95, 1), "Form slipped, lower the weight a bit"
    if all(r >= high for r in reps_done):
        step = 2.5 if upper_body else 5
        return weight + step, "All sets done, add weight"
    if any(r < low for r in reps_done):
        return weight, "Keep the same weight"
    return weight, "Same weight, try for more reps"


def next_hold(seconds, hold_score):
    if hold_score >= 80:
        return seconds + 5
    return seconds


# ---------- Readiness ----------
def readiness(hrv_today, hrv_history, rhr_today, rhr_history, sleep_hours, sleep_goal=8):
    hrv_z = (hrv_today - statistics.mean(hrv_history)) / (statistics.stdev(hrv_history) or 1)
    rhr_z = (rhr_today - statistics.mean(rhr_history)) / (statistics.stdev(rhr_history) or 1)
    sleep = max(-0.5, min(0.25, sleep_hours / sleep_goal - 1)) * 4
    value = 50 + 10 * (hrv_z - 0.8 * rhr_z + sleep)
    value = max(0, min(100, value))
    if value < 40:
        advice = "Take it easy: 30% less volume today"
    elif value > 70:
        advice = "You're fresh: go for progress"
    else:
        advice = "Train as planned"
    return round(value), advice


# ---------- Tools for the chat AI ----------
TOOLS = [
    {"name": "replace_exercise", "description": "Swap one exercise in today's session for another",
     "parameters": {"old": "string", "new": "string"}},
    {"name": "set_session_length", "description": "Make today's session fit in N minutes",
     "parameters": {"minutes": "number"}},
    {"name": "find_alternatives", "description": "List exercises that can replace one exercise",
     "parameters": {"exercise": "string"}},
]


def use_tool(name, args, session, athlete):
    names = [e[0].lower() for e in EXERCISES]

    if name == "replace_exercise":
        old, new = args.get("old", ""), args.get("new", "")
        if old.lower() not in [s.lower() for s in session]:
            return False, old + " is not in today's session", session
        if new.lower() not in names:
            return False, new + " is not in our exercise library", session
        exercise = EXERCISES[names.index(new.lower())]
        if not can_do(exercise, athlete["equipment"], athlete["injuries"]):
            return False, new + " is not safe or possible for this athlete", session
        session = [exercise[0] if s.lower() == old.lower() else s for s in session]
        return True, "Replaced " + old + " with " + exercise[0], session

    if name == "set_session_length":
        minutes = args.get("minutes", 0)
        if minutes < 10:
            return False, "A session needs at least 10 minutes", session
        keep = max(1, minutes // 8)
        return True, "Session shortened to " + str(minutes) + " minutes", session[:keep]

    if name == "find_alternatives":
        options = find_alternatives(args.get("exercise", ""), athlete["sport"],
                                    athlete["equipment"], athlete["injuries"])
        return True, ", ".join(options[:3]), session

    return False, "Unknown tool: " + name, session
