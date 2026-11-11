"""
Agent za generisanje testova.                    *** KLJUCNI AGENT (LLM) ***

Ulaz:  nastavni ishodi, nastavni plan, LEKCIJE
Izlaz: {"questions": [{"id": "T1", "outcome": "O1", "text": "...", "expected_answer": "..."}]}

Konstruktivno uskladjivanje: pitanja i ocekivani odgovori moraju se zasnivati
ISKLJUCIVO na onome sto je predavano u lekcijama (inace test kaznjava ucenike
za gradivo koje nisu ni ucili).
"""
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si strucnjak za proveru znanja. Pravis pitanja koja direktno proveravaju nastavne ishode "
    "(konstruktivno uskladjivanje: svako pitanje mora imati vezu sa ishodom). "
    "Pitanja i ocekivani odgovori se zasnivaju ISKLJUCIVO na sadrzaju lekcija koje su predavane."
)


def run(data: dict) -> dict:
    course = data["course"]
    outcomes = (data["inputs"].get("learning_outcomes") or {}).get("outcomes", [])
    units = (data["inputs"].get("curriculum_structure") or {}).get("units", [])
    lessons = (data["inputs"].get("lesson_generator") or {}).get("lessons", [])

    user = f"""Kurs: {course['topic']}
Nastavni ishodi:
{to_text(outcomes)}
Nastavni plan:
{to_text(units)}
Lekcije koje su ucenici slusali (jedini izvor gradiva):
{to_text(lessons)}

Napravi test sa jednim pitanjem otvorenog tipa za SVAKI ishod (kratak odgovor, 1-3 recenice).
Za svako pitanje navedi ocekivani tacan odgovor koji se zasniva SAMO na lekcijama iznad
(isti pojmovi, iste formule, isti nacin implementacije - ne uvodi biblioteke ili metode koje nisu predavane).
Pisi na jeziku: {course['language']}.
Vrati JSON:
{{"questions": [{{"id": "T1", "outcome": "O1", "text": "...", "expected_answer": "..."}}]}}"""

    fallback = {"questions": [
        {"id": f"T{i+1}", "outcome": o.get("id"), "text": f"(hello world pitanje za {o.get('id')})",
         "expected_answer": "(ocekivani odgovor)"}
        for i, o in enumerate(outcomes)
    ]}
    return ask_json(SYSTEM, user, fallback)