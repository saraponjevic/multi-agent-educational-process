"""Agent za generisanje zavrsnog izvestaja."""
from agents.common import hello


def run(data: dict) -> dict:
    fb = data["inputs"].get("feedback_manager") or {}
    grader = data["inputs"].get("answer_grader") or {}
    return hello(data, "agent za generisanje zavrsnog izvestaja",
                 summary=f"Prolaz {data['iteration'] + 1}: ocena kvaliteta {fb.get('score')}, "
                         f"prosek na testu {grader.get('average')}, potrebna dorada: {fb.get('needs_rework')}")
