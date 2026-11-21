# Beleške i ideje – graf znanja i RAG u multiagentskom sistemu

Jedno mesto za zaključke, ideje, otvorena pitanja i sugestije asistenta.
Dnevnik (`istrazivacki-dnevnik.md`) beleži šta je urađeno, a ovde je šta mislim, šta ne znam i šta treba istražiti.

---

## 1. Sugestije asistenta

### Termin 2 – 09.11.2026.

- Za početak povezati svoju zamisao sa **primitivnim agentima**: ne moraju još ništa pametno da rade, ali treba da **koriste strukturu grafa** i budu povezani sa tehnologijama sa kojima radim.
- Kasnije, kroz lanac dizajn kurikuluma → generisanje materijala → rad sa materijalima, biće potrebni **materijali kao uzorak**.
- Te materijale će koristiti agenti, pa se mogu predstaviti kao **zaseban RAG graf** koji agenti dele između sebe.
- Nadovezati se na postojeću arhitekturu i proveriti **da li ima smisla da ga koriste svi agenti**.
- Graf znanja može da definiše:
  - **pravila** koja agenti moraju da poštuju,
  - **zajedničku memoriju** koju agenti međusobno koriste.
- Agent drugom agentu ne treba da šalje plain tekst, nego **strukturu iz grafa**.
- Za početak uraditi primitivno, pa se kasnije nadovezivati.

### Termin 3 – 16.11.2026.

Pitanja:
- Šta je **izlaz** sistema zapravo?
- Šta **predstavlja graf** – izlaz iz sve 4 faze, koji svi dele?
- Da li koristim graf kao **ulaz u sledeću fazu**?
- **Za šta će se graf koristiti?** Agent treba da dobije ulaz, verovatno od prethodne faze – zašto plain tekst, ako može automatski da gleda u graf?
- **Ograničenja modela** – voditi računa koji LLM koristiti, jer ima jako puno agenata.

Zadatak:
- Razmisliti kako koristiti graf tako da **ima svrhu i smisao** (npr. kao ulaz), a ne ubacivati ga na silu.

O modelima:
- Ako bude problema sa modelima: **pretplata na Claude** i korišćenje preko **sesije** umesto API-ja (API je skup).
- Napraviti malu skriptu koja poziva model kroz sesiju.
- Koristiti jači model, npr. **Claude Haiku** – troši malo sesije, verovatno bi sve moglo da se odradi bez trošenja sesije ni blizu limita.

---

## 2. Odgovori na pitanja iz termina 3

### 2.1 Šta je izlaz sistema?

| Izlaz | Za koga | Šta je |
|---|---|---|
| `kurikulum.md`, `lekcije.md`, `zadaci.md`, `test.md`, `izvestaj.md` | za ljude | gotovi nastavni materijali |
| `graf_*.ttl` (Protégé), `graf_*.trig`, `graf_*.md` | za mašine (agente, pravila, upite) | struktura celog kursa kao RDF trojke |

### 2.2 Šta predstavlja graf?

Graf je **jedan povezan model celog kursa** koji pune sve 4 faze:

| Faza | Šta upisuje u graf |
|---|---|
| 1 – dizajn kurikuluma | šta je planirano: kompetencije, ishodi, jedinice, teme, preduslovi |
| 2 – nastavni sadržaji | šta je napravljeno: lekcije i zadaci, vezani za jedinice i ishode |
| 3 – realizacija nastave | ko uči: učenici i njihov nivo znanja |
| 4 – evaluacija | šta se desilo: test, pitanja, odgovori i poeni |

Iz grafa se prati ceo lanac, što iz običnog teksta nije moguće:
**ishod → jedinica → lekcija → zadatak → pitanje → odgovor učenika → poeni**

Dodatno:
- svaki agent piše u **svoj imenovani graf**, pa se zna ko je šta upisao;
- svaki upis se **proverava** prema ontologiji i pravilima za agente (`agenti.ttl`).

### 2.3 Da li koristim graf kao ulaz u sledeću fazu?

**Da.** Agenti ne dobijaju strukturu kao običan tekst, nego je čitaju **SPARQL upitima** iz grafa:

| Agent | Šta čita iz grafa |
|---|---|
| `curriculum_structure` (faza 1) | ishode sa kompetencijama i pokazateljima |
| `lesson_generator` (faza 2) | plan: jedinica → teme → preduslovi → ishodi |
| `exercise_generator` (faza 2) | ishode i lekcije sa njihovim ishodima |
| `teacher` (faza 3) | lekcije i ishode koje pokrivaju |
| `knowledge_state` (faza 3) | teme po jedinicama |
| `test_generator` (faza 4) | ishode i lekcije |
| `answer_grader` (faza 4) | pitanja, očekivane odgovore i odgovore učenika |
| `objective_achievement` (faza 4) | uspeh po ishodu (računa se SPARQL upitom) |

Šta nije u grafu:
- **dugački tekstovi** (sadržaj lekcija, rešenja) – graf koristim za strukturu i veze, a ne za duge sadržaje;
- **detalji faze 3** – delovi časa i koji je učenik usvojio koji deo; za sada je upisan samo ukupni nivo znanja.

### 2.4 Za šta se graf koristi?

1. **Ulaz za agente** – struktura umesto teksta (tabela iznad).
2. **Kontrola kvaliteta i povratna sprega** – 8 SPARQL pravila proverava graf, npr.:
   - svaki ishod mora biti proveren pitanjem na testu,
   - svaki ishod mora imati zadatak,
   - ishod je slabo ostvaren ako učenici osvoje manje od 50% poena.

   Svako pravilo zna **koji agent je odgovoran**, pa povratna sprega zna **u koju fazu da vrati tok**.
3. **Sledljivost** – zna se ko je šta upisao i u kom prolazu (verzija).

### 2.5 Ograničenja modela

- Od ~36 agenata samo **~10 koristi LLM**; ostali rade po pravilima, preko SPARQL upita ili formatiranjem.
- Jedno pokretanje ≈ **12 LLM poziva** (sa doradom ≈ 20).
- Trenutno: Groq, besplatni nivo – limit od **8.000 tokena po minutu**, već dostignut kod dužih lekcija.
- **Graf pomaže:** agentu se daje samo deo grafa koji mu treba (npr. ishodi i teme jedne jedinice), a ne ceo tekst → manje tokena → jeftiniji ili manji model.
- Svi LLM pozivi idu kroz **jedno mesto** (`engine/llm.py`), pa se model menja na jednom mestu.

---

## 3. Ideje – kako graf da ima svrhu, a ne da bude na silu

### A) Preduslovi utiču na učenje
Graf već ima veze „tema B ima preduslov temu A“. Ako učenik nije usvojio A, teže usvaja B (manja verovatnoća).
Graf tako direktno utiče na simulaciju – realno je: ko nije naučio osnove, teže uči nastavak.

### B) Ciljana dorada
Kad pravilo „ishod slabo ostvaren“ nađe slab ishod, iz grafa se nađe koja lekcija i koji delovi časa ga pokrivaju,
pa se dorađuje samo to, a ne ceo kurs. Manje posla i manje LLM poziva.

### C) Objašnjenje rezultata iz grafa
Upisati koji je deo časa učenik usvojio. Jedan SPARQL upit tada odgovara:
„Zašto je početnik pao pitanje T3?“ → nije usvojio delove S4 i S5, koji pokrivaju ishod O3.

### D) Različit model za različite agente
Jači model za lekcije i nastavnika, slabiji i jeftiniji za jednostavne zadatke. Graf daje kratak, ciljan ulaz.

### E) RAG graf nad uzorcima materijala *(sugestija asistenta, termin 2)*
Uzorci pravih nastavnih materijala (npr. postojeće lekcije, zadaci) predstavljeni kao poseban graf.
Agenti za lekcije i zadatke iz njega uzimaju relevantne delove (RAG) umesto da sve izmišljaju sami.
Pitanje: da li ga koriste svi agenti ili samo oni iz faze 2?

### F) Claude Haiku preko pretplate *(sugestija asistenta, termin 3)*
Ako besplatni nivo (Groq) ne bude dovoljan: Claude pretplata i mala skripta koja poziva model kroz sesiju,
umesto plaćanja API-ja po pozivu. Haiku je jači od trenutnog modela, a troši malo sesije.
U kodu bi se menjao samo `engine/llm.py`.

---
## Rezime

> Graf je zajednička memorija svih agenata kroz sve četiri faze. Svaki agent upisuje rezultate kao trojke,
> a engine proverava da li upis poštuje ontologiju i pravila za tog agenta.
>
> Izlaz sistema su materijali za ljude i graf za mašine. Graf povezuje ceo lanac:
> ishod, jedinicu, lekciju, zadatak, pitanje, odgovor učenika i poene.
>
> Graf već koristim kao ulaz – agenti iz kasnijih faza čitaju strukturu SPARQL upitima,
> a ne kao tekst. Dugačke tekstove lekcija šaljem kao tekst, jer graf koristim za strukturu.
>
> Druga svrha je kontrola kvaliteta: 8 SPARQL pravila, i svako zna koji agent je odgovoran,
> pa povratna sprega zna u koju fazu da vrati tok.
>
> Samo desetak agenata zove LLM. Već sam udarila u limit tokena, a graf tu pomaže
> jer agentu mogu da dam samo deo grafa koji mu treba.
>
> Da graf ne bi bio na silu, predlažem da preduslovi iz grafa utiču na to koliko lako učenik usvaja temu
> i da dorada bude ciljana.

