"""
Agent za definisanje nastavnih ishoda.          *** KLJUCNI AGENT (LLM) ***

Ulaz:  tema kursa, kompetencije, predznanje
Izlaz: {"outcomes": [{"id": "O1", "text": "...", "level": "...", "indicator": "..."}]}

OVO JE UZOR kako izgleda "pravi" agent:
  1. iz `data` uzmes sta ti treba
  2. napises SYSTEM poruku (ko je agent) i USER poruku (sta tacno da uradi + format)
  3. pozoves ask_json(...) i das mu FALLBACK (hello world odgovor za mock rezim)
"""
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si strucnjak za dizajn kurikuluma i instrukcioni dizajn. "
    "Formulises MERLJIVE nastavne ishode koristeci aktivne glagole (Blumova taksonomija)."
)


def run(data: dict) -> dict:
    course = data["course"]
    competencies = (data["inputs"].get("competency_identification") or {}).get("competencies", [])
    prior = (data["inputs"].get("prior_knowledge_analysis") or {}).get("prerequisites", [])

    user = f"""Kurs: {course['topic']}
Ciljna grupa: {course['target_group']}
Broj nastavnih jedinica: {course['num_units']}
Zahtevi: {course.get('requirements', '')}
Kompetencije koje treba razviti: {to_text(competencies)}
Predznanje ucenika: {to_text(prior)}

Definisi 3 do 5 merljivih nastavnih ishoda. Pisi na jeziku: {course['language']}.
Vrati JSON u formatu:
{{"outcomes": [{{"id": "O1", "text": "Ucenik ce moci da ...", "level": "pamcenje|razumevanje|primena|analiza|sinteza|evaluacija", "indicator": "sta ucenik konkretno pokazuje/predaje"}}]}}"""

    fallback = {"outcomes": [
        {"id": "O1", "text": "Ucenik objasnjava osnovni pojam teme", "level": "razumevanje",
         "indicator": "daje definiciju i primer"},
        {"id": "O2", "text": "Ucenik primenjuje znanje na jednostavnom zadatku", "level": "primena",
         "indicator": "resava zadatak"},
    ]}
    return ask_json(SYSTEM, user, fallback)
