# fake_athlete.py
# Fake athletes: moving stick figures with random body size, position, speed, camera tilt and
# noise. We use them to test the code before recording real people, because we know the right
# answer (number of reps, bad reps, time in position).

import math
import random

# Exercises
EXERCISES = ["squat", "push_up", "wall_sit", "plank", "jumping_jack", "idle"]


# Helper
def move(point, length, angle_from_up, direction=1):
    a = math.radians(angle_from_up)
    return (point[0] + direction * length * math.sin(a), point[1] - length * math.cos(a))


# Fake athlete
class FakeAthlete:
    def __init__(self, exercise, seed=0, fps=30, half_rep_chance=0.0, lean_chance=0.0, drift=0.0):
        self.exercise = exercise
        self.fps = fps
        self.half_rep_chance = half_rep_chance
        self.lean_chance = lean_chance
        self.drift = drift
        self.random = random.Random(seed)
        r = self.random

        size = r.uniform(0.8, 1.1)
        self.shin, self.thigh, self.torso = 0.17 * size, 0.18 * size, 0.22 * size
        self.upper_arm, self.forearm = 0.12 * size, 0.11 * size
        self.x = r.uniform(0.38, 0.52)
        self.floor = r.uniform(0.76, 0.82)
        self.noise = r.uniform(0.002, 0.007)
        self.tilt = r.uniform(-8, 8)
        self.speed = {"squat": r.uniform(2.0, 3.2), "push_up": r.uniform(1.6, 2.6),
                      "jumping_jack": r.uniform(0.9, 1.3)}.get(exercise, 1.0)

        self.reps = []
        self.rep = None
        self.rep_start = 0.0

    # True answer for each squat rep
    def new_squat_rep(self, t):
        r = self.random
        half = r.random() < self.half_rep_chance
        lean = r.random() < self.lean_chance
        rep = {
            "full": not half,
            "lowest_knee": r.uniform(116, 126) if half else r.uniform(78, 92),
            "lean": r.uniform(50, 58) if lean else r.uniform(22, 36),
            "bad_lean": lean,
            "length": self.speed * r.uniform(0.9, 1.1),
        }
        rep["end_time"] = t + rep["length"]
        self.reps.append(rep)
        self.rep = rep
        self.rep_start = t

    # Body positions
    def standing_body(self, knee, lean, arm, elbow, shin_tilt=0.4):
        bend = 180 - knee
        ankle = (self.x, self.floor - 0.02)
        knee_point = move(ankle, self.shin, shin_tilt * bend)
        hip = move(knee_point, self.thigh, bend - shin_tilt * bend, direction=-1)
        shoulder = move(hip, self.torso, lean)
        elbow_point = (shoulder[0] + self.upper_arm * math.sin(math.radians(arm)),
                       shoulder[1] + self.upper_arm * math.cos(math.radians(arm)))
        forearm_angle = arm + (180 - elbow)
        wrist = (elbow_point[0] + self.forearm * math.sin(math.radians(forearm_angle)),
                 elbow_point[1] + self.forearm * math.cos(math.radians(forearm_angle)))
        return {"ankle": ankle, "knee": knee_point, "hip": hip, "shoulder": shoulder,
                "elbow": elbow_point, "wrist": wrist}

    def floor_body(self, elbow):
        body = self.shin + self.thigh + self.torso
        ankle = (self.x - 0.3, self.floor - 0.02)
        a, b = self.upper_arm, self.forearm
        arm_length = math.sqrt(a * a + b * b - 2 * a * b * math.cos(math.radians(elbow)))
        shoulder_y = self.floor - arm_length
        rise = math.asin(min(0.99, (ankle[1] - shoulder_y) / body))
        shoulder = (ankle[0] + body * math.cos(rise), shoulder_y)
        wrist = (shoulder[0] + 0.01, self.floor)

        dx, dy = wrist[0] - shoulder[0], wrist[1] - shoulder[1]
        d = max(1e-6, min(math.hypot(dx, dy), a + b - 1e-6))
        along = (a * a - b * b + d * d) / (2 * d)
        side = math.sqrt(max(0.0, a * a - along * along))
        elbow_point = (shoulder[0] + along * dx / d - side * dy / d,
                       shoulder[1] + along * dy / d + side * dx / d)
        hip_part = (self.shin + self.thigh) / body
        knee_part = self.shin / body
        hip = (ankle[0] + hip_part * (shoulder[0] - ankle[0]), ankle[1] + hip_part * (shoulder[1] - ankle[1]))
        knee = (ankle[0] + knee_part * (shoulder[0] - ankle[0]), ankle[1] + knee_part * (shoulder[1] - ankle[1]))
        return {"ankle": ankle, "knee": knee, "hip": hip, "shoulder": shoulder,
                "elbow": elbow_point, "wrist": wrist}

    # Movement for each exercise
    def body_at(self, t):
        ex = self.exercise
        if ex == "squat":
            if self.rep is None or t - self.rep_start >= self.rep["length"]:
                self.new_squat_rep(t)
            progress = (t - self.rep_start) / self.rep["length"]
            down = (1 - math.cos(2 * math.pi * progress)) / 2
            knee = 174 - (174 - self.rep["lowest_knee"]) * down
            lean = 6 + (self.rep["lean"] - 6) * down
            return self.standing_body(knee, lean, arm=60 + 30 * down, elbow=165)
        if ex == "wall_sit":
            settle = min(t / 1.2, 1.0)
            drift = max(t - 8.0, 0.0) * self.drift
            knee = 172 - 82 * settle + drift + 1.2 * math.sin(t * 1.7)
            return self.standing_body(knee, 4 + 1.5 * math.sin(t), arm=8, elbow=170, shin_tilt=0.0)
        if ex == "jumping_jack":
            progress = (t % self.speed) / self.speed
            up = (1 - math.cos(2 * math.pi * progress)) / 2
            knee = 176 - 14 * abs(math.sin(2 * math.pi * progress))
            body = self.standing_body(knee, 3, arm=15 + 155 * up, elbow=170)
            hop = 0.03 * abs(math.sin(2 * math.pi * progress))
            return {k: (p[0], p[1] - hop) for k, p in body.items()}
        if ex == "idle":
            knee = 174 + 3 * math.sin(t * 0.5 + 1)
            return self.standing_body(knee, 4 + 2.5 * math.sin(t * 0.7), arm=10 + 8 * math.sin(t * 0.9), elbow=165)
        if ex == "push_up":
            progress = (t % self.speed) / self.speed
            elbow = 168 - 83 * (1 - math.cos(2 * math.pi * progress)) / 2
            return self.floor_body(elbow)
        if ex == "plank":
            return self.floor_body(90)
        raise ValueError("unknown exercise: " + ex)

    # What the camera sees
    def points_at(self, t):
        body = self.body_at(t)
        c, s = math.cos(math.radians(self.tilt)), math.sin(math.radians(self.tilt))
        points = {}
        for name, (x, y) in body.items():
            x, y = x - 0.5, y - 0.6
            x, y = 0.5 + c * x - s * y, 0.6 + s * x + c * y
            points[name] = (x + self.random.gauss(0, self.noise), y + self.random.gauss(0, self.noise))
        return points

    def frames(self, seconds):
        for i in range(int(seconds * self.fps)):
            yield self.points_at(i / self.fps)
