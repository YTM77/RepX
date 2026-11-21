# app.py
# The RepX demo app. A simple menu that joins every feature together:
# profile -> weekly plan -> smartwatch readiness -> today's workout -> chat coach -> progress.
# Run "python app.py" for the menu, or "python app.py --auto" to run the full demo by itself.

import sys

from chatbot import reply
from database import add_athlete, connect, get_athlete, save_message
from exercise_detector import train_fake_model
from onboarding import EXAMPLE_ATHLETE, check_profile, run_onboarding
from planner import make_plan, print_plan
from progress import print_summary, summary
from wearables import adjust_session, fake_watch_days, sync_watch, todays_readiness, weekly_insight
from workout import run_workout


# Helpers
def line(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def plan_for(athlete):
    return make_plan(athlete["sport"], athlete["days_per_week"], athlete["equipment"],
                     athlete["injuries"], athlete["weak_points"], athlete["season"])


def session_names(session):
    return [name for name, dose in session]


# Automatic demo
def auto_demo(db_file="repx_demo.db"):
    db = connect(db_file)
    line("1) Profile")
    print("Problems found:", check_profile(EXAMPLE_ATHLETE) or "none")
    athlete_id = add_athlete(db, EXAMPLE_ATHLETE)
    athlete = get_athlete(db, athlete_id)
    print("Saved athlete", athlete_id, ":", athlete["name"], "-", athlete["sport"], athlete["position"],
          "| injuries:", athlete["injuries"])

    line("2) Weekly plan")
    plan = plan_for(athlete)
    print_plan(plan)

    line("3) Smartwatch")
    print("Synced", sync_watch(db, athlete_id, fake_watch_days(bad_last_night=True)), "days")
    score, advice = todays_readiness(db, athlete_id)
    print("Readiness today:", score, "-", advice)
    day_type, session = plan[0]
    session = adjust_session(session, score)
    print("Today's adjusted session:", session)

    line("4) Today's workout")
    print("Training the exercise detector...")
    model = train_fake_model()
    run_workout(db, athlete_id, model, day_type, session)

    line("5) Chat coach")
    names = session_names(session)
    for message in ["What's my workout today?", "My knee hurts on goblet squat",
                    "Can I swap Goblet squat for Box squat?", "Why do I do Nordic curl?",
                    "I only have 20 minutes"]:
        answer, names = reply(message, names, athlete)
        save_message(db, athlete_id, "athlete", message)
        save_message(db, athlete_id, "coach", answer)
        print("You:  ", message)
        print("Coach:", answer)

    line("6) Progress")
    print_summary(summary(db, athlete_id))
    print(weekly_insight(db, athlete_id))


# Menu
def menu():
    db = connect()
    athlete, plan, model, session = None, None, None, None
    while True:
        print("\nRepX menu")
        print(" 1. Create profile")
        print(" 2. See my weekly plan")
        print(" 3. Sync smartwatch")
        print(" 4. Do today's workout")
        print(" 5. Chat with the coach")
        print(" 6. See my progress")
        print(" 0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            athlete = run_onboarding()
            athlete["id"] = add_athlete(db, athlete)
            plan = plan_for(athlete)
            session = plan[0][1]
            print("Profile saved!")
        elif choice == "0":
            break
        elif athlete is None:
            print("Create your profile first (option 1).")
        elif choice == "2":
            print_plan(plan)
        elif choice == "3":
            print("Synced", sync_watch(db, athlete["id"], fake_watch_days()), "days")
            score, advice = todays_readiness(db, athlete["id"])
            print("Readiness:", score, "-", advice)
            session = adjust_session(plan[0][1], score)
        elif choice == "4":
            if model is None:
                print("Training the exercise detector...")
                model = train_fake_model()
            run_workout(db, athlete["id"], model, plan[0][0], session)
        elif choice == "5":
            names = session_names(session)
            print("Type 'back' to go back to the menu.")
            while True:
                message = input("You: ")
                if message.strip().lower() == "back":
                    break
                answer, names = reply(message, names, athlete)
                save_message(db, athlete["id"], "athlete", message)
                save_message(db, athlete["id"], "coach", answer)
                print("Coach:", answer)
        elif choice == "6":
            print_summary(summary(db, athlete["id"]))
            print(weekly_insight(db, athlete["id"]))


# Start
if __name__ == "__main__":
    if "--auto" in sys.argv:
        auto_demo()
    else:
        menu()
