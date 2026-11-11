"""
Agent za definisanje pokazatelja ostvarenosti ishoda.

STATUS: hello world (vraca izmisljene podatke).
Kasnije: zameni telo funkcije run() pravom logikom ili LLM pozivom
(uzor: agents/phase1_curriculum/learning_outcomes.py).
"""
from agents.common import hello


def run(data: dict) -> dict:
    return hello(data, "agent za definisanje pokazatelja ostvarenosti ishoda", indicators={'O1': 'ucenik daje definiciju i primer'})
