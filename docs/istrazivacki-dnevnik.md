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

## Nedelja 3

**Period:** 04.11.2026 – 10.11.2026.

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
