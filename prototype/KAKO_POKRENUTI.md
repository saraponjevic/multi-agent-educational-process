# Kako pokrenuti prototip

## Prvi put (instalacija)
```powershell
cd prototype
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Svaki sledeći put
```powershell
cd prototype
.venv\Scripts\activate
python main.py                    # pokreni ceo nastavni proces
python main.py --list             # samo prikaži registrovane agente
python main.py --graph            # sačuvaj dijagram grafa u docs/graph.md
python main.py --course "Osnove SQL upita"   # druga tema (inače se čita config/course.yaml)
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
| `engine/orchestrator.py` | glavni orkestrator (LangGraph): faze sekvencijalno, korak paralelno, povratna sprega |
| `agents/<faza>/<agent>.py` | jedan fajl = jedan agent, svaki ima funkciju `run(data)` |
| `external_agent/server.py` | primer eksternog agenta preko HTTP API-ja |
| `output/` | evidencija svakog pokretanja (JSON) |

## Ključni agenti (pravi LLM)
| Faza | Agenti |
|---|---|
| 1 – kurikulum | `learning_outcomes`, `curriculum_structure` |
| 2 – nastavni materijali | `lesson_generator`, `exercise_generator` |
| 3 – profesor i student | `teacher`, `student` (3 nivoa) |
| 4 – testovi | `test_generator`, `student` radi test (3 nivoa), `answer_grader` |

Ostali agenti su i dalje hello world. Uzor za pretvaranje agenta u pravog:
`agents/phase1_curriculum/learning_outcomes.py`.

## Pravila redosleda
- Faze idu redom kako su navedene u `phases`.
- Unutar faze agenti idu po broju `step`.
- Isti `step` u istoj fazi = rade **paralelno**.
- Korak N+1 čeka da se završe **svi** agenti iz koraka N.
- Ako `feedback_manager` vrati `needs_rework: true`, tok se vraća na fazu `return_to`
  (najviše `max_feedback_iterations` puta).

## Isključivanje agenta
Dodaj `enabled: false` u blok agenta – engine ga preskače, a ostali rade dalje.
