"""
Agent za evaluaciju kvaliteta (Evaluator Agent).

Pravilo (za sada jednostavno, bez LLM-a):
  - ako je ocenjivanje radio pravi LLM -> ocena kvaliteta = prosek ucenika na testu
  - u mock rezimu -> demo ocena: prvi prolaz 60 (losa), posle dorade 90 (dobra),
    da bi se videlo da povratna sprega radi.
"""
from agents.common import hello


def run(data: dict) -> dict:
    grader = data["inputs"].get("answer_grader") or {}
    if str(grader.get("_source", "")).startswith("llm") and grader.get("average") is not None:
        score, basis = grader["average"], "prosek ucenika na testu"
    else:
        score, basis = (60 if data["iteration"] == 0 else 90), "demo ocena (mock rezim)"
    return hello(data, "agent za evaluaciju kvaliteta (Evaluator)", score=score, basis=basis)
