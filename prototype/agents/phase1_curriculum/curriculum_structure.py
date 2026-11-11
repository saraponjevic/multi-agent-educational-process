"""
Agent za strukturiranje nastavnog plana.         *** KLJUCNI AGENT (LLM) ***

Ulaz:  nastavni ishodi
Izlaz: {"units": [{"unit": 1, "title": "...", "topics": [...], "outcomes": ["O1"]}]}
"""
from agents import graph_context
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si strucnjak za planiranje nastave. Organizujes nastavne jedinice logicnim redosledom "
    "(od jednostavnijeg ka slozenijem) tako da svaka jedinica pokriva odredjene nastavne ishode."
)


def run(data: dict) -> dict:
    course = data["course"]
    kg = data.get("kg")
    # ishode cita iz GRAFA (sa kompetencijama i pokazateljima), ne kao tekst od agenta za ishode
    outcomes = graph_context.outcomes(kg) if kg else \
        (data["inputs"].get("learning_outcomes") or {}).get("outcomes", [])

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

def write_graph(result: dict, g):
    """
    GRAF:
        :Kurs  :imaJedinicu  :Jedinica_1 .
        :Jedinica_1 :sadrziTemu :Tema_... ; :pokrivaIshod :Ishod_O1 .
        :Tema_2 :imaPreduslov :Tema_1 .
    PRIMITIVNO: preduslov = prethodna tema u planu (plan ide od jednostavnijeg ka slozenijem).
    Kasnije: model da eksplicitno navede preduslove.
    """
    previous_topic = None
    for u in result.get("units", []):
        j = g.node("NastavnaJedinica", f"Jedinica_{u['unit']}", label=u.get("title"))
        g.value(j, "redniBroj", int(u["unit"]))
        g.link(g.course, "imaJedinicu", j)
        for name in u.get("topics", []):
            t = g.node("Tema", f"Tema_{name}", label=name)
            g.link(j, "sadrziTemu", t)
            if previous_topic is not None and previous_topic != t:
                g.link(t, "imaPreduslov", previous_topic)
            previous_topic = t
        for outcome_id in u.get("outcomes", []):
            g.link(j, "pokrivaIshod", g.ref(f"Ishod_{outcome_id}"))
