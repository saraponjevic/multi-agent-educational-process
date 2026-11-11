"""
SPARQL nad sacuvanim grafom znanja - za vezbu i proveru.

    python kg_query.py                         -> pokrene SVA pravila nad poslednjim grafom iz output/
    python kg_query.py knowledge/upiti/ishodi_i_pitanja.rq    -> pokrene tvoj upit (.rq fajl)
    python kg_query.py "SELECT ?i ?n WHERE { ?i a :NastavniIshod ; rdfs:label ?n }"
    python kg_query.py --file output/graf_20261111_203000.ttl  ... -> nad tacno tim grafom
"""
import argparse
import sys
from pathlib import Path

from rdflib import Graph

from engine.knowledge_graph import PREFIXES, KnowledgeGraph

ROOT = Path(__file__).parent

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", help="SPARQL upit ili putanja do .rq fajla")
    parser.add_argument("--file", help="graf (.ttl); podrazumevano poslednji iz output/")
    args = parser.parse_args()

    files = sorted((ROOT / "output").glob("graf_*.ttl"))
    path = Path(args.file) if args.file else (files[-1] if files else None)
    if not path or not path.exists():
        print("Nema sacuvanog grafa - prvo pokreni:  python main.py")
        return
    g = Graph().parse(path, format="turtle")
    print(f"Graf: {path.name}  ({len(g)} trojki)\n")

    if not args.query:
        rules = KnowledgeGraph._load_rules(ROOT / "knowledge" / "pravila")
        for name, rule in rules.items():
            rows = list(g.query(rule["query"]))
            mark = "OK " if not rows else f"{len(rows)} PREKRSAJ(A)"
            print(f"[{mark}] {name}: {rule['opis']}")
            for r in rows:
                print(f"        - {r.poruka}")
        return

    text = Path(args.query).read_text(encoding="utf-8") if args.query.endswith(".rq") else args.query
    if "PREFIX" not in text.upper():
        text = PREFIXES + text
    result = g.query(text)
    names = [str(v) for v in result.vars]
    print(" | ".join(names))
    print("-" * 60)
    for row in result:
        print(" | ".join(g.namespace_manager.normalizeUri(v) if hasattr(v, "n3") and not hasattr(v, "language")
                         else str(v) for v in row))
    print(f"\n({len(result)} redova)")


if __name__ == "__main__":
    main()
