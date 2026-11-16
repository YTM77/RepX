# jump_tracker.py
# Measures jump height from the camera. We watch the ankle: when it leaves the ground the
# jump starts, when it comes back the jump ends. Height = g x flight time squared / 8.

GRAVITY = 9.81


# Jump height from flight time
def jump_height_cm(flight_time):
    return round(GRAVITY * flight_time ** 2 / 8 * 100, 1)


# Jump tracker
class JumpTracker:
    def __init__(self, fps=30, lift=0.005):
        self.fps = fps
        self.lift = lift
        self.ground = None
        self.in_air = False
        self.air_frames = 0
        self.jumps = []

    def update(self, ankle_y):
        if self.ground is None:
            self.ground = ankle_y
        if not self.in_air and ankle_y > self.ground:
            self.ground = ankle_y

        off_ground = ankle_y < self.ground - self.lift
        if off_ground:
            if not self.in_air:
                self.in_air = True
                self.air_frames = 0
            self.air_frames += 1
        elif self.in_air:
            self.in_air = False
            flight_time = self.air_frames / self.fps
            if flight_time > 0.15:
                height = jump_height_cm(flight_time)
                self.jumps.append(height)
                return height
        return None

    def best(self):
        return max(self.jumps) if self.jumps else 0


# Fake jump for testing
def fake_jump_ankle(height_cm, fps=30, ground=0.8, scale=0.5):
    flight_time = (8 * height_cm / 100 / GRAVITY) ** 0.5
    frames = [ground] * 15
    for i in range(round(flight_time * fps)):
        t = (i + 0.5) / fps
        frames.append(ground - GRAVITY / 2 * t * (flight_time - t) * scale)
    frames += [ground] * 15
    return frames
