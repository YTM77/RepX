# form_checker.py
# Checks the form of every rep with fixed rules. Each rule looks at one joint angle:
# "reach below" means the angle must go under the limit at least once (depth),
# "stay below" means it must never go over the limit, "stay above" means never under it.
# Every broken rule takes 30 points off the form score and the first one becomes the tip.

# Form rules
RULES = {
    "squat": [
        ("knee", "reach below", 100, "Go lower"),
        ("trunk_lean", "stay below", 45, "Keep your chest up"),
    ],
    "push_up": [
        ("elbow", "reach below", 100, "Lower your chest more"),
        ("hip", "stay above", 155, "Keep your body straight"),
    ],
    "pull_up": [
        ("elbow", "reach below", 90, "Pull higher"),
        ("trunk_lean", "stay below", 30, "Don't swing"),
    ],
    "shoulder_press": [
        ("elbow", "reach below", 100, "Bring the weights down to your shoulders"),
        ("trunk_lean", "stay below", 20, "Don't lean back"),
    ],
    "plank": [
        ("hip", "stay above", 160, "Keep your hips in line"),
    ],
    "wall_sit": [
        ("knee", "stay below", 100, "Sit lower"),
        ("knee", "stay above", 80, "Come up a little"),
    ],
}


# Form checker
class FormChecker:
    def __init__(self, exercise):
        self.rules = RULES.get(exercise, [])
        self.reset()

    def reset(self):
        self.lowest = {}
        self.highest = {}

    def update(self, angles):
        for name, value in angles.items():
            self.lowest[name] = min(self.lowest.get(name, value), value)
            self.highest[name] = max(self.highest.get(name, value), value)

    def finish_rep(self):
        broken = []
        for angle, kind, limit, tip in self.rules:
            if angle not in self.lowest:
                continue
            if kind == "reach below" and self.lowest[angle] > limit:
                broken.append(tip)
            if kind == "stay below" and self.highest[angle] > limit:
                broken.append(tip)
            if kind == "stay above" and self.lowest[angle] < limit:
                broken.append(tip)

        score = max(100 - 30 * len(broken), 0)
        tip = broken[0] if broken else "Good rep!"
        self.reset()
        return score, tip, broken
