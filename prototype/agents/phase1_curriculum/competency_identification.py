"""
Agent za identifikaciju kompetencija.

STATUS: hello world (vraca izmisljene podatke).
Kasnije: zameni telo funkcije run() pravom logikom ili LLM pozivom
(uzor: agents/phase1_curriculum/learning_outcomes.py).
"""
from agents.common import hello


def run(data: dict) -> dict:
    return hello(data, "agent za identifikaciju kompetencija", competencies=['K1: razume osnovne pojmove', 'K2: primenjuje znanje u praksi'])

def write_graph(result: dict, g):
    """GRAF: Kurs --imaKompetenciju--> Kompetencija   (format 'K1: opis')."""
    for i, comp in enumerate(result.get("competencies", []), start=1):
        text = comp if isinstance(comp, str) else comp.get("text", "")
        cid, _, label = text.partition(":") if ":" in text else (f"K{i}", "", text)
        k = g.node("Kompetencija", f"Komp_{cid.strip()}", label=label.strip() or text)
        g.link(g.course, "imaKompetenciju", k)
