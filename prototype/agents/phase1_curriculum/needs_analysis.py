"""
Agent za analizu obrazovnih potreba.

STATUS: hello world (vraca izmisljene podatke).
Kasnije: zameni telo funkcije run() pravom logikom ili LLM pozivom
(uzor: agents/phase1_curriculum/learning_outcomes.py).
"""
from agents.common import hello


def run(data: dict) -> dict:
    return hello(data, "agent za analizu obrazovnih potreba", needs=['razumevanje osnovnih pojmova', 'prakticna primena'])
