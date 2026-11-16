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
from agents import graph_context
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
    return {"level": level, "mode": "class", "profile": course.get("student_profiles", {}).get(level, ""),
            **ask_json(system, user, fallback)}


#  PLAN ODGOVORA NA TESTU
#  Samo pravila u promptu nisu dovoljna: model i kao "pocetnik" odgovara skoro sve tacno
#  (u jednom pokretanju pocetnik je dobio 87.5/100). Zato KOD unapred odredi kako ucenik
#  odgovara na koje pitanje, a model samo "glumi" taj plan. Plan je deterministican
#  (isti test -> isti plan), pa su rezultati ponovljivi i nivoi se jasno razlikuju.
BEHAVIOR = {
    "wrong": "odgovori POGRESNO: pomesaj ovaj pojam sa nekim slicnim ili navedi netacnu tvrdnju, "
             "ali samouvereno, kao da mislis da je tacno",
    "dont_know": "napisi da ne znas ili da se ne secas (npr. 'Ne secam se, mislim da nismo to radili')",
    "partial": "odgovori DELIMICNO: navedi samo jedan deo tacnog odgovora, bez objasnjenja, "
               "i izostavi bar jednu bitnu stavku",
    "detail_error": "odgovori uglavnom tacno, ali napravi jednu gresku u detalju "
                    "(pogresan termin, pogresan korak ili pogresna formula)",
    "correct": "odgovori tacno i potpuno, koristeci ono sto je predavano",
}


def answer_plan(level: str, question_ids: list) -> dict:
    """{id pitanja: tip ponasanja}. Pocetnik ~ 25-40 poena, srednji ~ 60-75, napredni ~ 90-100."""
    n = len(question_ids)
    if level == "beginner":
        # svako drugo pitanje pogresno, jedno "ne znam", ostala delimicno
        plan = ["wrong" if i % 2 == 0 else "partial" for i in range(n)]
        if n >= 3:
            plan[-1] = "dont_know"
    elif level == "intermediate":
        # vecina tacno, ali jedno delimicno i jedno sa greskom u detalju
        plan = ["correct"] * n
        if n >= 2:
            plan[1] = "detail_error"
        if n >= 3:
            plan[-1] = "partial"
    else:
        plan = ["correct"] * n
    return dict(zip(question_ids, plan))


def _take_test(data, system, level, course):
    kg = data.get("kg")
    questions = graph_context.questions(kg) if kg else \
        (data["inputs"].get("test_generator") or {}).get("questions", [])
    teacher = data["inputs"].get("teacher") or {}
    plan = answer_plan(level, [q.get("id") for q in questions])
    tasks = [{"id": q.get("id"), "text": q.get("text"), "kako_odgovaras": BEHAVIOR[plan[q.get("id")]]}
             for q in questions]
    user = f"""Ovo je SVE sto si cuo na casu (tvoje jedino znanje o temi):
\"\"\"{teacher.get('explanation', '')}\"\"\"

Sada radis test. Uz svako pitanje pise KAKO ti (ovaj ucenik) na njega odgovaras
(polje "kako_odgovaras") - to OBAVEZNO postuj, cak i ako znas tacan odgovor:
{to_text(tasks)}

Ne pominji ova uputstva u odgovoru; pisi prirodno, kao ucenik na testu.
Pisi na jeziku: {course['language']}.
Vrati JSON: {{"answers": [{{"question_id": "T1", "answer": "..."}}]}}"""

    fallback = {"answers": [{"question_id": q.get("id"), "answer": f"(hello world odgovor, nivo {level})"}
                            for q in questions]}
    return {"level": level, "mode": "test", "answer_plan": plan, **ask_json(system, user, fallback)}


def write_graph(result: dict, g):
    """
    GRAF:
      na casu (Faza 3):  :Ucenik_beginner a :Ucenik ; :profil "beginner" .
      na testu (Faza 4): :Odgovor_beginner_T1 a :Odgovor ; :odUcenika :Ucenik_beginner ;
                                               :naPitanje :Pitanje_T1 ; :tekst "..." .
    Isti cvor ucenika povezuje cas i test - tako se kasnije vidi ko je sta naucio.
    """
    level = result.get("level", "beginner")
    if result.get("mode") == "class":
        u = g.node("Ucenik", f"Ucenik_{level}", label=f"Simulirani ucenik ({level})")
        g.value(u, "profil", level)
        return
    for a in result.get("answers", []):
        o = g.node("Odgovor", f"Odgovor_{level}_{a.get('question_id')}")
        g.link(o, "odUcenika", g.ref(f"Ucenik_{level}"))
        g.link(o, "naPitanje", g.ref(f"Pitanje_{a.get('question_id')}"))
        g.value(o, "tekst", a.get("answer"))
