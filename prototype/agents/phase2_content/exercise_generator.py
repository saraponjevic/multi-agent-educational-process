"""
Agent za generisanje zadataka.                   *** KLJUCNI AGENT (LLM) ***

Ulaz:  ishodi, lekcije, studija slucaja i ogranicenja (course.yaml)
Izlaz: {"exercises": [{"id": "Z1", "unit": 1, "outcome": "O1", "difficulty": "lako|srednje|tesko",
                       "type": "pojmovni|racunski|programski|analiza_greske",
                       "text": "...", "data": "tabela / kod / brojevi (ili prazno)",
                       "solution": "resenje korak po korak", "answer": "kratak konacan odgovor"}]}

ZADACI KAO PRAVI ZADACI:
  - razlicite VRSTE zadataka (TASK_TYPES), ne samo "objasni pojam",
  - KONKRETNI PODACI iz studije slucaja (mala tabela, brojevi koji se racunaju rucno, kod),
  - uz svaki zadatak ide RESENJE korak po korak i kratak konacan odgovor
    (agent exercise_solver ih posle nezavisno proverava).
"""
from agents import graph_context
from agents.common import course_context, lessons_brief
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si nastavnik koji pravi vezbe razlicitih vrsta i nivoa tezine, povezane sa nastavnim ishodima. "
    "Zadaci su konkretni: imaju podatke, jasan zahtev i jedno tacno resenje."
)

TASK_TYPES = {
    "pojmovni": "objasni / uporedi pojmove na primeru iz studije slucaja",
    "racunski": "izracunaj nesto rucno na maloj tabeli ili brojevima (npr. metrika, predikcija)",
    "programski": "napisi ili dopuni kratak kod",
    "analiza_greske": "dat je pogresan postupak ili kod - pronadji i ispravi gresku",
}


def run(data: dict) -> dict:
    course = data["course"]
    kg = data.get("kg")
    if kg:   # struktura iz grafa: ishodi + lekcije sa temama i ishodima svoje jedinice
        outcomes, lessons = graph_context.outcomes(kg), graph_context.lessons(kg)
    else:
        outcomes = (data["inputs"].get("learning_outcomes") or {}).get("outcomes", [])
        lessons = (data["inputs"].get("lesson_generator") or {}).get("lessons", [])

    types = "\n".join(f"  - {k}: {v}" for k, v in TASK_TYPES.items())
    corrections = (data["inputs"].get("optimizer") or {}).get("corrections", [])
    rework_note = ""
    if data["iteration"] > 0 and corrections:
        rework_note = f"\nOVO JE DORADA. Uvazi sledece primedbe evaluacije:\n{to_text(corrections)}\n"
    user = f"""Kurs: {course['topic']}{rework_note}
Nastavni ishodi:
{to_text(outcomes)}
Lekcije - bitni delovi (zadaci se oslanjaju SAMO na ovo gradivo):
{to_text(lessons_brief(lessons, (data["inputs"].get("lesson_generator") or {}).get("lessons")))}

{course_context(course)}

Napravi 4 do 6 zadataka:
- bar jedan lak, jedan srednji i jedan tezak; svaki ishod pokriven bar jednim zadatkom,
- koristi bar 3 razlicite vrste zadataka:
{types}
- polje "data" sadrzi konkretne podatke (markdown tabela, brojevi ili kod); prazno samo za pojmovni zadatak,
- polje "solution" je resenje KORAK PO KORAK, "answer" je kratak konacan odgovor (broj, rec ili jedna recenica).
Proveri da je racun u resenju tacan.
Pisi na jeziku: {course['language']}.
Vrati JSON:
{{"exercises": [{{"id": "Z1", "unit": 1, "outcome": "O1", "difficulty": "lako", "type": "racunski",
  "text": "...", "data": "...", "solution": "...", "answer": "..."}}]}}"""

    fallback = {"exercises": [
        {"id": "Z1", "unit": 1, "outcome": "O1", "difficulty": "lako", "type": "pojmovni",
         "text": "(hello world zadatak 1)", "data": "", "solution": "(resenje 1)", "answer": "(odgovor 1)"},
        {"id": "Z2", "unit": 2, "outcome": "O2", "difficulty": "srednje", "type": "racunski",
         "text": "(hello world zadatak 2)", "data": "| x | y |\n|---|---|\n| 1 | 2 |",
         "solution": "(resenje 2)", "answer": "(odgovor 2)"},
    ]}
    return ask_json(SYSTEM, user, fallback)


def write_graph(result: dict, g):
    """GRAF:  :Zadatak_Z1 a :Zadatak ; :zaJedinicu :Jedinica_1 ; :podrzavaIshod :Ishod_O1 ."""
    for ex in result.get("exercises", []):
        z = g.node("Zadatak", f"Zadatak_{ex['id']}", label=ex.get("text"))
        g.value(z, "tezina", ex.get("difficulty"))
        if ex.get("unit") is not None:
            g.link(z, "zaJedinicu", g.ref(f"Jedinica_{ex['unit']}"))
        if ex.get("outcome"):
            g.link(z, "podrzavaIshod", g.ref(f"Ishod_{ex['outcome']}"))
