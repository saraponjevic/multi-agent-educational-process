"""
Agent za evaluaciju celokupnog kurikuluma.

STATUS: pravi agent bez LLM-a - pokrece SVA pravila iz knowledge/pravila/*.rq
nad grafom znanja i za svaki problem kaze KOJI AGENT je odgovoran i u KOJOJ FAZI je.
To koristi agent za povratnu spregu da zna gde da vrati tok.
"""
from agents.common import hello


def run(data: dict) -> dict:
    kg = data.get("kg")
    if kg is None:
        return hello(data, "agent za evaluaciju celokupnog kurikuluma", aligned=True, violations=[])
    violations = kg.check()                          # sva pravila
    for v in violations:
        v["faza"] = kg.phase_of(v["odgovoran"])
        print(f"      [evaluacija] {v['poruka']}  -> {v['odgovoran']} ({v['faza']})")
    return hello(data, "agent za evaluaciju celokupnog kurikuluma",
                 aligned=not violations, violations=violations)
