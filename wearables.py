# wearables.py
# Smartwatch part. The real app will read Apple Health / Health Connect. For now we make
# fake smartwatch days (HRV, resting heart rate, sleep), save them, and use the last
# 30 days to work out today's readiness and change today's workout.

import random
from datetime import date, timedelta

from coach import readiness
from database import get_wearable_days, save_wearable_day


# Fake smartwatch data
def fake_watch_days(days=30, seed=1, bad_last_night=False):
    r = random.Random(seed)
    today = date.today()
    result = []
    for i in range(days, 0, -1):
        result.append({
            "day": str(today - timedelta(days=i - 1)),
            "hrv": round(r.gauss(62, 5), 1),
            "resting_hr": round(r.gauss(55, 2), 1),
            "sleep_hours": round(r.uniform(6.5, 8.5), 1),
        })
    if bad_last_night:
        result[-1].update({"hrv": 55.0, "resting_hr": 58.0, "sleep_hours": 5.5})
    return result


def sync_watch(db, athlete_id, days):
    for d in days:
        save_wearable_day(db, athlete_id, d["day"], d["hrv"], d["resting_hr"], d["sleep_hours"])
    return len(days)


# Today's readiness
def todays_readiness(db, athlete_id):
    days = get_wearable_days(db, athlete_id)
    if len(days) < 8:
        return None, "Wear your watch for a week so we can learn your normal"
    history, today = days[-31:-1], days[-1]
    return readiness(today["hrv"], [d["hrv"] for d in history],
                     today["resting_hr"], [d["resting_hr"] for d in history],
                     today["sleep_hours"])


# Changing today's workout
def adjust_session(session, score):
    if score is None or 40 <= score <= 70:
        return session
    changed = []
    for name, dose in session:
        if score < 40 and " x " in dose:
            sets, reps = dose.split(" x ")
            dose = str(max(1, round(int(sets) * 0.7))) + " x " + reps
        changed.append((name, dose))
    return changed


# Weekly insight
def weekly_insight(db, athlete_id):
    days = get_wearable_days(db, athlete_id)[-7:]
    if not days:
        return "No watch data yet."
    sleep = sum(d["sleep_hours"] for d in days) / len(days)
    hrv = sum(d["hrv"] for d in days) / len(days)
    text = "This week you slept " + str(round(sleep, 1)) + " h a night and your HRV averaged " + str(round(hrv)) + ". "
    if sleep < 7:
        text += "Try to sleep a bit more, your recovery will be better."
    else:
        text += "Nice, your sleep is on track."
    return text
