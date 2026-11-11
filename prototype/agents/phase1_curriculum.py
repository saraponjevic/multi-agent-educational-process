"""
FAZA 1 - Dizajn kurikuluma  (9 "hello world" agenata)
"""
from agents.common import hello


def needs_analysis(data):                     # 1
    return hello(data, "agent za analizu obrazovnih potreba",
                 needs=["razumevanje osnovnih pojmova", "prakticna primena"])


def prior_knowledge_analysis(data):           # 2
    return hello(data, "agent za analizu predznanja",
                 prerequisites=["promenljive", "petlje", "funkcije"])


def existing_curricula_analysis(data):        # 3
    return hello(data, "agent za analizu postojecih kurikuluma",
                 compared=["Kurikulum A", "Kurikulum B"])


def competency_identification(data):          # 4
    return hello(data, "agent za identifikaciju kompetencija",
                 competencies=["K1: razume klasifikaciju", "K2: trenira model"])


def learning_outcomes(data):                  # 5
    return hello(data, "agent za definisanje nastavnih ishoda", outcomes=[
        {"id": "O1", "text": "Ucenik objasnjava pojam klasifikacije", "level": "razumevanje"},
        {"id": "O2", "text": "Ucenik trenira jednostavan model", "level": "primena"},
    ])


def curriculum_structure(data):               # 6
    outcomes = data["inputs"]["learning_outcomes"]["outcomes"]
    return hello(data, "agent za strukturiranje nastavnog plana", units=[
        {"unit": 1, "title": "Uvod", "outcomes": [outcomes[0]["id"]]},
        {"unit": 2, "title": "Prvi model", "outcomes": [outcomes[1]["id"]]},
    ])


def achievement_indicators(data):             # 7
    return hello(data, "agent za pokazatelje ostvarenosti ishoda",
                 indicators={"O1": "ucenik daje definiciju i primer", "O2": "ucenik preda istreniran model"})


def curriculum_validation(data):              # 8
    return hello(data, "agent za validaciju kurikuluma", valid=True)


def curriculum_documentation(data):           # 9
    return hello(data, "agent za generisanje dokumentacije kurikuluma",
                 document="# Kurikulum (hello world)")
