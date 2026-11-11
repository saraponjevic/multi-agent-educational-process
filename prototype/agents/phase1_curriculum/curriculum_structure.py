"""
Agent za strukturiranje nastavnog plana.         *** KLJUCNI AGENT (LLM) ***

Ulaz:  nastavni ishodi
Izlaz: {"units": [{"unit": 1, "title": "...", "topics": [...], "outcomes": ["O1"]}]}
"""
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si strucnjak za planiranje nastave. Organizujes nastavne jedinice logicnim redosledom "
    "(od jednostavnijeg ka slozenijem) tako da svaka jedinica pokriva odredjene nastavne ishode."
)


def run(data: dict) -> dict:
    course = data["course"]
    outcomes = (data["inputs"].get("learning_outcomes") or {}).get("outcomes", [])

    user = f"""Kurs: {course['topic']}
Broj nastavnih jedinica: {course['num_units']}
Nastavni ishodi:
{to_text(outcomes)}

Napravi nastavni plan sa tacno {course['num_units']} jedinica. Svaki ishod mora biti pokriven bar jednom jedinicom.
Pisi na jeziku: {course['language']}.
Vrati JSON:
{{"units": [{{"unit": 1, "title": "...", "topics": ["...", "..."], "outcomes": ["O1"]}}]}}"""

    fallback = {"units": [
        {"unit": 1, "title": "Uvod", "topics": ["osnovni pojmovi"], "outcomes": ["O1"]},
        {"unit": 2, "title": "Prakticna primena", "topics": ["jednostavan primer"], "outcomes": ["O2"]},
    ]}
    return ask_json(SYSTEM, user, fallback)
