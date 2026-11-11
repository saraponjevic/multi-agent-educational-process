"""FAZA 2 - Kreiranje nastavnih sadrzaja  (9 "hello world" agenata)."""
import time

from agents.common import hello


def lesson_generator(data):                   # 1
    units = data["inputs"]["curriculum_structure"]["units"]
    version = data["iteration"] + 1           # posle dorade pravimo "novu verziju"
    return hello(data, f"agent za generisanje lekcija (verzija {version})",
                 lessons=[f"Lekcija {u['unit']}: {u['title']} (v{version})" for u in units])


def instructional_strategy(data):             # 2
    return hello(data, "agent za izbor instrukcione strategije", strategy="ucenje kroz primere")


def activity_planning(data):                  # 3
    return hello(data, "agent za planiranje nastavnih aktivnosti",
                 activities=["uvodno pitanje", "rad u parovima"])


def example_generator(data):                  # 4
    time.sleep(1)    # glumimo rad 1s - da se vidi paralelizam
    return hello(data, "agent za generisanje primera", examples=["primer A", "primer B"])


def exercise_generator(data):                 # 5
    time.sleep(1)    
    return hello(data, "agent za generisanje zadataka",
                 exercises=[{"id": "Z1", "difficulty": "lako"}, {"id": "Z2", "difficulty": "srednje"}])


def exercise_solver(data):                    # 6
    return hello(data, "agent za resavanje zadataka", solutions={"Z1": "resenje 1", "Z2": "resenje 2"})


def material_quality_check(data):             # 7
    return hello(data, "agent za proveru kvaliteta materijala", ok=True)


def formatting_export(data):                  # 8
    return hello(data, "agent za formatiranje i eksport", format="markdown")


def material_organization(data):              # 9
    return hello(data, "agent za organizaciju i distribuciju materijala",
                 collection={"unit_1": ["lekcija", "primeri"], "unit_2": ["lekcija", "zadaci"]})
