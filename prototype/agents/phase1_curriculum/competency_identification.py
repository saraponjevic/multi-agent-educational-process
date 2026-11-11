"""
Agent za identifikaciju kompetencija.

STATUS: hello world (vraca izmisljene podatke).
Kasnije: zameni telo funkcije run() pravom logikom ili LLM pozivom
(uzor: agents/phase1_curriculum/learning_outcomes.py).
"""
from agents.common import hello


def run(data: dict) -> dict:
    return hello(data, "agent za identifikaciju kompetencija", competencies=['K1: razume osnovne pojmove', 'K2: primenjuje znanje u praksi'])
