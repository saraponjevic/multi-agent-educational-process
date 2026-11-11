"""
Agent za upravljanje povratnom spregom.

Odlucuje da li treba dorada i KOJOJ fazi se tok vraca.
Orkestrator (engine/orchestrator.py) cita polja needs_rework i return_to.

Dva razloga za doradu:
  1. ocena kvaliteta je ispod praga (quality_evaluator)
  2. graf znanja ima prekrsena pravila (curriculum_evaluation) -> vraca se na
     NAJRANIJU fazu u kojoj je odgovoran agent (npr. ishod bez pitanja -> faza evaluacije,
     jedinica bez lekcije -> faza sadrzaja)
"""
from agents.common import hello


def run(data: dict) -> dict:
    score = (data["inputs"].get("quality_evaluator") or {}).get("score", 100)
    threshold = data["settings"].get("quality_threshold", 75)
    violations = (data["inputs"].get("curriculum_evaluation") or {}).get("violations", [])

    order = data["settings"].get("phase_order") or ["curriculum_design", "content_creation", "teaching", "evaluation"]
    phases_with_problems = [v.get("faza") for v in violations if v.get("faza") in order]

    if phases_with_problems:
        return_to = min(phases_with_problems, key=order.index)
        reason = f"graf znanja: {len(violations)} prekrsenih pravila"
    elif score < threshold:
        return_to = "content_creation"
        reason = f"ocena kvaliteta {score} < {threshold}"
    else:
        return_to, reason = None, "sve u redu"

    return hello(data, "agent za upravljanje povratnom spregom",
                 score=score, needs_rework=return_to is not None, return_to=return_to, reason=reason)
