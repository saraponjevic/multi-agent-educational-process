"""
Agent za proveru kvaliteta materijala.

STATUS: pravi agent (bez LLM-a) - proverava materijale po PRAVILIMA:
  1. svaka lekcija ima sve delove prave lekcije (uvod, objasnjenje, reseni primer, ...),
  2. svaki nastavni ishod ima bar jedan zadatak,
  3. racunski / programski / analiza_greske zadaci imaju konkretne podatke,
  4. svaki zadatak ima resenje,
  5. agent za resavanje (exercise_solver) se slaze sa autorom zadatka.

Izlaz: {"ok": true/false, "issues": ["..."], "checked": {...}}
Primedbe (issues) optimizator salje u doradu agentima za lekcije i zadatke.
"""
from agents.phase2_content.lesson_generator import SECTION_TYPES

OPTIONAL_SECTIONS = {"kod"}          # tema ne mora imati kod (npr. istorija)


def run(data: dict) -> dict:
    inp = data["inputs"]
    lessons = (inp.get("lesson_generator") or {}).get("lessons", [])
    exercises = (inp.get("exercise_generator") or {}).get("exercises", [])
    solver = inp.get("exercise_solver") or {}
    outcomes = [o.get("id") for o in (data["inputs"].get("learning_outcomes") or {}).get("outcomes", [])]

    issues = []
    for les in lessons:
        have = {s.get("type") for s in les.get("sections", []) if isinstance(s, dict)}
        missing = [t for t in SECTION_TYPES if t not in have and t not in OPTIONAL_SECTIONS]
        if missing:
            issues.append(f"Lekcija {les.get('unit')} ('{les.get('title')}') nema delove: {', '.join(missing)}")

    covered = {e.get("outcome") for e in exercises}
    for o in outcomes:
        if o not in covered:
            issues.append(f"Ishod {o} nema nijedan zadatak")

    for e in exercises:
        if e.get("type") in ("racunski", "programski", "analiza_greske") and not str(e.get("data") or "").strip():
            issues.append(f"Zadatak {e.get('id')} ({e.get('type')}) nema konkretne podatke")
        if not str(e.get("solution") or "").strip():
            issues.append(f"Zadatak {e.get('id')} nema resenje")

    for zid in solver.get("mismatches", []):
        note = (solver.get("solutions", {}).get(zid) or {}).get("note", "")
        issues.append(f"Zadatak {zid}: resavac se ne slaze sa autorom ({note or 'proveriti racun'})")

    return {
        "ok": not issues,
        "issues": issues,
        "checked": {"lessons": len(lessons), "exercises": len(exercises), "outcomes": len(outcomes)},
        "message": "Materijali su u redu." if not issues else f"Pronadjeno {len(issues)} primedbi.",
    }
