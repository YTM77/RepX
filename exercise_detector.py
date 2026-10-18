# exercise_detector.py
# Recognises the exercise from 1.6 seconds of joint angles with a Random Forest.
# An exercise is only locked after 3 confident guesses in a row agree.

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from angles import ANGLE_NAMES, Smoother, get_angles
from fake_athlete import EXERCISES, FakeAthlete

# Settings
WINDOW = 48
STEP = 8


# Features
def window_features(window):
    row = []
    for name in ANGLE_NAMES:
        values = np.array([frame[name] for frame in window])
        row += [values.mean(), values.std(), values.min(), values.max(),
                values.max() - values.min(), np.abs(np.diff(values)).mean()]
    return row


# Training data and model
def angles_from_athlete(athlete, seconds):
    smoother = Smoother()
    return [smoother.smooth(get_angles(points)) for points in athlete.frames(seconds)]


def make_dataset(seeds, seconds=12):
    X, y = [], []
    for exercise in EXERCISES:
        for seed in seeds:
            angles = angles_from_athlete(FakeAthlete(exercise, seed=seed), seconds)
            for start in range(0, len(angles) - WINDOW + 1, STEP):
                X.append(window_features(angles[start:start + WINDOW]))
                y.append(exercise)
    return np.array(X), np.array(y)


def train_model(seeds=range(20)):
    X, y = make_dataset(seeds)
    model = RandomForestClassifier(n_estimators=100, random_state=0)
    model.fit(X, y)
    return model


# Live detector
class ExerciseDetector:
    def __init__(self, model):
        self.model = model
        self.window = []
        self.frame_count = 0
        self.last_guesses = []
        self.exercise = None

    def update(self, angles):
        self.window.append(angles)
        if len(self.window) > WINDOW:
            self.window.pop(0)
        self.frame_count += 1
        if len(self.window) < WINDOW or self.frame_count % STEP != 0:
            return self.exercise

        probabilities = self.model.predict_proba([window_features(self.window)])[0]
        best = probabilities.argmax()
        guess = self.model.classes_[best] if probabilities[best] >= 0.7 else None

        self.last_guesses.append(guess)
        self.last_guesses = self.last_guesses[-3:]
        if len(self.last_guesses) == 3 and len(set(self.last_guesses)) == 1 and guess is not None:
            self.exercise = None if guess == "idle" else guess
        return self.exercise
