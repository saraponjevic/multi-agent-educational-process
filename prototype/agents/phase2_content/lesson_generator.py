"""
Agent za generisanje lekcija.                    *** KLJUCNI AGENT (LLM) ***

Ulaz:  nastavni plan, ishodi, (u doradi) primedbe optimizatora
Izlaz: {"lessons": [{"unit": 1, "title": "...", "text": "..."}]}
"""
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si iskusan nastavnik koji pise jasne, kratke i tacne lekcije prilagodjene nivou ucenika. "
    "Koristis jednostavan jezik i konkretne primere."
)


def run(data: dict) -> dict:
    course = data["course"]
    units = (data["inputs"].get("curriculum_structure") or {}).get("units", [])
    outcomes = (data["inputs"].get("learning_outcomes") or {}).get("outcomes", [])
    # Ako smo u doradi (povratna sprega), optimizator je ostavio primedbe:
    corrections = (data["inputs"].get("optimizer") or {}).get("corrections", [])

    rework_note = ""
    if data["iteration"] > 0 and corrections:
        rework_note = f"\nOVO JE DORADA. Uvazi sledece primedbe evaluacije:\n{to_text(corrections)}\n"

    user = f"""Kurs: {course['topic']}
Ciljna grupa: {course['target_group']}
Nastavni plan:
{to_text(units)}
Nastavni ishodi:
{to_text(outcomes)}
{rework_note}
Za SVAKU nastavnu jedinicu napisi lekciju od najvise 250 reci. Pisi na jeziku: {course['language']}.
Vrati JSON:
{{"lessons": [{{"unit": 1, "title": "...", "text": "..."}}]}}"""

    version = data["iteration"] + 1
    fallback = {"lessons": [
        {"unit": u.get("unit"), "title": u.get("title"), "text": f"(hello world tekst lekcije, verzija {version})"}
        for u in units
    ]}
    return ask_json(SYSTEM, user, fallback)
