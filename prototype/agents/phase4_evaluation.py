"""FAZA 4 - Evaluacija i unapredjenje  (10 "hello world" agenata)."""
from agents.common import hello


def test_generator(data):                     # 1
    outcomes = data["inputs"]["learning_outcomes"]["outcomes"]
    return hello(data, "agent za generisanje testova",
                 questions=[{"outcome": o["id"], "q": f"Pitanje za {o['id']}"} for o in outcomes])


def answer_grader(data):                      # 2  (lokalna verzija; eksterna je u external_agent/)
    return hello(data, "agent za ocenjivanje odgovora (lokalni)",
                 grades={"student_beginner": 5, "student_intermediate": 7, "student_advanced": 9})


def error_analysis(data):                     # 3
    return hello(data, "agent za analizu gresaka ucenika", common_errors=["mesa klasifikaciju i regresiju"])


def objective_achievement(data):              # 4
    return hello(data, "agent za analizu ostvarenosti ciljeva", achieved={"O1": True, "O2": False})


def adaptive_adjustment(data):                # 5
    return hello(data, "agent za adaptivno prilagodjavanje nastave",
                 suggestion="vise primera za pocetnike")


def curriculum_evaluation(data):              # 6
    return hello(data, "agent za evaluaciju celokupnog kurikuluma", aligned=True)


def quality_evaluator(data):                  # 7
    # Lazna ocena: prvi put losa, posle dorade dobra -> vidimo da povratna sprega radi
    score = 60 if data["iteration"] == 0 else 90
    return hello(data, "agent za evaluaciju kvaliteta (Evaluator)", score=score)


def optimizer(data):                          # 8
    score = data["inputs"]["quality_evaluator"]["score"]
    return hello(data, "agent za optimizaciju (Optimizer)",
                 corrections=["dodati primere u lekciju 2"] if score < 75 else [])


def feedback_manager(data):                   # 9
    score = data["inputs"]["quality_evaluator"]["score"]
    threshold = data["settings"].get("quality_threshold", 75)
    needs_rework = score < threshold
    return hello(data, "agent za upravljanje povratnom spregom",
                 score=score, needs_rework=needs_rework,
                 return_to="content_creation" if needs_rework else None)


def final_report(data):                       # 10
    fb = data["inputs"]["feedback_manager"]
    return hello(data, "agent za generisanje zavrsnog izvestaja",
                 summary=f"Ocena {fb['score']}, potrebna dorada: {fb['needs_rework']}")
