# evaluate.py
# Tests every part on fake athletes the model never saw and prints the results.

import math

from sklearn.metrics import accuracy_score

from angles import Smoother, get_angles
from exercise_detector import make_dataset, train_model
from fake_athlete import FakeAthlete
from form_checker import SquatChecker
from hold_timer import HoldTimer
from rep_counter import RepCounter

# 1) Exercise recognition
print("1) Exercise recognition")
model = train_model(seeds=range(20))
X_test, y_test = make_dataset(seeds=range(100, 130))
accuracy = accuracy_score(y_test, model.predict(X_test))
print("   test windows:", len(y_test), "  accuracy:", round(accuracy, 3))

# 2) Rep counting and form tips
print("2) Rep counting and form tips (40 squat sets)")
exact_sets = 0
found = {"depth": [0, 0, 0], "chest": [0, 0, 0]}
for seed in range(200, 240):
    athlete = FakeAthlete("squat", seed=seed, half_rep_chance=0.25, lean_chance=0.25)
    counter, checker, smoother = RepCounter(), SquatChecker(), Smoother()
    results, t = [], 0.0
    for points in athlete.frames(30):
        angles = smoother.smooth(get_angles(points))
        checker.update(angles)
        if counter.update(angles["knee"]):
            results.append(checker.finish_rep()[2])
        t += 1 / athlete.fps

    finished = []
    for rep in athlete.reps:
        d = 14 / (174 - rep["lowest_knee"])
        back_up = rep["end_time"] - rep["length"] * math.acos(1 - 2 * d) / (2 * math.pi)
        if back_up + 0.1 <= t:
            finished.append(rep)
    true_full = sum(rep["full"] for rep in finished)
    if counter.reps == true_full and counter.half_reps == len(finished) - true_full:
        exact_sets += 1
    for rep, problems in zip(finished, results):
        for name, truth in (("depth", not rep["full"]), ("chest", rep["bad_lean"])):
            said = name in problems
            if said and truth:
                found[name][0] += 1
            elif said:
                found[name][1] += 1
            elif truth:
                found[name][2] += 1
print("   sets counted exactly:", exact_sets, "/ 40")
for name, (tp, fp, fn) in found.items():
    print("   tip '" + name + "': precision", round(tp / max(tp + fp, 1), 2), " recall", round(tp / max(tp + fn, 1), 2))

# 3) Hold timer
print("3) Hold timer (20 wall sits, half of them drift out of position)")
errors = []
for seed in range(300, 320):
    drift = 2.0 if seed % 2 else 0.0
    athlete = FakeAthlete("wall_sit", seed=seed, drift=drift)
    timer, smoother = HoldTimer(90, 10), Smoother()
    true_seconds, t = 0.0, 0.0
    for points in athlete.frames(25):
        timer.update(smoother.smooth(get_angles(points))["knee"])

        settle = min(t / 1.2, 1.0)
        knee = 172 - 82 * settle + max(t - 8.0, 0.0) * drift
        if abs(knee - 90) <= 10:
            true_seconds += 1 / athlete.fps
        t += 1 / athlete.fps
    errors.append(abs(timer.seconds - true_seconds))
print("   mean error:", round(sum(errors) / len(errors), 2), "s   max error:", round(max(errors), 2), "s")
