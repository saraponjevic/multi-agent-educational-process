"""
Agent ucenik (Student Agent).                    *** KLJUCNI AGENT (LLM) ***

Jedna funkcija, vise instanci u config-u (razlikuju se po params):
  params.level: beginner | intermediate | advanced   -> koji profil ucenik "glumi"
  params.mode:  class  -> FAZA 3: odgovara na pitanje nastavnika na casu
                test   -> FAZA 4: radi test

VAZNO ZA SIMULACIJU:
  Jezicki model "zna sve", pa ce, ako ga ne ogranicimo, i pocetnik odgovarati kao ekspert.
  Zato:
    1. ucenik sme da koristi SAMO ono sto je nastavnik rekao na casu,
    2. svaki nivo ima KONKRETNA pravila ponasanja (LEVEL_RULES ispod).
Profil svakog nivoa (opis) nalazi se u config/course.yaml (student_profiles).
"""
from engine.llm import ask_json, to_text

LEVEL_RULES = {
    "beginner": (
        "- Odgovaras KRATKO: najvise 1-2 recenice po pitanju.\n"
        "- NE pises programski kod; najvise opises recima sta bi radio, nespretno.\n"
        "- Na bar POLOVINU pitanja odgovaras netacno ili samo delimicno tacno.\n"
        "- Mesas slicne pojmove (npr. klasifikaciju i regresiju, preciznost i tacnost).\n"
        "- Ne pamtis formule; ako se trazi formula, napises je pogresno ili kazes da se ne secas.\n"
        "- Ponekad napises 'ne znam' ili 'nisam siguran'."
    ),
    "intermediate": (
        "- Razumes osnovnu ideju i vecinu odgovora das delimicno ili potpuno tacno.\n"
        "- Gresis u DETALJIMA (npr. pomesas formulu za preciznost i odziv, ili zaboravis korak).\n"
        "- Kod mozes da napises, ali nepotpun ili sa sitnom greskom.\n"
        "- Na 1-2 pitanja das nepotpun ili pogresan odgovor."
    ),
    "advanced": (
        "- Odgovaras tacno, jasno i sa razumevanjem.\n"
        "- Mozes da napises ispravan kod i da navedes formule.\n"
        "- I dalje koristis samo ono sto je predavano, uz logicno zakljucivanje."
    ),
}

SYSTEM_TEMPLATE = (
    "Ti glumis UCENIKA u simulaciji nastave. Ti NISI asistent i NISI strucnjak.\n"
    "Profil ucenika: {profile}\n\n"
    "Pravila ponasanja za ovaj nivo:\n{rules}\n\n"
    "NAJVAZNIJE PRAVILO: znas SAMO ono sto je nastavnik rekao na casu (tekst ispod) "
    "i opste znanje koje ima ucenik sa ovim profilom. NE koristi svoje sopstveno znanje o temi. "
    "Ako nesto nije objasnjeno na casu, odgovori onako kako bi ovaj ucenik pogadjao - "
    "pocetnik ce verovatno pogresiti ili reci da ne zna."
)


def run(data: dict) -> dict:
    course = data["course"]
    level = data["params"].get("level", "beginner")
    mode = data["params"].get("mode", "class")
    profile = course.get("student_profiles", {}).get(level, level)
    system = SYSTEM_TEMPLATE.format(profile=profile, rules=LEVEL_RULES.get(level, ""))

    if mode == "test":
        return _take_test(data, system, level, course)
    return _attend_class(data, system, level, course)


def _attend_class(data, system, level, course):
    teacher = data["inputs"].get("teacher") or {}
    user = f"""Nastavnik je na casu rekao:
\"\"\"{teacher.get('explanation', '')}\"\"\"

Nastavnik pita: "{teacher.get('question', '')}"

Odgovori na pitanje kao ovaj ucenik, postujuci pravila za svoj nivo.
Ako ti nesto nije jasno, postavi i svoje pitanje nastavniku.
Pisi na jeziku: {course['language']}.
Vrati JSON: {{"answer": "...", "question_to_teacher": "... ili prazno"}}"""

    answers = {"beginner": "Nisam siguran...", "intermediate": "Mislim da je to...",
               "advanced": "To je precizno definisan pojam koji..."}
    fallback = {"answer": answers.get(level, "?"), "question_to_teacher": ""}
    return {"level": level, **ask_json(system, user, fallback)}


def _take_test(data, system, level, course):
    questions = (data["inputs"].get("test_generator") or {}).get("questions", [])
    teacher = data["inputs"].get("teacher") or {}
    user = f"""Ovo je SVE sto si cuo na casu (tvoje jedino znanje o temi):
\"\"\"{teacher.get('explanation', '')}\"\"\"

Sada radis test. Pitanja:
{to_text([{"id": q.get("id"), "text": q.get("text")} for q in questions])}

Odgovori na SVA pitanja kao ovaj ucenik, strogo postujuci pravila za svoj nivo.
Pisi na jeziku: {course['language']}.
Vrati JSON: {{"answers": [{{"question_id": "T1", "answer": "..."}}]}}"""

    fallback = {"answers": [{"question_id": q.get("id"), "answer": f"(hello world odgovor, nivo {level})"}
                            for q in questions]}
    return {"level": level, **ask_json(system, user, fallback)}
