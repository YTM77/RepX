# angles.py
# Turns body points into joint angles.
# A point is just (x, y). For MediaPipe points we multiply x by (width / height)
# first, otherwise the angles are wrong on wide videos.

import math


def calculate_angle(a, b, c):
    """Angle at point b (in degrees) between the lines b->a and b->c."""
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    dot = ba[0] * bc[0] + ba[1] * bc[1]
    length = math.hypot(ba[0], ba[1]) * math.hypot(bc[0], bc[1])
    if length == 0:
        return 0.0
    cos_value = max(-1.0, min(1.0, dot / length))
    return math.degrees(math.acos(cos_value))


def angle_from_vertical(top, bottom):
    """How much the line bottom->top leans away from straight up (0 = standing tall)."""
    dx = top[0] - bottom[0]
    dy = bottom[1] - top[1]  # y goes down in images
    return abs(math.degrees(math.atan2(dx, dy)))


def get_angles(points):
    """points is a dict like {"shoulder": (x, y), "hip": (x, y), ...} for the side facing the camera."""
    knee = calculate_angle(points["hip"], points["knee"], points["ankle"])
    hip = calculate_angle(points["shoulder"], points["hip"], points["knee"])
    elbow = calculate_angle(points["shoulder"], points["elbow"], points["wrist"])
    shoulder = calculate_angle(points["elbow"], points["shoulder"], points["hip"])
    trunk_lean = angle_from_vertical(points["shoulder"], points["hip"])
    body_line = angle_from_vertical(points["shoulder"], points["ankle"])
    return {"knee": knee, "hip": hip, "elbow": elbow, "shoulder": shoulder,
            "trunk_lean": trunk_lean, "body_line": body_line}


ANGLE_NAMES = ["knee", "hip", "elbow", "shoulder", "trunk_lean", "body_line"]


class Smoother:
    """Averages the last few values of each angle so the numbers don't jump around."""

    def __init__(self, size=5):
        self.size = size
        self.history = {}

    def smooth(self, angles):
        result = {}
        for name, value in angles.items():
            values = self.history.setdefault(name, [])
            values.append(value)
            if len(values) > self.size:
                values.pop(0)
            result[name] = sum(values) / len(values)
        return result
