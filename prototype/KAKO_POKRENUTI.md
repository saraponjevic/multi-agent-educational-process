# Kako pokrenuti prototip

## Prvi put (instalacija)
```powershell
cd prototype
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# vizuelna platforma (React) - treba Node.js (https://nodejs.org, LTS verzija)
cd frontend
npm install
npm run build                     # napravi gotovu stranicu u frontend/dist
cd ..
```
Posle svake izmene u `frontend/src` ponovo `npm run build` (ili koristi razvojni režim, vidi dole).

## Svaki sledeći put
```powershell
cd prototype
.venv\Scripts\activate
python app.py                     # VIZUELNA PLATFORMA: FastAPI server + React stranica (http://127.0.0.1:8000)
python main.py                    # pokreni ceo nastavni proces u terminalu
python main.py --list             # samo prikaži registrovane agente
python main.py --graph            # sačuvaj dijagram grafa u docs/graph.md
python main.py --course "Osnove SQL upita"   # druga tema (inače se čita config/course.yaml)
python main.py --no-kg            # bez grafa znanja (kao ranije)
python kg_query.py                # SPARQL pravila nad poslednjim sačuvanim grafom
python kg_query.py knowledge/upiti/plan_kursa.rq   # tvoj SPARQL upit
```

## Graf znanja (Semantički veb)
Agenti upisuju rezultate u zajednički RDF graf; engine proverava pravila iz
`knowledge/ontologija.ttl` i `knowledge/agenti.ttl`, a kvalitet se proverava
SPARQL pravilima iz `knowledge/pravila/`. Graf se čuva u `output/graf_*.ttl`
(otvara se u Protégé-u), a crtež grafa u `output/graf_*.md`. Detaljno: `../semanticki-veb/graf-znanja-u-prototipu.md`.

## Vizuelna platforma (`python app.py`)
Otvara se stranica u pregledaču. Upišeš „Želim kurs o …" i gledaš uživo:
- **Faze** – u kojoj si fazi i koliko je završeno,
- **Tok faze** – koji agent / koja aktivnost radi (plavo), završila (zeleno), pukla (crveno);
  narandžasti isprekidani okvir je **petlja** (nastavnik ↔ učenici) sa brojem kruga,
- **Učionica** – na tabli je deo lekcije koji nastavnik upravo predaje; tačkica leti do svakog učenika:
  zelena = usvojio, siva = čuo ali nije usvojio; trake pokazuju koliko je ko naučio, posle testa i ocenu,
- **Artefakti** – sve što su agenti napravili (ishodi, plan, lekcije, test, ocene, izveštaj); klik otvara sadržaj.

Svako pokretanje (i iz `main.py`) se snima u `output/events_<vreme>.json`, pa se kasnije može pustiti
kao snimak (padajuća lista gore desno) ili direktno linkom: `http://127.0.0.1:8000/?replay=events_<vreme>.json&speed=2`.
Za prezentaciju je najbolje unapred napraviti pokretanje sa LLM-om i onda pustiti snimak.

**Kako je napravljena:**
- **backend** = `app.py`, **FastAPI** server (pokreće ga **uvicorn**). Pokreće simulaciju u pozadini i
  daje stranici događaje. Automatska dokumentacija API-ja: http://127.0.0.1:8000/docs
- **frontend** = folder `frontend/`, **React** aplikacija napravljena alatom **Vite** (opis fajlova u `frontend/README.md`).

**Razvojni režim** (kad menjaš stranicu, izmene se vide odmah, bez `npm run build`), dva terminala:
```powershell
python app.py --no-browser        # terminal 1, folder prototype
cd frontend; npm run dev          # terminal 2 -> otvori http://localhost:5173
```

## Dva režima rada
| Režim | Kako | Šta se dešava |
|---|---|---|
| **mock** (podrazumevano) | nema `.env` fajla ili `LLM_ENABLED=false` | svi agenti vraćaju hello world podatke; ne treba internet ni ključ |
| **pravi LLM** | `.env` sa `LLM_ENABLED=true` i API ključem | ključni agenti (označeni `# KLJUCNI (LLM)` u configu) pozivaju model |

Uključivanje LLM-a:
1. Napravi besplatan API ključ na https://aistudio.google.com (Get API key).
2. Kopiraj `.env.example` u novi fajl `.env`.
3. U `.env` stavi `LLM_ENABLED=true` i nalepi ključ u `LLM_API_KEY=`.
4. `python main.py`

`.env` se NE šalje na GitHub (nalazi se u `.gitignore`).

## Eksterni agent (HTTP)
1. U drugom terminalu: `python external_agent/server.py`
2. U `config/agents.yaml` kod `answer_grader` promeni `type: local` u `type: remote_http`
3. U prvom terminalu: `python main.py`

## Struktura
| Folder / fajl | Šta je to (iz arhitekture) |
|---|---|
| `config/course.yaml` | **ulaz**: kurs koji se simulira (tema, ciljna grupa, profili učenika) |
| `config/agents.yaml` | Agent Registry – spisak agenata, faza, korak, kako se pozivaju |
| `engine/registry.py` | učitava i proverava registar, traženje po sposobnosti |
| `engine/invoker.py` | Agent Invoker / Adapter – poziva lokalnog ili HTTP agenta, meri vreme, hvata greške |
| `engine/llm.py` | jedno mesto za pozive jezičkog modela (mock ili pravi) |
| `engine/state.py` | zajedničko stanje (State) |
| `engine/orchestrator.py` | glavni orkestrator (LangGraph): faze sekvencijalno, korak paralelno, **petlja unutar faze**, povratna sprega |
| `engine/activities.py` | **aktivnosti** – čvorovi grafa koji nisu agenti (učenici slušaju deo lekcije, rade test) |
| `engine/events.py` | događaji simulacije (za vizualizaciju i snimke) |
| `engine/simulation.py` | jedno pokretanje simulacije (koriste ga `main.py` i `app.py`) |
| `agents/students/base.py` | **generički interfejs učenika**: `knowledge()`, `receive(deo)`, `take_test(pitanja)` |
| `agents/students/simple_student.py` | grubo simulirani učenik: memorija + random usvajanje |
| `app.py` | backend vizuelne platforme (FastAPI) |
| `frontend/` | frontend vizuelne platforme (React + Vite) |
| `agents/<faza>/<agent>.py` | jedan fajl = jedan agent, svaki ima funkciju `run(data)` |
| `external_agent/server.py` | primer eksternog agenta preko HTTP API-ja |
| `output/` | evidencija svakog pokretanja (JSON) + graf znanja (`.ttl`, `.trig`, crtež `.md`) |
| `output/materijali_<vreme>/` | čitljivi materijali: `kurikulum.md`, `lekcije.md`, `zadaci.md` (agent `formatting_export`), `test.md`, `izvestaj.md` (agent `final_report`) |
| `knowledge/` | ontologija, pravila za agente, SPARQL pravila i primeri upita |
| `engine/knowledge_graph.py` | zajednički graf znanja (rdflib): upis uz proveru pravila, SPARQL, čuvanje |
| `kg_query.py` | SPARQL upiti nad sačuvanim grafom |
| `agents/graph_context.py` | zajednički SPARQL upiti kojima agenti čitaju graf umesto teksta |

## Ključni agenti (pravi LLM)
| Faza | Agenti |
|---|---|
| 1 – kurikulum | `learning_outcomes`, `curriculum_structure` |
| 2 – nastavni materijali | `lesson_generator`, `exercise_generator` |
| 3 – nastava | `teacher` (jedan poziv: deli lekcije na delove) |
| 4 – testovi | `test_generator`, aktivnost `test_taking` (svaki učenik jedan poziv), `answer_grader` |

Ostali agenti su i dalje hello world. Uzor za pretvaranje agenta u pravog:
`agents/phase1_curriculum/learning_outcomes.py`.

## Pravila redosleda
- Faze idu redom kako su navedene u `phases`.
- Unutar faze agenti idu po broju `step`.
- Isti `step` u istoj fazi = rade **paralelno**.
- Korak N+1 čeka da se završe **svi** agenti iz koraka N.
- Ako `feedback_manager` vrati `needs_rework: true`, tok se vraća na fazu `return_to`
  (najviše `max_feedback_iterations` puta).

- **Petlja unutar faze** (`loop` kod faze): koraci `from_step`..`to_step` se ponavljaju dok rezultat
  agenta iz `until` nema to polje `true`. Faza 3: `teacher` (korak 3) → aktivnost `learning` (korak 4) →
  ponovo `teacher` … dok `teacher.done` nije `true`.

## Agenti, učenici i aktivnosti (config/agents.yaml)
| Sekcija | Šta je | Primer |
|---|---|---|
| `agents` | agent = fajl sa `run(data)` | `teacher`, `test_generator` |
| `students` | simulirani učenik = klasa koja ispunjava `agents/students/base.py` | `student_beginner` |
| `activities` | **nije agent**: postojeći učenici (`participants`) rade akciju (`action`) nad izlazom postojećeg agenta (`resource`) | `test_taking`: učenici rade test koji je napravio `test_generator` |

Rezultat aktivnosti se upisuje pod njenim id-jem, pa ga sledeći agent dobija kao običan ulaz
(`answer_grader` ima `requires: [test_generator, test_taking]`).

**Drugi simulirani učenik**: napravi klasu koja nasleđuje `StudentInterface`
(`agents/students/base.py`) i u sekciji `students` promeni `class:`. Ništa drugo se ne menja.

**Kako uči naš učenik:** svaki deo lekcije usvaja sa verovatnoćom `learning_probability` iz
`config/course.yaml` (početnik 0.45, srednji 0.7, napredni 0.9). Na testu kod pogleda memoriju:
usvojio sve delove za ishod → tačno, deo → delimično, ništa → ne zna / pogrešno.
`random_seed` u `course.yaml` čini rezultate ponovljivim (`null` = svaki put drugačije).

## Kako izgleda lekcija (Faza 2)
- `config/course.yaml` ima **studiju slučaja** (`case_study`) i **ograničenja** (`constraints`).
  Lekcije, zadaci i test koriste isti primer. Ako se iz platforme zada druga tema, ova dva polja
  se ne koriste i agenti sami biraju primer iz te oblasti.
- `lesson_generator`: svaka lekcija ima delove uvod → objašnjenje → rešen primer → kod → česte greške → rezime → provera.
- `example_generator`: zbirka rešenih primera izdvojena iz lekcija (bez LLM-a).
- `exercise_generator`: 4–6 zadataka različitih vrsta (pojmovni, računski, programski, pronađi grešku) sa podacima i rešenjem.
- `exercise_solver`: nezavisno rešava zadatke i javlja ako se ne slaže sa autorom.
- `material_quality_check`: proverava pravila (svi delovi lekcije, svaki ishod ima zadatak, zadaci imaju podatke…);
  primedbe idu u doradu preko optimizatora.
- `teacher`: delove časa pravi iz delova lekcije, jedan poziv modela po lekciji.

## Isključivanje agenta
Dodaj `enabled: false` u blok agenta – engine ga preskače, a ostali rade dalje.
