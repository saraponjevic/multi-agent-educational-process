"""
Agent za upravljanje povratnom spregom.

Odlucuje da li treba dorada i KOJOJ fazi se tok vraca.
Orkestrator (engine/orchestrator.py) cita polja needs_rework i return_to.
"""
from agents.common import hello


def run(data: dict) -> dict:
    score = (data["inputs"].get("quality_evaluator") or {}).get("score", 100)
    threshold = data["settings"].get("quality_threshold", 75)
    needs_rework = score < threshold
    return hello(data, "agent za upravljanje povratnom spregom",
                 score=score, needs_rework=needs_rework,
                 return_to="content_creation" if needs_rework else None)
