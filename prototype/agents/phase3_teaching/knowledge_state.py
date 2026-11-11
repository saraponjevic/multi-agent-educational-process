"""
Agent za upravljanje stanjem znanja ucenika.

STATUS: PRIMITIVNO, bez LLM-a. Procena znanja zavisi samo od profila ucenika
(pocetnik 0.3, srednji 0.6, napredni 0.9). Ucenik "usvaja" teme redom kojim su
predavane, onoliko njih koliko mu procena dozvoljava.

Ucenike i teme cita iz GRAFA, a stanje znanja upisuje nazad u graf:
    :Ucenik_beginner :nivoZnanja 0.3 ; :usvojioTemu :Tema_osnovni_pojmovi .

Kasnije: procena na osnovu odgovora na casu (LLM) i rezultata testa.
"""
from agents import graph_context
from agents.common import hello

ESTIMATE = {"beginner": 0.3, "intermediate": 0.6, "advanced": 0.9}


def run(data: dict) -> dict:
    kg = data.get("kg")
    if kg is None:
        return hello(data, "agent za upravljanje stanjem znanja ucenika", knowledge=ESTIMATE)

    topics = graph_context.topics(kg)
    students = kg.query("SELECT ?u ?profil WHERE { ?u a :Ucenik ; :profil ?profil }")
    state = {}
    for s in students:
        level = ESTIMATE.get(s["profil"], 0.5)
        mastered = topics[: round(level * len(topics))]
        state[s["profil"]] = {"estimate": level, "mastered_topics": [t["name"] for t in mastered]}
    return hello(data, "agent za upravljanje stanjem znanja ucenika", knowledge=state)


def write_graph(result: dict, g):
    for profil, st in result.get("knowledge", {}).items():
        if not isinstance(st, dict):
            continue
        u = g.ref(f"Ucenik_{profil}")
        g.value(u, "nivoZnanja", st["estimate"])
        for name in st["mastered_topics"]:
            g.link(u, "usvojioTemu", g.ref(f"Tema_{name}"))
