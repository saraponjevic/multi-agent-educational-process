"""
Agent nastavnik (Teaching Agent).                *** KLJUCNI AGENT (LLM) ***

Ulaz:  sve lekcije, scenario
Izlaz: {"explanation": "...", "question": "..."}

Nastavnik predaje SVE nastavne jedinice (kratko), jer test u fazi 4 proverava sve ishode.
Ono sto nastavnik ovde kaze je JEDINO znanje koje simulirani ucenici imaju.
Kasnije (Classroom Controller): vise krugova pitanja i odgovora.
"""
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si nastavnik koji drzi cas. Objasnjavas gradivo jasno i strpljivo, "
    "a na kraju postavis jedno pitanje kojim proveravas razumevanje."
)


def run(data: dict) -> dict:
    course = data["course"]
    lessons = (data["inputs"].get("lesson_generator") or {}).get("lessons", [])
    scenario = (data["inputs"].get("teaching_scenario") or {}).get("scenario", [])

    user = f"""Drzis cas iz kursa "{course['topic']}" za: {course['target_group']}.
Scenario casa: {to_text(scenario)}
Lekcije koje predajes (SVE moras da obradis, redom):
{to_text(lessons)}

Napisi kako objasnjavas gradivo ucenicima, kao da govoris u ucionici.
Obradi SVAKU lekciju (oko 150 reci po lekciji). Ukljuci kljucne pojmove, formule i korake
koje ucenici treba da zapamte. Na kraju postavi JEDNO pitanje za proveru razumevanja.
Pisi na jeziku: {course['language']}.
Vrati JSON: {{"explanation": "...", "question": "..."}}"""

    titles = ", ".join(str(l.get("title")) for l in lessons) or course["topic"]
    fallback = {
        "explanation": f"(hello world) Danas radimo: {titles}",
        "question": "Mozete li svojim recima objasniti osnovni pojam?",
    }
    return ask_json(SYSTEM, user, fallback)
