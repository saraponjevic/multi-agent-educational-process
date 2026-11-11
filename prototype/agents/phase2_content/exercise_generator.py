"""
Agent za generisanje zadataka.                   *** KLJUCNI AGENT (LLM) ***

Ulaz:  ishodi, lekcije
Izlaz: {"exercises": [{"id": "Z1", "unit": 1, "difficulty": "lako|srednje|tesko", "text": "...", "outcome": "O1"}]}
"""
from agents import graph_context
from engine.llm import ask_json, to_text

SYSTEM = "Ti si nastavnik koji pravi vezbe razlicitih nivoa tezine, povezane sa nastavnim ishodima."


def run(data: dict) -> dict:
    course = data["course"]
    kg = data.get("kg")
    if kg:   # struktura iz grafa: ishodi + lekcije sa temama i ishodima svoje jedinice
        outcomes, lessons = graph_context.outcomes(kg), graph_context.lessons(kg)
    else:
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

def write_graph(result: dict, g):
    """GRAF:  :Zadatak_Z1 a :Zadatak ; :zaJedinicu :Jedinica_1 ; :podrzavaIshod :Ishod_O1 ."""
    for ex in result.get("exercises", []):
        z = g.node("Zadatak", f"Zadatak_{ex['id']}", label=ex.get("text"))
        g.value(z, "tezina", ex.get("difficulty"))
        if ex.get("unit") is not None:
            g.link(z, "zaJedinicu", g.ref(f"Jedinica_{ex['unit']}"))
        if ex.get("outcome"):
            g.link(z, "podrzavaIshod", g.ref(f"Ishod_{ex['outcome']}"))
