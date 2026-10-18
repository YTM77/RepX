# RepX

RepX is our graduation project: an AI strength and conditioning coach for athletes of any sport.
The phone camera watches you train, recognises the exercise, counts your reps, times your holds
and tells you how to fix your form. It also builds a weekly plan for your sport and adjusts it
using your smartwatch data.

This repository is the **proof of concept** (about 10% of the full project). It is written in Python.
The final app will be built with Flutter.

**Team:** Youssef Tarek, Eyad Abdelbaky, Selim Khattab, Abdullah Kamal, Yassin Yasser
**Supervisor:** Dr. Walaa, School of Computing & Digital Technology, ESLSCA University

## What works so far

| File | What it does |
|---|---|
| `main.py` | Live coach: webcam or video, skeleton turns red on mistakes, reps and hold timer on screen |
| `angles.py` | Joint angles from body points (knee, hip, elbow, shoulder, trunk lean) |
| `exercise_detector.py` | Recognises the exercise from 1.6 s of movement (Random Forest) |
| `rep_counter.py` | Counts full reps and half reps |
| `hold_timer.py` | Times holds (wall sit, plank) only while you are in position, and scores them |
| `form_checker.py` | Form rules and tips like "Go lower" and "Keep your chest up" |
| `planner.py` | Builds a weekly plan for a sport (28 exercises, 6 sports) |
| `coach.py` | Progression, readiness from smartwatch data, and the tools the chat AI is allowed to use |
| `fake_athlete.py` | Fake athletes (moving stick figures) used for testing before we record real people |
| `evaluate.py` | Prints the results below |
| `test_repx.py` | Tests (run with `pytest`) |
| `prototype/index.html` | Clickable app prototype (open it in a browser) |

## How to run

```
pip install -r requirements.txt     # Python 3.9 - 3.12
python main.py                      # webcam, exercise detected automatically
python main.py --video squats.mp4   # use a video
python main.py --demo squat         # no camera needed
python evaluate.py                  # results
pytest                              # tests
```

Stand 2-3 m from the camera, side-on, with your whole body in view. Press `q` to quit.

## Results (on fake athletes the model never saw)

| Test | Result |
|---|---|
| Exercise recognition (6 classes, 7,200 windows) | 100% accuracy |
| Rep counting (40 squat sets with half reps) | 40 / 40 sets counted exactly |
| "Go lower" tip | precision 1.00, recall 1.00 |
| "Keep your chest up" tip | precision 1.00, recall 0.97 |
| Hold timer (20 wall sits) | 0.5 s average error |

These numbers only show that the logic works. Fake athletes are much easier than real video,
so the next step is recording 20-30 real people and testing on them.
