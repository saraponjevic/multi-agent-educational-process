"""
Agent za ocenjivanje odgovora.                   *** KLJUCNI AGENT (LLM) ***

Ulaz:  pitanja sa ocekivanim odgovorima + odgovori svih ucenika na testu
Ulaz dolazi od AKTIVNOSTI 'test_taking' (ucenici rade test), ne od posebnih agenata.
Izlaz: {"grades": {"student_beginner": {"score": 0-100, "comment": "...", "points": [...]}},
        "average": 0-100}

Kako ocenjuje (da bi bilo objektivno):
  1. ucenici su ANONIMNI za ocenjivaca (S1, S2, S3) - ne zna ko je pocetnik a ko napredni,
  2. svako pitanje se boduje 0 / 1 / 2 poena prema ocekivanom odgovoru,
  3. konacnu ocenu (0-100) racuna KOD, a ne model.

Napomena: ovaj agent moze da radi i kao EKSTERNI (external_agent/server.py),
samo promenis  type: local -> type: remote_http  u config/agents.yaml.
"""
from agents import graph_context
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si strog i objektivan ispitivac. Boduj svaki odgovor ISKLJUCIVO u odnosu na ocekivani odgovor:\n"
    "  2 poena = tacan i potpun odgovor (sve kljucne stavke iz ocekivanog odgovora)\n"
    "  1 poen  = delimicno tacan ili nepotpun odgovor\n"
    "  0 poena = netacan, nejasan, 'ne znam' ili bez odgovora\n"
    "Ne nagradjuj opsirnost, samouverenost ni dodatne informacije - samo tacnost i potpunost."
)

MAX_POINTS = 2


def run(data: dict) -> dict:
    course = data["course"]
    kg = data.get("kg")
    if kg:   # pitanja, ocekivani odgovori i odgovori ucenika - sve iz grafa
        questions, students = graph_context.questions(kg), graph_context.test_answers(kg)
    else:
        questions = (data["inputs"].get("test_generator") or {}).get("questions", [])
        # izlaz aktivnosti 'test_taking': {"participants": {id ucenika: {"answers": [...]}}}
        taking = data["inputs"].get("test_taking") or {}
        students = {sid: (out or {}).get("answers", []) for sid, out in (taking.get("participants") or {}).items()}

    # anonimizacija: student_beginner -> S1 ...
    anon = {f"S{i + 1}": sid for i, sid in enumerate(sorted(students))}
    anon_answers = {aid: students[sid] for aid, sid in anon.items()}

    user = f"""Kurs: {course['topic']}
Pitanja i ocekivani odgovori:
{to_text(questions)}

Odgovori ucenika (S1, S2, ... su anonimne oznake):
{to_text(anon_answers)}

Za SVAKOG ucenika i SVAKO pitanje dodeli 0, 1 ili 2 poena i kratko obrazlozenje.
Dodaj i jednu recenicu opsteg komentara po uceniku. Pisi na jeziku: {course['language']}.
Vrati JSON:
{{"grades": {{"S1": {{"points": [{{"question_id": "T1", "points": 0, "reason": "..."}}], "comment": "..."}}}}}}"""

    fallback = {"grades": {
        aid: {"points": [{"question_id": a.get("question_id"), "points": mock_points(a.get("answer", "")),
                          "reason": "(mock ocena po oznaci u odgovoru)"} for a in anon_answers[aid]],
              "comment": "(hello world)"}
        for aid in anon
    }}
    result = ask_json(SYSTEM, user, fallback)

    # vracamo prava imena ucenika i racunamo ocenu 0-100 u kodu
    grades = {}
    for aid, g in (result.get("grades") or {}).items():
        sid = anon.get(aid, aid)
        points = g.get("points", []) if isinstance(g, dict) else []
        total = sum(min(MAX_POINTS, max(0, int(p.get("points", 0)))) for p in points if isinstance(p, dict))
        max_total = MAX_POINTS * max(len(questions), 1)
        grades[sid] = {"score": round(100 * total / max_total, 1),
                       "comment": g.get("comment", "") if isinstance(g, dict) else "",
                       "points": points}

    scores = [g["score"] for g in grades.values()]
    return {
        "grades": grades,
        "average": round(sum(scores) / len(scores), 1) if scores else None,
        "_source": result.get("_source"),
    }

def mock_points(answer: str) -> int:
    """Mock rezim: mock ucenik oznaci odgovor sa (tacno)/(delimicno)/(netacno) - vidi simple_student.py."""
    a = str(answer).lower()
    return 2 if a.startswith("(tacno)") else 1 if a.startswith("(delimicno)") else 0


def write_graph(result: dict, g):
    """GRAF: dopunjuje odgovore ucenika poenima:  :Odgovor_beginner_T1 :poeni 1 ; :obrazlozenje "..." ."""
    for sid, grade in result.get("grades", {}).items():
        for p in grade.get("points", []):
            if not isinstance(p, dict):
                continue
            o = g.ref(f"Odgovor_{sid}_{p.get('question_id')}")
            g.value(o, "poeni", min(2, max(0, int(p.get("points", 0)))))
            g.value(o, "obrazlozenje", p.get("reason"))
