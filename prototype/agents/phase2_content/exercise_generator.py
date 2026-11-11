"""
Agent za generisanje zadataka.                   *** KLJUCNI AGENT (LLM) ***

Ulaz:  ishodi, lekcije
Izlaz: {"exercises": [{"id": "Z1", "unit": 1, "difficulty": "lako|srednje|tesko", "text": "...", "outcome": "O1"}]}
"""
from engine.llm import ask_json, to_text

SYSTEM = "Ti si nastavnik koji pravi vezbe razlicitih nivoa tezine, povezane sa nastavnim ishodima."


def run(data: dict) -> dict:
    course = data["course"]
    outcomes = (data["inputs"].get("learning_outcomes") or {}).get("outcomes", [])
    lessons = (data["inputs"].get("lesson_generator") or {}).get("lessons", [])

    user = f"""Kurs: {course['topic']}
Nastavni ishodi:
{to_text(outcomes)}
Lekcije:
{to_text(lessons)}

Napravi 4 zadatka: bar jedan lak, jedan srednji i jedan tezak. Svaki zadatak vezi za jedan ishod.
Pisi na jeziku: {course['language']}.
Vrati JSON:
{{"exercises": [{{"id": "Z1", "unit": 1, "difficulty": "lako", "outcome": "O1", "text": "..."}}]}}"""

    fallback = {"exercises": [
        {"id": "Z1", "unit": 1, "difficulty": "lako", "outcome": "O1", "text": "(hello world zadatak 1)"},
        {"id": "Z2", "unit": 2, "difficulty": "srednje", "outcome": "O2", "text": "(hello world zadatak 2)"},
    ]}
    return ask_json(SYSTEM, user, fallback)
