"""
Agent za upravljanje stanjem znanja ucenika.

STATUS: pravi agent (bez LLM-a). Vise NE nagadja znanje po profilu, nego cita
STVARNO stanje iz memorije ucenika posle casa (izlaz aktivnosti 'learning'):

    nivo znanja   = usvojeni delovi / svi delovi koje je cuo
    usvojena tema = iz te jedinice je usvojio bar polovinu delova

Upis u graf:
    :Ucenik_student_beginner :nivoZnanja 0.5 ; :usvojioTemu :Tema_osnovni_pojmovi .
"""
from agents import graph_context


def run(data: dict) -> dict:
    learning = data["inputs"].get("learning") or {}
    segments = (data["inputs"].get("teacher") or {}).get("segments", [])
    kg = data.get("kg")
    topics = graph_context.topics(kg) if kg else []

    units = {}
    for s in segments:
        units.setdefault(s.get("unit"), []).append(s.get("id"))

    state = {}
    for sid, st in (learning.get("participants") or {}).items():
        if not st:
            continue
        learned = set(st.get("learned_ids", []))
        mastered_units = [u for u, ids in units.items() if ids and len(learned & set(ids)) / len(ids) >= 0.5]
        state[sid] = {
            "estimate": st.get("ratio", 0.0),
            "learned": st.get("learned", 0),
            "heard": st.get("heard", 0),
            "mastered_units": mastered_units,
            "mastered_topics": [t["name"] for t in topics if t["unit"] in mastered_units],
            "learned_concepts": st.get("learned_concepts", []),
            "missed_concepts": st.get("missed_concepts", []),
        }
    return {"knowledge": state,
            "message": "Stanje znanja procitano iz memorije simuliranih ucenika."}


def write_graph(result: dict, g):
    for sid, st in result.get("knowledge", {}).items():
        if not isinstance(st, dict):
            continue
        u = g.ref(f"Ucenik_{sid}")
        g.value(u, "nivoZnanja", st["estimate"])
        for name in st["mastered_topics"]:
            g.link(u, "usvojioTemu", g.ref(f"Tema_{name}"))
