"""
Agent za resavanje zadataka.                     *** KLJUCNI AGENT (LLM) ***

Uloga: KONTROLA zadataka. Za svaki zadatak agent:
   1. SAM resi zadatak (na osnovu teksta i podataka),
   2. uporedi svoj konacan odgovor sa odgovorom autora (exercise_generator),
   3. javi da li se slazu; ako ne, objasni gde je razlika.
Zadatak za koji se resenja ne slazu je sumnjiv (greska u racunu ili nejasan tekst).

Izlaz: {"solutions": {"Z1": {"solution": "...", "answer": "...", "matches_author": true, "note": "..."}},
        "mismatches": ["Z3"]}
"""
from agents.common import course_context
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si pazljiv asistent koji proverava zadatke pre nego sto ih dobiju ucenici. "
    "Svaki zadatak prvo resis SAM, korak po korak, pa tek onda uporedis sa resenjem autora."
)


def run(data: dict) -> dict:
    course = data["course"]
    exercises = (data["inputs"].get("exercise_generator") or {}).get("exercises", [])
    tasks = [{"id": e.get("id"), "text": e.get("text"), "data": e.get("data", ""),
              "author_answer": e.get("answer", "")} for e in exercises]

    user = f"""Kurs: {course['topic']}
{course_context(course)}

Zadaci (polje author_answer je konacan odgovor autora zadatka):
{to_text(tasks)}

Za SVAKI zadatak:
1. resi ga sam, kratko i korak po korak (polje "solution"), i napisi svoj konacan odgovor ("answer"),
2. "matches_author": true ako se tvoj konacan odgovor slaze sa author_answer (ista vrednost/smisao), inace false,
3. "note": ako se ne slaze - gde je razlika (npr. greska u racunu autora, nejasan tekst zadatka); inace prazno.
Pisi na jeziku: {course['language']}.
Vrati JSON:
{{"solutions": {{"Z1": {{"solution": "...", "answer": "...", "matches_author": true, "note": ""}}}}}}"""

    fallback = {"solutions": {e.get("id"): {"solution": "(hello world resenje)", "answer": e.get("answer", ""),
                                            "matches_author": True, "note": ""} for e in exercises}}
    result = ask_json(SYSTEM, user, fallback)
    solutions = {k: v for k, v in (result.get("solutions") or {}).items() if isinstance(v, dict)}
    mismatches = [k for k, v in solutions.items() if v.get("matches_author") is False]
    return {"solutions": solutions, "mismatches": mismatches,
            "message": f"Provereno {len(solutions)} zadataka, neslaganja: {len(mismatches)}",
            "_source": result.get("_source")}
