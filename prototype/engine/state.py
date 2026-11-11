"""
ZAJEDNIČKO STANJE (State) koje putuje kroz LangGraph graf.

Svaki agent upisuje svoj rezultat u  results[<id agenta>].
Pošto neki agenti rade paralelno, koristimo "reducer" (merge_dicts)
koji spaja izmene umesto da jedna pregazi drugu.
"""
from typing import Annotated, TypedDict


def merge_dicts(old: dict, new: dict) -> dict:
    """Spaja dva rečnika. Koristi se kada više agenata istovremeno upisuje rezultate."""
    merged = dict(old or {})
    merged.update(new or {})
    return merged


class EducationState(TypedDict, total=False):
    course: dict                                   # ulaz korisnika: tema, ciljna grupa...
    settings: dict                                 # podešavanja iz config fajla
    iteration: int                                 # koliko puta je evaluacija vratila tok nazad
    current_phase: str                             # u kojoj smo fazi
    results: Annotated[dict, merge_dicts]          # izlazi svih agenata: {agent_id: {...}}
    log: Annotated[dict, merge_dicts]              # evidencija izvršavanja (vreme, status, greške)
    abort: Annotated[dict, merge_dicts]            # ako nije prazno: rad je prekinut zbog greške {agent: greska}
