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

## Nedelja 3

**Period:** 16.11.2026 – 22.11.2026.

### Realizovane aktivnosti

**16.11.2026. – Termin sa asistentom**

- Dobila sam pitanja o ulozi grafa: šta je izlaz sistema, da li se graf koristi kao ulaz u sledeću fazu, za šta će služiti i kako voditi računa o ograničenjima LLM modela.
- Zadatak: osmisliti upotrebu grafa koja ima jasnu svrhu, a ne ubacivati ga na silu.

**19.11.2026. – Usklađivanje grafa sa novom arhitekturom sistema**

- U ontologiju sam dodala klasu **Aktivnost**. Aktivnosti (učenje na času, polaganje testa) nisu agenti, nego radnje postojećih agenata, i sada su opisane u grafu.
- Pravila za upis u graf (`agenti.ttl`) sam prebacila sa posebnih agenata-učenika na aktivnosti, koje sada upisuju učenike i njihove odgovore na testu.
- Proverila sam da svi upisi u graf prolaze proveru prema ontologiji i pravilima: nijedan upis nije odbijen.

**20.11.2026. – Analiza uloge grafa i ideje za dalji rad**

- Analizirala sam kako se graf trenutno koristi: kao **ulaz za agente** (8 agenata čita strukturu SPARQL upitima umesto teksta), za **kontrolu kvaliteta i povratnu spregu** (8 SPARQL pravila) i za **sledljivost** (svaki agent piše u svoj imenovani graf).
- Uočila sam da faza 3 u grafu nije dovoljno detaljna: nema delova časa, ni koji je učenik usvojio koji deo.
- Predložila sam načine da graf ima stvarnu svrhu: preduslovi koji utiču na učenje simuliranog učenika, ciljana dorada slabo ostvarenih ishoda, objašnjenje rezultata testa iz grafa, kao i RAG graf nad uzorcima materijala.
- Analizirala sam ograničenja LLM modela: od oko 36 agenata model koristi samo desetak, a dostignut je limit tokena besplatnog nivoa. Graf tu pomaže jer agentu može da se da samo deo strukture koji mu treba.
- Napravila sam fajl `beleske-i-ideje.md` za zaključke, ideje i sugestije asistenta na jednom mestu.

