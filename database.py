# database.py
# Saves everything in one small SQLite file (repx.db): athletes, workouts, sets,
# smartwatch days and chat messages. This is the app's memory.

import json
import sqlite3
from datetime import date

DB_FILE = "repx.db"


# Connect and create tables
def connect(file=DB_FILE):
    db = sqlite3.connect(file)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE IF NOT EXISTS athletes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, age INTEGER, sport TEXT, position TEXT, season TEXT,
            days_per_week INTEGER, equipment TEXT, injuries TEXT, weak_points TEXT
        );
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            athlete_id INTEGER, day TEXT, day_type TEXT, readiness INTEGER,
            FOREIGN KEY (athlete_id) REFERENCES athletes(id)
        );
        CREATE TABLE IF NOT EXISTS sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER, exercise TEXT, reps INTEGER, half_reps INTEGER,
            hold_seconds REAL, form_score INTEGER, tip TEXT,
            FOREIGN KEY (workout_id) REFERENCES workouts(id)
        );
        CREATE TABLE IF NOT EXISTS wearable_days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            athlete_id INTEGER, day TEXT, hrv REAL, resting_hr REAL, sleep_hours REAL,
            FOREIGN KEY (athlete_id) REFERENCES athletes(id)
        );
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            athlete_id INTEGER, sender TEXT, text TEXT,
            FOREIGN KEY (athlete_id) REFERENCES athletes(id)
        );
    """)
    return db


# Athletes
def add_athlete(db, athlete):
    cursor = db.execute(
        "INSERT INTO athletes (name, age, sport, position, season, days_per_week, equipment, injuries, weak_points) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (athlete["name"], athlete["age"], athlete["sport"], athlete["position"], athlete["season"],
         athlete["days_per_week"], json.dumps(athlete["equipment"]), json.dumps(athlete["injuries"]),
         json.dumps(athlete["weak_points"])))
    db.commit()
    return cursor.lastrowid


def get_athlete(db, athlete_id):
    row = db.execute("SELECT * FROM athletes WHERE id = ?", (athlete_id,)).fetchone()
    if row is None:
        return None
    athlete = dict(row)
    for key in ["equipment", "injuries", "weak_points"]:
        athlete[key] = json.loads(athlete[key])
    return athlete


# Workouts and sets
def start_workout(db, athlete_id, day_type, readiness=None, day=None):
    day = day or str(date.today())
    cursor = db.execute("INSERT INTO workouts (athlete_id, day, day_type, readiness) VALUES (?, ?, ?, ?)",
                        (athlete_id, day, day_type, readiness))
    db.commit()
    return cursor.lastrowid


def save_set(db, workout_id, exercise, reps=0, half_reps=0, hold_seconds=0, form_score=None, tip=""):
    db.execute("INSERT INTO sets (workout_id, exercise, reps, half_reps, hold_seconds, form_score, tip) "
               "VALUES (?, ?, ?, ?, ?, ?, ?)",
               (workout_id, exercise, reps, half_reps, hold_seconds, form_score, tip))
    db.commit()


def get_sets(db, athlete_id):
    rows = db.execute("SELECT sets.*, workouts.day FROM sets JOIN workouts ON sets.workout_id = workouts.id "
                      "WHERE workouts.athlete_id = ? ORDER BY sets.id", (athlete_id,)).fetchall()
    return [dict(row) for row in rows]


# Smartwatch days
def save_wearable_day(db, athlete_id, day, hrv, resting_hr, sleep_hours):
    db.execute("INSERT INTO wearable_days (athlete_id, day, hrv, resting_hr, sleep_hours) VALUES (?, ?, ?, ?, ?)",
               (athlete_id, day, hrv, resting_hr, sleep_hours))
    db.commit()


def get_wearable_days(db, athlete_id):
    rows = db.execute("SELECT * FROM wearable_days WHERE athlete_id = ? ORDER BY day", (athlete_id,)).fetchall()
    return [dict(row) for row in rows]


# Chat messages
def save_message(db, athlete_id, sender, text):
    db.execute("INSERT INTO chat_messages (athlete_id, sender, text) VALUES (?, ?, ?)", (athlete_id, sender, text))
    db.commit()


def get_messages(db, athlete_id):
    rows = db.execute("SELECT sender, text FROM chat_messages WHERE athlete_id = ? ORDER BY id",
                      (athlete_id,)).fetchall()
    return [dict(row) for row in rows]
