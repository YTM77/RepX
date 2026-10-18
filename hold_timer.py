# hold_timer.py
# Times isometric holds (wall sit, plank...). The timer only runs while you are
# in the right position AND holding still. At the end it gives a hold score.

import numpy as np


class HoldTimer:
    def __init__(self, target, tolerance, fps=30):
        self.target = target
        self.tolerance = tolerance
        self.fps = fps
        self.recent = []         # last ~0.6 seconds of angles
        self.held_angles = []    # every angle while the timer was running
        self.seconds = 0.0

    def update(self, angle):
        """Call once per frame. Returns True if the timer is running."""
        self.recent.append(angle)
        if len(self.recent) > int(0.6 * self.fps):
            self.recent.pop(0)
        if len(self.recent) < 5:
            return False

        average = sum(self.recent) / len(self.recent)
        in_position = abs(average - self.target) <= self.tolerance
        # holding still = the angle is not trending up or down and not shaking a lot
        times = np.arange(len(self.recent)) / self.fps
        speed = np.polyfit(times, self.recent, 1)[0]  # degrees per second
        shaking = np.std(self.recent)
        still = abs(speed) < 25 and shaking < 0.6 * self.tolerance

        if in_position and still:
            self.seconds += 1 / self.fps
            self.held_angles.append(angle)
            return True
        return False

    def score(self):
        """0-100: how close to the target and how steady you were."""
        if len(self.held_angles) < 2:
            return 0
        errors = np.abs(np.array(self.held_angles) - self.target)
        accuracy = max(0.0, 1 - errors.mean() / self.tolerance)
        stability = max(0.0, 1 - np.std(self.held_angles) / self.tolerance)
        return round(100 * (0.6 * accuracy + 0.4 * stability))

    def fatigue_drift(self):
        """Degrees per second you drift away from the target as you get tired."""
        if len(self.held_angles) < self.fps:
            return 0.0
        errors = np.abs(np.array(self.held_angles) - self.target)
        times = np.arange(len(errors)) / self.fps
        return float(np.polyfit(times, errors, 1)[0])


HOLD_SETTINGS = {
    "wall_sit": {"angle": "knee", "target": 90, "tolerance": 10},
    "plank": {"angle": "body_line", "target": 78, "tolerance": 12},
}
