# Beleške i ideje – graf znanja i RAG u multiagentskom sistemu

Jedno mesto za zaključke, ideje, otvorena pitanja, sugestije asistenta i literaturu.
Dnevnik (`istrazivacki-dnevnik.md`) beleži šta je urađeno, a ovde je šta mislim, šta ne znam i šta treba istražiti.

---

## 1. Sugestije asistenta

### Termin 2 - 09.11.2026.

- Za početak povezati svoju zamisao sa **primitivnim agentima**: ne moraju još ništa pametno da rade, ali treba da **koriste strukturu grafa** i budu povezani sa tehnologijama sa kojima radim.
- Kasnije, kroz lanac dizajn kurikuluma → generisanje materijala → rad sa materijalima, biće potrebni **materijali kao uzorak**.
- Te materijale će koristiti agenti, pa se mogu predstaviti kao **zaseban RAG graf** koji agenti dele između sebe.
- Nadovezati se na postojeću arhitekturu i proveriti **da li ima smisla da ga koriste svi agenti**.
- Graf znanja može da definiše:
  - **pravila** koja agenti moraju da poštuju,
  - **zajedničku memoriju** koju agenti međusobno koriste.
- Agent drugom agentu ne treba da šalje plain tekst, nego **strukturu iz grafa**.
- Za početak uraditi primitivno, pa se kasnije nadovezivati.

### Termin 3 - 16.11.2026.

- Šta je **izlaz** sistema zapravo?
- Šta **predstavlja graf** – izlaz iz sve 4 faze, koji svi dele?
- Da li koristim graf kao **ulaz u sledeću fazu**?
- **Za šta će se graf koristiti?** Agent treba da dobije ulaz, verovatno od prethodne faze – zašto plain tekst, ako može automatski da gleda u graf?
- **Ograničenja modela** – voditi računa koji LLM koristiti, jer ima jako puno agenata.

Zadaci:
- Razmisliti kako koristiti graf tako da **ima svrhu i smisao** (npr. kao ulaz), a ne ubacivati ga na silu.

O modelima:
- Ako bude problema sa modelima: **pretplata na Claude** i korišćenje preko **sesije** umesto API-ja (API je skup).
- Napraviti malu skriptu koja poziva model kroz sesiju.
- Koristiti jači model, npr. **Claude Haiku** – troši malo sesije, verovatno bi sve moglo da se odradi bez trošenja sesije ni blizu limita.

---

## 2. Trenutno stanje (moji odgovori na pitanja iz termina 3)

**Izlaz sistema:**
- za ljude: `kurikulum.md`, `lekcije.md`, `zadaci.md`, `test.md`, `izvestaj.md`
- za mašine: graf znanja (`graf_*.ttl` za Protégé, `graf_*.trig` po agentima, `graf_*.md` crtež)

**Šta je graf:** jedan povezan model celog kursa koji pune sve 4 faze:
- faza 1 – kompetencije, ishodi, jedinice, teme, preduslovi (šta je planirano)
- faza 2 – lekcije i zadaci vezani za jedinice i ishode (šta je napravljeno)
- faza 3 – učenici i nivo znanja (ko uči)
- faza 4 – test, pitanja, odgovori, poeni (šta se desilo)

Lanac koji se može pratiti: ishod → jedinica → lekcija → zadatak → pitanje → odgovor učenika → poeni.

**Graf kao ulaz:** da – agenti strukturu čitaju SPARQL upitima, a ne kao tekst
(plan kursa, ishodi, lekcije sa ishodima, pitanja i odgovori za ocenjivanje, uspeh po ishodu).
Dugački tekstovi (sadržaj lekcija, rešenja) i dalje idu kao tekst – graf je za strukturu i veze.

**Svrhe grafa sada:**
1. ulaz za agente (struktura umesto teksta)
2. kontrola kvaliteta – 8 SPARQL pravila; svako zna odgovornog agenta, pa povratna sprega zna u koju fazu da vrati tok
3. sledljivost – svaki agent piše u svoj imenovani graf, uz verziju (prolaz)

**Ograničenja modela:**
- od ~36 agenata samo ~10 koristi LLM; ostali rade po pravilima ili preko SPARQL upita
- jedno pokretanje ≈ 12 LLM poziva (sa doradom ≈ 20)
- trenutno: Groq, besplatni nivo – limit 8.000 tokena po minutu, već dostignut kod dugih lekcija
- graf može da smanji zahteve: agentu se daje samo deo grafa koji mu treba
- svi LLM pozivi idu kroz jedno mesto (`engine/llm.py`), pa se model menja na jednom mestu


---

## 3. Ideje (da graf ima svrhu, a ne da bude na silu)

### A) Preduslovi utiču na učenje
Graf već ima veze „tema B ima preduslov temu A“. Ako učenik nije usvojio A, teže usvaja B (manja verovatnoća).
Graf tada direktno utiče na simulaciju. Realno: ko nije naučio osnove, teže uči nastavak.

### B) Ciljana dorada
Kad pravilo „ishod slabo ostvaren“ nađe slab ishod, iz grafa se nađe koja lekcija i koji delovi časa ga pokrivaju,
pa se dorađuje samo to, a ne ceo kurs. Manje posla i manje LLM poziva.

### C) Objašnjenje rezultata iz grafa
Upisati koji je deo časa učenik usvojio. Jedan SPARQL upit tada odgovara na pitanje
„zašto je učenik pao pitanje T3?“ → nije usvojio delove koji pokrivaju ishod koji T3 proverava.

### D) Različit model za različite agente
Jači model za lekcije i nastavnika, slabiji i jeftiniji za jednostavne zadatke. Graf daje kratak, ciljan ulaz.

### E) RAG graf nad uzorcima materijala (sugestija asistenta, termin 2)
Uzorci pravih nastavnih materijala (npr. postojeće lekcije, zadaci) predstavljeni kao poseban graf.
Agenti za lekcije i zadatke iz njega uzimaju relevantne delove (RAG) umesto da sve izmišljaju sami.
Pitanje: da li ga koriste svi agenti ili samo oni iz faze 2?

### F) Claude Haiku preko pretplate (sugestija asistenta, termin 3)
Ako besplatni nivo (Groq) ne bude dovoljan: Claude pretplata i mala skripta koja poziva model kroz sesiju,
umesto plaćanja API-ja po pozivu. Haiku je jači od trenutnog modela, a troši malo sesije.
U kodu bi se menjao samo `engine/llm.py`.


---
