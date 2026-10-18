# form_checker.py
# Checks the form of every rep with simple rules, gives a form score (100 minus penalties)
# and one tip like "Go lower".

# ---------- Squat form ----------
class SquatChecker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.lowest_knee = 180
        self.most_lean = 0

    def update(self, angles):
        self.lowest_knee = min(self.lowest_knee, angles["knee"])
        self.most_lean = max(self.most_lean, angles["trunk_lean"])

    def finish_rep(self):
        problems = []
        score = 100
        if self.lowest_knee > 100:
            problems.append("depth")
            score -= 30
        if self.most_lean > 45:
            problems.append("chest")
            score -= 25

        tip = "Good rep!"
        if "depth" in problems:
            tip = "Go lower"
        elif "chest" in problems:
            tip = "Keep your chest up"

        self.reset()
        return score, tip, problems


# ---------- Push-up form ----------
class PushUpChecker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.lowest_elbow = 180
        self.worst_sag = 0

    def update(self, angles):
        self.lowest_elbow = min(self.lowest_elbow, angles["elbow"])
        self.worst_sag = max(self.worst_sag, 180 - angles["hip"])

    def finish_rep(self):
        problems = []
        score = 100
        if self.lowest_elbow > 100:
            problems.append("depth")
            score -= 30
        if self.worst_sag > 25:
            problems.append("hips")
            score -= 25

        tip = "Good rep!"
        if "depth" in problems:
            tip = "Lower your chest more"
        elif "hips" in problems:
            tip = "Keep your body straight"

        self.reset()
        return score, tip, problems


# ---------- Checker for each exercise ----------
CHECKERS = {"squat": SquatChecker, "push_up": PushUpChecker}
