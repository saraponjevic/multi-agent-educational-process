"""
GRAF ZNANJA - zajednicka memorija svih agenata (RDF / OWL / SPARQL, biblioteka rdflib).

Ideja:
  - Agenti i dalje vracaju JSON (kao do sada), ali agent moze imati i funkciju
        write_graph(result, g)
    koja svoj rezultat prevodi u CVOROVE i VEZE grafa.
  - Engine (invoker) poziva write_graph i UPISUJE u graf tek posto proveri pravila:
        1. agent pravi samo cvorove klasa koje sme      (knowledge/agenti.ttl  :kreira)
        2. agent koristi samo svojstva iz ontologije     (knowledge/ontologija.ttl)
        3. tudje cvorove menja samo dozvoljenim svojstvima (:dopunjuje)
        4. veze postuju domen i opseg (rdfs:domain / rdfs:range)
  - Svaki agent pise u SVOJ imenovani graf (named graph), pa se uvek zna ko je sta upisao.
    Kada agent radi ponovo (povratna sprega), njegov stari deo grafa se zameni novim.
  - Agenti CITAJU graf preko SPARQL upita:  data["kg"].query("SELECT ...")
  - Pravila kvaliteta su SPARQL upiti u knowledge/pravila/*.rq:  data["kg"].check([...])

Na kraju pokretanja graf se cuva u output/ kao:
  graf_<vreme>.ttl   - ceo graf + ontologija (otvara se u Protege-u)
  graf_<vreme>.trig  - isto, ali podeljeno po agentima (ko je sta upisao)
  graf_<vreme>.md    - crtez grafa (Mermaid) - GitHub i VS Code ga prikazuju kao sliku
"""
import re
import threading
from pathlib import Path

from rdflib import RDF, RDFS, OWL, XSD, Dataset, Graph, Literal, Namespace, URIRef

K = Namespace("http://example.org/kurikulum#")          # nasi pojmovi:  K.NastavniIshod, K.Ishod_O1 ...
GRAF = "http://example.org/kurikulum/graf/"              # imena podgrafova: .../graf/learning_outcomes

PREFIXES = """PREFIX :     <http://example.org/kurikulum#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
"""

_SR = str.maketrans({"č": "c", "ć": "c", "š": "s", "ž": "z", "đ": "dj",
                     "Č": "C", "Ć": "C", "Š": "S", "Ž": "Z", "Đ": "Dj"})


def slug(text) -> str:
    """'Uvod u klasifikaciju' -> 'Uvod_u_klasifikaciju' (za ime cvora)."""
    text = str(text).translate(_SR)
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_") or "x"


class GraphRuleError(Exception):
    """Agent je prekrsio pravilo upisa u graf."""


# ======================================================================
#  AgentWriter - "olovka" koju dobija jedan agent
# ======================================================================
class AgentWriter:
    """
    Pomocnik koji agent koristi u write_graph(result, g):

        ishod = g.node("NastavniIshod", "Ishod_O1", label="Ucenik ce moci da ...")
        g.link(kompetencija, "imaIshod", ishod)
        g.value(ishod, "nivo", "primena")

    Nista se ne upisuje odmah - engine na kraju proveri pravila i tek onda upise sve.
    """

    def __init__(self, agent_id: str, course: URIRef, iteration: int):
        self.agent_id = agent_id
        self.course = course                     # cvor kursa (napravljen iz config/course.yaml)
        self.iteration = iteration
        self.triples: list = []

    @staticmethod
    def ref(key: str) -> URIRef:
        """Referenca na postojeci cvor po imenu, npr. g.ref('Ishod_O1')."""
        return K[slug(key)]

    def node(self, cls: str, key: str, label: str | None = None) -> URIRef:
        uri = self.ref(key)
        self.triples.append((uri, RDF.type, K[cls]))
        if label:
            self.triples.append((uri, RDFS.label, Literal(str(label))))
        self.triples.append((uri, K.verzija, Literal(self.iteration + 1, datatype=XSD.integer)))
        return uri

    def link(self, subject: URIRef, prop: str, obj: URIRef):
        self.triples.append((subject, K[prop], obj))

    def value(self, subject: URIRef, prop: str, val):
        if val is None or val == "":
            return
        dt = XSD.integer if isinstance(val, int) and not isinstance(val, bool) else None
        self.triples.append((subject, K[prop], Literal(val, datatype=dt) if dt else Literal(str(val))))


# ======================================================================
#  KnowledgeGraph
# ======================================================================
class KnowledgeGraph:
    def __init__(self, folder: str | Path):
        self.folder = Path(folder)
        self.ds = Dataset(default_union=True)    # upiti vide sve podgrafove zajedno
        self.ds.bind("", K)
        self._lock = threading.RLock()            # agenti rade paralelno -> jedan po jedan pise
        self.course: URIRef | None = None

        self.ds.graph(URIRef(GRAF + "ontologija")).parse(self.folder / "ontologija.ttl", format="turtle")
        self.ds.graph(URIRef(GRAF + "pravila_agenata")).parse(self.folder / "agenti.ttl", format="turtle")
        self.rules = self._load_rules(self.folder / "pravila")

    # ------------------------------------------------------------------
    #  Priprema
    # ------------------------------------------------------------------
    @staticmethod
    def _load_rules(folder: Path) -> dict:
        """Ucitava knowledge/pravila/*.rq. Iz komentara cita '# opis:' i '# odgovoran:'."""
        rules = {}
        for f in sorted(folder.glob("*.rq")):
            text = f.read_text(encoding="utf-8")
            meta = dict(re.findall(r"^#\s*(opis|odgovoran):\s*(.+)$", text, flags=re.MULTILINE))
            rules[f.stem] = {"query": text, "opis": meta.get("opis", "").strip(),
                             "odgovoran": meta.get("odgovoran", "").strip()}
        return rules

    def register_system(self, registry, course: dict):
        """Upisuje u graf: sve agente sa fazom (iz agents.yaml) i kurs (iz course.yaml)."""
        with self._lock:
            g = self.ds.graph(URIRef(GRAF + "sistem"))
            for a in registry.agents.values():
                uri = K["agent_" + a.id]
                g.add((uri, RDF.type, K.Agent))
                g.add((uri, RDFS.label, Literal(a.name)))
                g.add((uri, K.agentId, Literal(a.id)))
                g.add((uri, K.pripadaFazi, Literal(a.phase)))

            self.course = K["Kurs_" + slug(course["topic"])]
            u = self.ds.graph(URIRef(GRAF + "ulaz"))
            u.add((self.course, RDF.type, K.Kurs))
            u.add((self.course, RDFS.label, Literal(course["topic"])))
            u.add((self.course, K.ciljnaGrupa, Literal(course.get("target_group", ""))))

    def writer(self, agent_id: str, iteration: int) -> AgentWriter:
        return AgentWriter(agent_id, self.course, iteration)

    # ------------------------------------------------------------------
    #  Upis uz proveru pravila
    # ------------------------------------------------------------------
    def _allowed(self, agent_id: str, prop: URIRef) -> set:
        return set(self.ds.objects(K["agent_" + agent_id], prop))

    def _is_a(self, g: Graph, node, cls) -> bool:
        """Da li je cvor tipa cls (ukljucujuci podklase: Lekcija je i Materijal)."""
        return any(t == cls or (t, RDFS.subClassOf * "+", cls) in g for t in g.objects(node, RDF.type))

    def commit(self, agent_id: str, writer: AgentWriter) -> dict:
        """Proverava pravila i upisuje trojke agenta u njegov podgraf. Vraca kratak izvestaj."""
        with self._lock:
            may_create = self._allowed(agent_id, K.kreira)
            may_extend = self._allowed(agent_id, K.dopunjuje)
            if not (may_create or may_extend):
                raise GraphRuleError(
                    f"Agent '{agent_id}' nema pravo upisa u graf (dodaj ga u knowledge/agenti.ttl)")

            # 1) klase novih cvorova
            own_nodes = set()
            for s, p, o in writer.triples:
                if p == RDF.type:
                    if o not in may_create:
                        raise GraphRuleError(
                            f"Agent '{agent_id}' ne sme da pravi cvorove klase {o.n3(self.ds.namespace_manager)}"
                            f" (dozvoljeno: {sorted(x.n3(self.ds.namespace_manager) for x in may_create)})")
                    own_nodes.add(s)

            # 2) i 3) svojstva
            known = {RDF.type, RDFS.label}
            for s, p, o in writer.triples:
                if p in known:
                    continue
                if not any((p, RDF.type, t) in self.ds for t in (OWL.ObjectProperty, OWL.DatatypeProperty)):
                    raise GraphRuleError(f"Agent '{agent_id}' koristi svojstvo koje ne postoji u ontologiji: {p}")
                if s not in own_nodes and p not in may_extend:
                    raise GraphRuleError(
                        f"Agent '{agent_id}' pokusava da menja tudji cvor {s.n3(self.ds.namespace_manager)}"
                        f" svojstvom {p.n3(self.ds.namespace_manager)} (nije u :dopunjuje)")

            # stari upis ovog agenta (ako radi ponovo) se brise
            gname = URIRef(GRAF + agent_id)
            self.ds.remove_graph(gname)

            # 4) domen i opseg - proveravamo nad "ostatak grafa + novi upis"
            view = Graph()
            for t in self.ds.triples((None, None, None)):
                view.add(t)
            for t in writer.triples:
                view.add(t)

            accepted, rejected = [], []
            for s, p, o in writer.triples:
                problem = None
                for d in self.ds.objects(p, RDFS.domain):
                    if not self._is_a(view, s, d):
                        problem = f"{s.n3(self.ds.namespace_manager)} nije {d.n3(self.ds.namespace_manager)}"
                for r in self.ds.objects(p, RDFS.range):
                    if (r, RDF.type, OWL.Class) in self.ds and not self._is_a(view, o, r):
                        problem = f"{o.n3(self.ds.namespace_manager)} nije {r.n3(self.ds.namespace_manager)}"
                if problem:
                    rejected.append(f"{p.n3(self.ds.namespace_manager)}: {problem}")
                else:
                    accepted.append((s, p, o))

            g = self.ds.graph(gname)
            for t in accepted:
                g.add(t)
            return {"upisano_trojki": len(accepted), "odbijeno": rejected}

    # ------------------------------------------------------------------
    #  Citanje
    # ------------------------------------------------------------------
    def query(self, sparql: str) -> list[dict]:
        """SPARQL SELECT nad celim grafom. Prefiks ':' je vec definisan. Vraca listu recnika."""
        if "PREFIX" not in sparql.upper():
            sparql = PREFIXES + sparql
        with self._lock:
            result = self.ds.query(sparql)
            names = [str(v) for v in result.vars]
            return [{n: (None if row[i] is None else self._short(row[i])) for i, n in enumerate(names)}
                    for row in result]

    def _short(self, term):
        if isinstance(term, Literal):
            return term.toPython()
        if isinstance(term, URIRef) and str(term).startswith(str(K)):
            return ":" + str(term)[len(str(K)):]
        return str(term)

    def check(self, rule_names: list[str] | None = None) -> list[dict]:
        """Pokrece pravila (SPARQL) i vraca listu prekrsaja: [{pravilo, cvor, poruka, odgovoran}]."""
        violations = []
        for name in rule_names or self.rules:
            rule = self.rules[name]
            for row in self.query(rule["query"]):
                violations.append({"pravilo": name, "cvor": row.get("cvor"),
                                   "poruka": row.get("poruka"), "odgovoran": rule["odgovoran"]})
        return violations

    def phase_of(self, agent_id: str) -> str | None:
        rows = self.query(f'SELECT ?f WHERE {{ ?a :agentId "{agent_id}" ; :pripadaFazi ?f }}')
        return rows[0]["f"] if rows else None

    # ------------------------------------------------------------------
    #  Cuvanje
    # ------------------------------------------------------------------
    def stats(self) -> dict:
        with self._lock:
            per_agent = {}
            for g in self.ds.graphs():
                name = str(g.identifier)
                if name.startswith(GRAF):
                    per_agent[name[len(GRAF):]] = len(g)
            return per_agent

    def to_mermaid(self, max_edges: int = 200) -> str:
        """Crtez cvorova koje su napravili agenti i veza medju njima (bez ontologije i opisa sistema)."""
        skip = {URIRef(GRAF + n) for n in ("ontologija", "pravila_agenata", "sistem")}
        colors = {"Kurs": "#f9e79f", "Kompetencija": "#d6eaf8", "NastavniIshod": "#aed6f1",
                  "NastavnaJedinica": "#d5f5e3", "Tema": "#abebc6", "Lekcija": "#fdebd0",
                  "Zadatak": "#fad7a0", "Test": "#f5b7b1", "Pitanje": "#fadbd8",
                  "Ucenik": "#e8daef", "Odgovor": "#d7bde2"}
        with self._lock:
            data = Graph()
            for g in self.ds.graphs():
                if g.identifier not in skip:
                    for t in g:
                        data.add(t)
            ids, lines, classes = {}, ["flowchart LR"], {}

            def nid(node):
                if node not in ids:
                    ids[node] = f"n{len(ids)}"
                    name = str(node).split("#")[-1]
                    cls = next((str(c).split("#")[-1] for c in data.objects(node, RDF.type)), "")
                    lines.append(f'    {ids[node]}["{cls}<br/>{name}"]')
                    if cls in colors:
                        classes.setdefault(cls, []).append(ids[node])
                return ids[node]

            edges = 0
            for s_, p, o in sorted(data):
                if isinstance(o, URIRef) and p != RDF.type and edges < max_edges:
                    lines.append(f"    {nid(s_)} -->|{str(p).split('#')[-1]}| {nid(o)}")
                    edges += 1
            for cls, nodes in classes.items():
                lines.append(f"    classDef c{cls} fill:{colors[cls]},stroke:#555")
                lines.append(f"    class {','.join(nodes)} c{cls}")
            return "\n".join(l for l in lines if l)

    def save(self, out_dir: Path, stem: str) -> list[Path]:
        with self._lock:
            out_dir.mkdir(exist_ok=True)
            trig = out_dir / f"{stem}.trig"
            self.ds.serialize(trig, format="trig")
            flat = Graph()
            flat.bind("", K)
            for t in self.ds.triples((None, None, None)):
                flat.add(t)
            ttl = out_dir / f"{stem}.ttl"
            flat.serialize(ttl, format="turtle")
            md = out_dir / f"{stem}.md"
            md.write_text("# Graf znanja posle pokretanja\n\n```mermaid\n" + self.to_mermaid() + "\n```\n",
                          encoding="utf-8")
            return [ttl, trig, md]
