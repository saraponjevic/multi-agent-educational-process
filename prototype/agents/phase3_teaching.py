"""FAZA 3 - Realizacija nastave  (8 "hello world" agenata; ucenik ima 3 instance)."""
from agents.common import hello


def teaching_scenario(data):                  # 1
    return hello(data, "agent za pripremu nastavnog scenarija",
                 scenario=["uvod", "objasnjenje", "pitanja ucenika", "zakljucak"])


def teacher(data):                            # 2
    lessons = data["inputs"]["lesson_generator"]["lessons"]
    return hello(data, "agent nastavnik", said=f"Danas radimo: {lessons[0]}",
                 question="Sta je klasifikacija?")


def student(data):                            # 3  (ista funkcija za vise ucenika)
    level = data["params"].get("level", "beginner")
    answers = {"beginner": "Nisam siguran...",
               "intermediate": "Nesto kao grupisanje?",
               "advanced": "Razvrstavanje primera u klase."}
    return hello(data, f"agent ucenik ({level})",
                 heard_question=data["inputs"]["teacher"]["question"],
                 answer=answers.get(level, "?"))


def knowledge_state(data):                    # 4
    return hello(data, "agent za upravljanje stanjem znanja ucenika",
                 knowledge={"student_beginner": 0.3, "student_intermediate": 0.6, "student_advanced": 0.9})


def classroom_controller(data):               # 5
    return hello(data, "agent za upravljanje ucionicom (Classroom Controller)",
                 order=["teacher", "student_beginner", "student_intermediate", "student_advanced"])


def activity_tracking(data):                  # 6
    return hello(data, "agent za pracenje nastavnih aktivnosti", transcript_lines=4)


def material_accuracy_check(data):            # 7
    return hello(data, "agent za proveru tacnosti materijala", errors_found=[])


def teaching_report(data):                    # 8
    return hello(data, "agent za izvestavanje o realizaciji nastave", report="Nastava odrzana (hello world).")
