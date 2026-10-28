Koji su zaključci koje sam do sad izvela? / Sta sam do sada saznala?


# Sumarizacija dosadašnjeg istraživanja

## 1. Cilj istraživanja

Istraživanje je usmereno na primenu multiagentskih sistema zasnovanih na LLM modelima za simulaciju celokupnog nastavnog procesa.

Cilj je razviti modularan sistem u kojem specijalizovani AI agenti sarađuju tokom različitih faza nastave, pri čemu rezultati jedne faze predstavljaju ulaz za narednu.

## 2. Organizacija nastavnog procesa

Na osnovu analize nastavnog procesa i ADDIE modela, izdvojene su četiri osnovne faze:

1. **Dizajn kurikuluma** – definisanje nastavnih ciljeva, tema i plana nastave.
2. **Kreiranje nastavnih sadržaja** – generisanje lekcija, primera i zadataka.
3. **Izvođenje nastave** – simulacija interakcije nastavnika i učenika.
4. **Evaluacija** – provera znanja, analiza rezultata i unapređenje prethodnih faza.

Svaka faza može obuhvatiti više specijalizovanih agenata.

## 3. Najvažnija saznanja iz literature

- **EduPlanner** – pokazuje pristup generisanju, evaluaciji i optimizaciji nastavnog dizajna pomoću više agenata.
- **SimClass** – pruža ideje za simulaciju nastave kroz interakciju agenata nastavnika i učenika.
- **AgentSchool** – ukazuje na značaj modelovanja znanja i ponašanja simuliranih učenika.
- **ChatDev** – predstavlja koristan primer raspodele uloga i koordinacije specijalizovanih agenata.
- **Generative Agents** – uvodi koncepte memorije, refleksije i planiranja na osnovu prethodnih iskustava.
- **Constructive Alignment** – naglašava potrebu za usklađivanjem nastavnih ciljeva, aktivnosti i evaluacije.

## 4. Ideje za arhitekturu sistema

Na osnovu dosadašnjeg istraživanja i smernica profesora izdvojene su sledeće ideje:

- Razviti **generički multiagentski engine** za upravljanje agentima.
- Koristiti centralni orkestrator za koordinaciju četiri faze nastavnog procesa.
- Omogućiti registraciju agenata i njihovo sekvencijalno ili paralelno izvršavanje.
- Definisati zajednički interfejs za razmenu strukturisanih podataka.
- Predvideti mogućnost povezivanja eksternih agenata preko API-ja.
- Za početak implementirati jednostavne LLM agente, a zatim postepeno unapređivati njihove funkcionalnosti.

## 5. Evaluacija i povratna sprega

Jedno od važnijih saznanja jeste da evaluacija ne treba samo da proverava znanje učenika, već i kvalitet prethodnih faza.

Na primer, ukoliko test proverava nastavni cilj koji nije adekvatno obrađen u nastavnom materijalu, sistem treba da prepozna tu neusaglašenost i predloži odgovarajuću korekciju.

## 6. Dosadašnji zaključci

- Multiagentski pristup omogućava podelu složenog nastavnog procesa na manje, specijalizovane zadatke.
- Važno je definisati odgovornosti, ulaze i izlaze svakog agenta.
- Postojeća istraživanja pružaju osnovu za pojedinačne faze i mehanizme koordinacije.
- Fokus projekta treba da bude na **pokrivanju sve četiri faze**, a ne na detaljnom usavršavanju jednog agenta.
- Modularna arhitektura omogućila bi kasnije proširivanje sistema i zamenu pojedinačnih agenata.

## 7. Dalji koraci

- Detaljnije definisati agente za svaku fazu.
- Istražiti postojeće framework-e za multiagentske sisteme.
- Definisati arhitekturu engine-a i način komunikacije.
- Izabrati tehnologije i oblast za studiju slučaja.

---

*Dokument predstavlja sažetak dosadašnjih saznanja i početnih projektnih ideja. Dopunjavaće se tokom daljeg istraživanja i razvoja sistema.*
