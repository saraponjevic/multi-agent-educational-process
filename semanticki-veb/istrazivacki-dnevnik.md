# Istraživački dnevnik

## Nedelja 1

**Period:** 02.11.2026 – 08.11.2026.

### Realizovane aktivnosti

**05.11.2026. – Istraživanje grafova znanja i RAG sistema u multiagentskim sistemima**

- Proučila osnove semantičkog veba (RDF, RDFS, OWL, SPARQL) i RAG/GraphRAG pristup
- Uradila pregled literature o grafovima i RAG-u u multiagentskim sistemima i u obrazovanju
- Predložila arhitekturu u kojoj je graf znanja zajednička memorija agenata, a RAG služi za utemeljenje sadržaja u izvorima
- Nacrtala skice grafa kurikuluma i arhitekture sistema
- Analizirala alate, rizike i ograničenja i definisala dalje korake

---

## Nedelja 2

**Period:** 09.11.2026 – 15.11.2026.

### Realizovane aktivnosti

**10.11.2026. – Graf znanja kao zajednička memorija agenata u simulaciji nastavnog procesa**

- Implementacija osnovnih agenata u svakoj od 4 faze nastavnog procesa
- Napravila sam ontologiju kurikuluma u RDFS/OWL-u (ontologija.ttl), sa klasama, vezama, domenom i opsegom.
- Definisala sam pravila za agente u grafu: ko sme šta da upiše.
- Implementirala sam zajednički graf znanja (rdflib) kao memoriju za sve četiri faze. Svaki upis se proverava prema ontologiji.
- Agenti iz svih faza upisuju rezultate u graf kao trojke, a kasniji agenti čitaju strukturu iz grafa SPARQL upitima umesto teksta.
- Napisala sam 8 SPARQL pravila za proveru kurikuluma. Ona se koriste u validaciji, evaluaciji i povratnoj sprezi.
- Ostvarenost ishoda se računa SPARQL upitom nad grafom.
- Graf sam vizualizovala (HTML prikaz, Mermaid) i proverila u Protégé-u.

---
