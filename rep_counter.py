# rep_counter.py
# Counts reps from one joint angle. Going down past the depth line and back up is one rep;
# coming back up before the depth line is a half rep (not counted).

# Rep counter
class RepCounter:
    def __init__(self, top=160, depth=100, start=150):
        self.top = top
        self.depth = depth
        self.start = start
        self.state = "up"
        self.lowest = 180
        self.reps = 0
        self.half_reps = 0

    def update(self, angle):
        if self.state == "up":
            if angle < self.start:
                self.state = "down"
                self.lowest = angle
        else:
            self.lowest = min(self.lowest, angle)
            if angle > self.top:
                self.state = "up"
                if self.lowest <= self.depth:
                    self.reps += 1
                    return "rep"
                self.half_reps += 1
                return "half"
        return None


# Settings for each exercise
REP_SETTINGS = {
    "squat": {"angle": "knee", "top": 160, "depth": 100, "start": 150},
    "push_up": {"angle": "elbow", "top": 155, "depth": 100, "start": 145},
}
