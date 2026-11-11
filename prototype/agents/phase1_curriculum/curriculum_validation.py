"""
Agent za validaciju kurikuluma.

STATUS: pravi agent bez LLM-a - proverava kurikulum nad GRAFOM ZNANJA
pomocu SPARQL pravila iz knowledge/pravila/*.rq.

Kasnije: LLM moze dodatno da proceni smislenost ishoda, a graf ostaje
"tvrda" provera strukture.
"""
from agents.common import hello

RULES = ["ishod_bez_kompetencije", "ishod_bez_pokazatelja", "ishod_bez_jedinice", "ciklus_preduslova"]


def run(data: dict) -> dict:
    kg = data.get("kg")
    if kg is None:                                   # pokrenuto bez grafa (--no-kg)
        return hello(data, "agent za validaciju kurikuluma", valid=True, checked=[])
    violations = kg.check(RULES)
    for v in violations:
        print(f"      [validacija] {v['poruka']}")
    return hello(data, "agent za validaciju kurikuluma",
                 valid=not violations, checked=RULES, violations=violations)
