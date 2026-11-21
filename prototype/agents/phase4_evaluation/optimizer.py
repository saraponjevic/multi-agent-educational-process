"""
Agent za optimizaciju (Optimizer Agent).

Za sada: ako je ocena ispod praga, skuplja komentare ocenjivaca za slabije ucenike
i pretvara ih u predloge korekcija. Uvek dodaje i primedbe provere materijala
(material_quality_check). Te korekcije u doradi citaju agenti za lekcije i zadatke.
"""
from agents.common import hello


def run(data: dict) -> dict:
    score = (data["inputs"].get("quality_evaluator") or {}).get("score", 100)
    threshold = data["settings"].get("quality_threshold", 75)
    grades = (data["inputs"].get("answer_grader") or {}).get("grades", {})

    corrections = []
    if score < threshold:
        corrections = [f"{sid}: {g.get('comment')}" for sid, g in grades.items()
                       if isinstance(g, dict) and g.get("score", 100) < threshold]
        corrections.append("Pojednostaviti objasnjenja i dodati vise konkretnih primera za slabije ucenike.")
    corrections += (data["inputs"].get("material_quality_check") or {}).get("issues", [])
    return hello(data, "agent za optimizaciju (Optimizer)", corrections=corrections)
