# rep_counter.py
# Counts reps from one joint angle (the knee for squats, the elbow for push-ups).
#
#   standing (angle > top) -> going down (angle < start) -> below the depth line -> back up = 1 rep
#   if you come back up before reaching the depth line it is a "half rep" (not counted)


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
        """Give it the angle for every frame. Returns "rep", "half" or None."""
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


# which angle to use and the thresholds for each exercise
REP_SETTINGS = {
    "squat": {"angle": "knee", "top": 160, "depth": 100, "start": 150},
    "push_up": {"angle": "elbow", "top": 155, "depth": 100, "start": 145},
}
