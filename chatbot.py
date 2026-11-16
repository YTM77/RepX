# chatbot.py
# The chat coach. In the final app a large language model (LLM) will understand the message
# and pick a tool. For now we understand simple messages with keywords, then use the same
# checked tools from coach.py, so the plan can only change in safe ways.

import re

from coach import use_tool
from planner import EXERCISES

PAIN_WORDS = ["pain", "hurts", "hurt", "injury", "injured", "sore"]


# Finding exercise names in a message
def find_exercises(message):
    found = []
    text = message.lower()
    for e in EXERCISES:
        if e[0].lower() in text:
            found.append(e[0])
    found.sort(key=lambda name: text.index(name.lower()))
    return found


# Answering a message
def reply(message, session, athlete):
    text = message.lower()
    names = find_exercises(message)

    if any(word in text for word in PAIN_WORDS):
        if names:
            ok, options, session = use_tool("find_alternatives", {"exercise": names[0]}, session, athlete)
            answer = "Sorry to hear that. Stop " + names[0] + " for today."
            if options:
                answer += " You can try: " + options + "."
            return answer + " If the pain stays, please see a physio or doctor.", session
        return "Please don't train through pain. Rest today and see a physio or doctor if it stays.", session

    if "replace" in text or "swap" in text or "instead" in text:
        if len(names) >= 2:
            ok, answer, session = use_tool("replace_exercise", {"old": names[0], "new": names[1]}, session, athlete)
            return answer, session
        if len(names) == 1:
            ok, options, session = use_tool("find_alternatives", {"exercise": names[0]}, session, athlete)
            if not options:
                return "I couldn't find a safe swap for " + names[0] + ".", session
            return "You can swap " + names[0] + " for: " + options, session
        return "Which exercise do you want to swap?", session

    minutes = re.search(r"(\d+)\s*(min|minute)", text)
    if minutes:
        ok, answer, session = use_tool("set_session_length", {"minutes": int(minutes.group(1))}, session, athlete)
        return answer + ": " + ", ".join(session), session

    if "today" in text or "plan" in text or "workout" in text:
        return "Today's session: " + ", ".join(session), session

    if "why" in text and names:
        for e in EXERCISES:
            if e[0] == names[0]:
                return names[0] + " trains " + ", ".join(e[2]) + ", which " + athlete["sport"] + " needs.", session

    return ask_llm(message), session


# Placeholder for the language model
def ask_llm(message):
    return "I'm still learning! Try asking about today's plan, swapping an exercise, or saying how many minutes you have."
