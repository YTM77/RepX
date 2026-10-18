# main.py
# RepX live coach: open the webcam (or a video), find your body with MediaPipe,
# figure out the exercise, count reps, time holds and tell you how to fix your form.
#
#   python main.py                        -> webcam, exercise detected automatically
#   python main.py --video squats.mp4     -> use a video file instead
#   python main.py --exercise wall_sit    -> skip detection
#   python main.py --demo squat           -> no camera: a fake athlete on screen

import argparse
import time

import cv2
import numpy as np

from angles import Smoother, get_angles
from exercise_detector import ExerciseDetector, train_model
from fake_athlete import FakeAthlete
from form_checker import CHECKERS
from hold_timer import HOLD_SETTINGS, HoldTimer
from rep_counter import REP_SETTINGS, RepCounter

GREEN = (80, 200, 120)
RED = (60, 60, 230)
WHITE = (255, 255, 255)
LINES = [("shoulder", "elbow"), ("elbow", "wrist"), ("shoulder", "hip"),
         ("hip", "knee"), ("knee", "ankle")]


def points_from_mediapipe(landmarks, width, height):
    """Pick the side of the body that faces the camera and fix x for the screen shape."""
    lm = landmarks.landmark
    left = {"shoulder": 11, "elbow": 13, "wrist": 15, "hip": 23, "knee": 25, "ankle": 27}
    right = {"shoulder": 12, "elbow": 14, "wrist": 16, "hip": 24, "knee": 26, "ankle": 28}
    left_seen = sum(lm[i].visibility for i in left.values())
    right_seen = sum(lm[i].visibility for i in right.values())
    side = left if left_seen >= right_seen else right
    aspect = width / height
    return {name: (lm[i].x * aspect, lm[i].y) for name, i in side.items()}, aspect


class Coach:
    """Joins everything together for one training session."""

    def __init__(self, model, exercise=None):
        self.detector = ExerciseDetector(model)
        self.fixed_exercise = exercise
        self.smoother = Smoother()
        self.exercise = None
        self.message = "Get into position"
        self.bad_rep = False

    def start(self, exercise):
        self.exercise = exercise
        self.counter = None
        self.timer = None
        self.checker = None
        if exercise in REP_SETTINGS:
            s = REP_SETTINGS[exercise]
            self.counter = RepCounter(s["top"], s["depth"], s["start"])
            self.checker = CHECKERS[exercise]()
        if exercise in HOLD_SETTINGS:
            s = HOLD_SETTINGS[exercise]
            self.timer = HoldTimer(s["target"], s["tolerance"])
        self.message = "Detected: " + exercise.replace("_", " ")

    def update(self, points):
        angles = self.smoother.smooth(get_angles(points))
        exercise = self.fixed_exercise or self.detector.update(angles)
        if exercise and exercise != self.exercise:
            self.start(exercise)
        if self.exercise is None:
            return angles

        if self.counter:
            self.checker.update(angles)
            result = self.counter.update(angles[REP_SETTINGS[self.exercise]["angle"]])
            if result:
                score, tip, problems = self.checker.finish_rep()
                self.bad_rep = len(problems) > 0
                if result == "half":
                    tip = "Half rep - " + tip
                self.message = tip + " (form " + str(score) + ")"
        if self.timer:
            running = self.timer.update(angles[HOLD_SETTINGS[self.exercise]["angle"]])
            self.bad_rep = not running
            self.message = "Holding - keep still" if running else "Get back into position"
        return angles

    def panel_text(self):
        lines = ["Exercise: " + (self.exercise or "...").replace("_", " ")]
        if self.counter:
            lines.append("Reps: " + str(self.counter.reps) + "   half reps: " + str(self.counter.half_reps))
        if self.timer:
            lines.append("Hold: " + str(round(self.timer.seconds, 1)) + " s   score: " + str(self.timer.score()))
        lines.append(self.message)
        return lines


def draw(image, points, coach, scale_x, scale_y):
    color = RED if coach.bad_rep else GREEN
    pixel = {k: (int(x * scale_x), int(y * scale_y)) for k, (x, y) in points.items()}
    for a, b in LINES:
        cv2.line(image, pixel[a], pixel[b], color, 4)
    for p in pixel.values():
        cv2.circle(image, p, 6, WHITE, -1)
    cv2.rectangle(image, (0, 0), (image.shape[1], 30 + 28 * len(coach.panel_text())), (30, 30, 30), -1)
    for i, line in enumerate(coach.panel_text()):
        cv2.putText(image, line, (12, 32 + 28 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 2)


def run_camera(source, coach):
    import mediapipe as mp
    pose = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    video = cv2.VideoCapture(source)
    while video.isOpened():
        ok, frame = video.read()
        if not ok:
            break
        height, width = frame.shape[:2]
        result = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if result.pose_landmarks:
            points, aspect = points_from_mediapipe(result.pose_landmarks, width, height)
            coach.update(points)
            draw(frame, points, coach, width / aspect, height)
        cv2.imshow("RepX", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    video.release()
    cv2.destroyAllWindows()


def run_demo(exercise, coach, seconds=30):
    athlete = FakeAthlete(exercise, seed=7, half_rep_chance=0.3, lean_chance=0.3, drift=1.5)
    for points in athlete.frames(seconds):
        image = np.full((600, 600, 3), 40, dtype=np.uint8)
        coach.update(points)
        draw(image, points, coach, 600, 600)
        cv2.imshow("RepX demo", image)
        if cv2.waitKey(33) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()
    print("\n".join(coach.panel_text()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default=0, help="video file (default: webcam)")
    parser.add_argument("--exercise", default=None, help="squat, push_up, wall_sit or plank")
    parser.add_argument("--demo", default=None, help="run with a fake athlete, e.g. --demo squat")
    args = parser.parse_args()

    print("Training the exercise detector...")
    start = time.time()
    model = train_model()
    print("Done in", round(time.time() - start, 1), "seconds")

    coach = Coach(model, args.exercise)
    if args.demo:
        run_demo(args.demo, coach)
    else:
        run_camera(args.video, coach)
