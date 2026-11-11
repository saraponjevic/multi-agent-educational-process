"""
Agent za definisanje nastavnih ishoda.          *** KLJUCNI AGENT (LLM) ***

Ulaz:  tema kursa, kompetencije, predznanje
Izlaz: {"outcomes": [{"id": "O1", "competency": "K1", "text": "...", "level": "...", "indicator": "..."}]}
Graf:  Kompetencija --imaIshod--> NastavniIshod   (vidi write_graph na dnu)

OVO JE UZOR kako izgleda "pravi" agent:
  1. iz `data` uzmes sta ti treba
  2. napises SYSTEM poruku (ko je agent) i USER poruku (sta tacno da uradi + format)
  3. pozoves ask_json(...) i das mu FALLBACK (hello world odgovor za mock rezim)
"""
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si strucnjak za dizajn kurikuluma i instrukcioni dizajn. "
    "Formulises MERLJIVE nastavne ishode koristeci aktivne glagole (Blumova taksonomija)."
)


def run(data: dict) -> dict:
    course = data["course"]
    competencies = (data["inputs"].get("competency_identification") or {}).get("competencies", [])
    prior = (data["inputs"].get("prior_knowledge_analysis") or {}).get("prerequisites", [])

    user = f"""Kurs: {course['topic']}
Ciljna grupa: {course['target_group']}
Broj nastavnih jedinica: {course['num_units']}
Zahtevi: {course.get('requirements', '')}
Kompetencije koje treba razviti: {to_text(competencies)}
Predznanje ucenika: {to_text(prior)}

Definisi 3 do 5 merljivih nastavnih ishoda. Svaki ishod vezi za jednu kompetenciju (polje "competency" = oznaka kompetencije, npr. K1).
Pisi na jeziku: {course['language']}.
Vrati JSON u formatu:
{{"outcomes": [{{"id": "O1", "competency": "K1", "text": "Ucenik ce moci da ...", "level": "pamcenje|razumevanje|primena|analiza|sinteza|evaluacija", "indicator": "sta ucenik konkretno pokazuje/predaje"}}]}}"""

    fallback = {"outcomes": [
        {"id": "O1", "competency": "K1", "text": "Ucenik objasnjava osnovni pojam teme", "level": "razumevanje",
         "indicator": "daje definiciju i primer"},
        {"id": "O2", "competency": "K2", "text": "Ucenik primenjuje znanje na jednostavnom zadatku", "level": "primena",
         "indicator": "resava zadatak"},
    ]}
    return ask_json(SYSTEM, user, fallback)

def write_graph(result: dict, g):
    """
    GRAF: rezultat agenta -> cvorovi i veze.
        :Komp_K1  :imaIshod  :Ishod_O1 .
        :Ishod_O1 a :NastavniIshod ; rdfs:label "..." ; :nivo "primena" .
    Pokazatelj (indicator) NE upisuje ovaj agent - to je posao agenta za pokazatelje.
    """
    for o in result.get("outcomes", []):
        ishod = g.node("NastavniIshod", f"Ishod_{o['id']}", label=o.get("text"))
        g.value(ishod, "nivo", o.get("level"))
        if o.get("competency"):
            g.link(g.ref(f"Komp_{o['competency']}"), "imaIshod", ishod)
