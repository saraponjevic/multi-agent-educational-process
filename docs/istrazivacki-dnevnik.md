# Istraživački dnevnik

## Nedelja 1

**Period:** 21.10.2026 – 27.10.2026.

### Realizovane aktivnosti

- Analiziran je **projektni zadatak** i definisane su četiri faze nastavnog procesa: **dizajn nastave, kreiranje sadržaja, izvođenje nastave i evaluacija**.
- Razmatrane su **uloge AI agenata** u svakoj fazi i započeta je analiza **naučne literature**.

### Sledeći korak

Detaljnije istraživanje **arhitektura multiagentskih sistema**, kao i identifikacija agenata po fazama nastavnog procesa.

---

## Nedelja 2

**Period:** 28.10.2026 – 03.11.2026.

### Realizovane aktivnosti

**28.10.2026. – Identifikacija agenata i organizacija repozitorijuma**

- Identifikovani su agenti za sve četiri faze nastavnog procesa i definisane njihove **uloge, ulazni i izlazni podaci**.
- Organizovana je projektna dokumentacija i postavljeni su istraživački materijali na **GitHub repozitorijum**.

**29.10.2026. – Istraživanje framework-a**

- Istraženi su framework-i za razvoj multiagentskih sistema: **LangGraph, CrewAI i Microsoft Agent Framework**.
- Analizirane su njihove mogućnosti za **orkestraciju, komunikaciju i povezivanje agenata**.

**30.10.2026. – Projektovanje početne arhitekture**

- Razmatrana je arhitektura sistema i izrađen **početni arhitektonski predlog**.
- Definisane su glavne komponente: **generički engine, Agent Registry, glavni orkestrator i fazni orkestratori**.
- Kao početni izbor za orkestraciju predložen je **LangGraph**.

---

## Nedelja 3 i 4

**Period:** 04.11.2026 – 10.11.2026; 11.11.2026 - 17.11.2026.

### Realizovane aktivnosti

**08.11.2026. – Ispravljanje arhitekture i agenata po fazama**

- Identifikovane su sugestije koje je profesor rekao na terminu vezbi
- Ispravljen spisak agenata po fazama kao i slika arhitekture sistema

**10.11.2026. – Početak implementacije prototipa**

- Postavljeno razvojno okruženje (Python 3.13, `.venv`, LangGraph); kod smešten u folder `prototype/`.
- Realizovan generički engine: registracija agenata preko konfiguracionog fajla (`config/agents.yaml`), pozivanje lokalnih i eksternih (HTTP) agenata, evidencija izvršavanja i obrada grešaka.
- Realizovana orkestracija u LangGraph-u: faze se izvršavaju sekvencijalno, agenti unutar faze paralelno, a povratna sprega vraća tok na fazu 2 kada je ocena ispod praga.
- Napravljeno svih 36 agenata kao „hello world" verzije, svaki u zasebnom fajlu.
- Ključni agenti po fazama povezani sa jezičkim modelom (Groq, `gpt-oss-120b`): nastavni ishodi i nastavni plan, lekcije i zadaci, nastavnik i tri simulirana učenika, test i ocenjivanje.

**15.11.2026. – Eksport nastavnih materijala**
- Agent za formatiranje i eksport (faza 2) više nije hello world. Od rezultata drugih agenata pravi kurikulum.md, lekcije.md i zadaci.md (bez LLM-a).
- Agent za generisanje završnog izveštaja (faza 4) više nije hello world. Pravi test.md (pitanja i ključ) i izvestaj.md (tok časa, ocene i odgovori učenika, odluka povratne sprege).
- Materijali se posle svakog pokretanja čuvaju u output/materijali_<vreme>/, pored JSON evidencije.

---

## Nedelja 5

**Period:** 18.11.2026 – 24.11.2026.

### Realizovane aktivnosti

**19.11.2026. – Nova implementacija realizacije nastave - dodate aktivnosti, faza poducavanja, unapredjenje ucenika**

- Uveden je pojam **aktivnosti**, čvora u grafu koji nije novi agent, već radnja postojećih agenata nad postojećim resursom. Polaganje testa je modelovano kao aktivnost u kojoj simulirani učenici rade test, a njihovi odgovori se prosleđuju agentu za ocenjivanje.
- Realizovana je **faza podučavanja**: nastavnik deli lekciju na delove i isporučuje ih učenicima jedan po jedan.
- Engine je proširen mogućnošću sekvencioniranja agenata unutar faze: pored redosleda po koracima i paralelnog izvršavanja, faza može imati **petlju** (LangGraph uslovna ivica) koja ponavlja korake dok se ne ispuni uslov.
- Simulirani učenik je modelovan kao **generički interfejs** sa memorijom znanja (početno predznanje + usvojeno na času) i operacijama za prijem novog znanja i rešavanje testa. Implementirana je grubo simulirana verzija u kojoj učenik deo lekcije usvaja sa verovatnoćom koja zavisi od nivoa, pa rezultat na testu zavisi od onoga što je zaista naučio.

**20.11.2026. – Razrada nastavnih materijala na primeru mašinskog učenja + vizualizacija simulacije**

- Za kurs iz klasifikacije definisani su **studija slučaja** (klasifikacija e-poruka na spam / nije spam) i **ograničenja** kursa, koje koriste svi agenti.
- Lekcije su strukturirane kao prave lekcije: uvod, objašnjenje, rešen primer korak po korak, kod, česte greške, rezime i pitanja za proveru.
- Zadaci su različitih vrsta (pojmovni, računski, programski, pronalaženje greške), sa konkretnim podacima i rešenjima. Uvedena je nezavisna provera zadataka i provera kvaliteta materijala po pravilima.
- Razvijena je veb aplikacija za vizualizaciju simulacije (backend **FastAPI**, frontend **React**). Korisnik zadaje temu kursa, a aplikacija prikazuje trenutnu fazu, rad agenata i aktivnosti, isporuku delova lekcije učenicima i artefakte koje su agenti napravili.
- Svako pokretanje se čuva i može se kasnije reprodukovati.

---
