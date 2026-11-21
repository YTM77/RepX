# make_dataset.py
# Step 1 of training. Turns the Kaggle "Workout/Exercises Video" dataset into numbers.
# Every video goes through MediaPipe, becomes joint angles, and is cut into 1.6 second
# windows. Each window is saved as one row of exercise_data.csv with its exercise name.
# Put the Kaggle folders (squat, push-up, plank, pull Up, shoulder press...) inside "dataset".

import csv
import os

import cv2
import mediapipe as mp

from angles import Smoother, get_angles
from exercise_detector import FEATURE_NAMES, STEP, WINDOW, window_features
from main import points_from_mediapipe

# Settings
DATASET_FOLDER = "dataset"
OUTPUT_FILE = "exercise_data.csv"
EXERCISES = ["squat", "push_up", "plank", "pull_up", "shoulder_press"]


# Folder name to exercise name
def exercise_name(folder):
    return folder.lower().replace("-", "_").replace(" ", "_")


# Angles from one video
def angles_from_video(path):
    video = cv2.VideoCapture(path)
    fps = video.get(cv2.CAP_PROP_FPS) or 30
    skip = max(round(fps / 30), 1)
    smoother = Smoother()
    angles = []
    frame_number = 0
    with mp.solutions.pose.Pose() as pose:
        while True:
            ok, frame = video.read()
            if not ok:
                break
            frame_number += 1
            if frame_number % skip != 0:
                continue
            height, width = frame.shape[:2]
            result = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if result.pose_landmarks:
                points, aspect = points_from_mediapipe(result.pose_landmarks, width, height)
                angles.append(smoother.smooth(get_angles(points)))
    video.release()
    return angles


# Build the table
rows = 0
with open(OUTPUT_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["exercise", "video"] + FEATURE_NAMES)
    for folder in sorted(os.listdir(DATASET_FOLDER)):
        exercise = exercise_name(folder)
        if exercise not in EXERCISES:
            continue
        for video_name in sorted(os.listdir(os.path.join(DATASET_FOLDER, folder))):
            angles = angles_from_video(os.path.join(DATASET_FOLDER, folder, video_name))
            for start in range(0, len(angles) - WINDOW + 1, STEP):
                features = window_features(angles[start:start + WINDOW])
                writer.writerow([exercise, folder + "/" + video_name] + [round(f, 2) for f in features])
                rows += 1
            print(exercise, video_name, len(angles), "frames")

print("Saved", rows, "rows to", OUTPUT_FILE)
