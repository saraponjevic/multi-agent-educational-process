"""
Agent za analizu ostvarenosti nastavnih ciljeva.

STATUS: pravi agent bez LLM-a. Jednim SPARQL upitom (agregacija AVG + GROUP BY)
iz grafa racuna koliko su ucenici uspesni na pitanjima za svaki ishod:

    ishod <- proveravaIshod - pitanje <- naPitanje - odgovor (poeni)

Ishod je ostvaren ako je prosecan uspeh bar 50%.
"""
from agents.common import hello

USPEH_PO_ISHODU = """
SELECT ?ishod ?naziv (AVG(?poeni) / 2 AS ?uspeh) (COUNT(?odgovor) AS ?odgovora) WHERE {
  ?ishod a :NastavniIshod ; rdfs:label ?naziv .
  OPTIONAL { ?pitanje :proveravaIshod ?ishod .
             ?odgovor :naPitanje ?pitanje ; :poeni ?poeni . }
}
GROUP BY ?ishod ?naziv
ORDER BY ?ishod
"""


def run(data: dict) -> dict:
    kg = data.get("kg")
    if kg is None:
        return hello(data, "agent za analizu ostvarenosti nastavnih ciljeva", achieved={})
    achieved, details = {}, []
    for r in kg.query(USPEH_PO_ISHODU):
        oid = r["ishod"].removeprefix(":Ishod_")
        uspeh = float(r["uspeh"]) if r["uspeh"] is not None else None
        achieved[oid] = uspeh is not None and uspeh >= 0.5
        details.append({"outcome": oid, "text": r["naziv"], "success": None if uspeh is None else round(uspeh, 2),
                        "answers": int(r["odgovora"])})
        print(f"      [ishodi] {oid}: uspeh {'-' if uspeh is None else f'{uspeh:.0%}'}")
    return hello(data, "agent za analizu ostvarenosti nastavnih ciljeva", achieved=achieved, details=details)
