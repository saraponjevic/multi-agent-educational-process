"""
Agent za definisanje pokazatelja ostvarenosti ishoda.

STATUS: jednostavna logika bez LLM-a - preuzima "indicator" koji je predlozio
agent za ishode. Kasnije: LLM koji pravi preciznije, merljive pokazatelje.

Graf: dopunjuje TUDJE cvorove (ishode) svojstvom :pokazatelj.
To mu je dozvoljeno u knowledge/agenti.ttl  (:dopunjuje :pokazatelj).
"""
from agents.common import hello


def run(data: dict) -> dict:
    outcomes = (data["inputs"].get("learning_outcomes") or {}).get("outcomes", [])
    indicators = {o["id"]: o.get("indicator") or f"ucenik pokazuje: {o.get('text', '')}" for o in outcomes}
    return hello(data, "agent za definisanje pokazatelja ostvarenosti ishoda", indicators=indicators)


def write_graph(result: dict, g):
    """GRAF:  :Ishod_O1 :pokazatelj "..." ."""
    for outcome_id, text in result.get("indicators", {}).items():
        g.value(g.ref(f"Ishod_{outcome_id}"), "pokazatelj", text)
