# hold_timer.py
# Times isometric holds (wall sit, plank). The timer only runs while the athlete is in the
# right position and holding still, then the hold gets a score and a fatigue drift.

import numpy as np


# ---------- Hold timer ----------
class HoldTimer:
    def __init__(self, target, tolerance, fps=30):
        self.target = target
        self.tolerance = tolerance
        self.fps = fps
        self.recent = []
        self.held_angles = []
        self.seconds = 0.0

    def update(self, angle):
        self.recent.append(angle)
        if len(self.recent) > int(0.6 * self.fps):
            self.recent.pop(0)
        if len(self.recent) < 5:
            return False

        average = sum(self.recent) / len(self.recent)
        in_position = abs(average - self.target) <= self.tolerance

        times = np.arange(len(self.recent)) / self.fps
        speed = np.polyfit(times, self.recent, 1)[0]
        shaking = np.std(self.recent)
        still = abs(speed) < 25 and shaking < 0.6 * self.tolerance

        if in_position and still:
            self.seconds += 1 / self.fps
            self.held_angles.append(angle)
            return True
        return False

    # ---------- Hold score ----------
    def score(self):
        if len(self.held_angles) < 2:
            return 0
        errors = np.abs(np.array(self.held_angles) - self.target)
        accuracy = max(0.0, 1 - errors.mean() / self.tolerance)
        stability = max(0.0, 1 - np.std(self.held_angles) / self.tolerance)
        return round(100 * (0.6 * accuracy + 0.4 * stability))

    def fatigue_drift(self):
        if len(self.held_angles) < self.fps:
            return 0.0
        errors = np.abs(np.array(self.held_angles) - self.target)
        times = np.arange(len(errors)) / self.fps
        return float(np.polyfit(times, errors, 1)[0])


# ---------- Settings for each hold ----------
HOLD_SETTINGS = {
    "wall_sit": {"angle": "knee", "target": 90, "tolerance": 10},
    "plank": {"angle": "body_line", "target": 78, "tolerance": 12},
}
