# Osnovni pojmovi

## 1. Uvod

Ovaj dokument predstavlja pregled osnovnih pojmova relevantnih za istraživanje i razvoj multiagentskog sistema za simulaciju nastavnog procesa.

Obuhvaćeni su koncepti iz oblasti obrazovanja, veštačke inteligencije, multiagentskih sistema i softverske arhitekture.

Cilj je uspostavljanje teorijske osnove za identifikaciju aktivnosti nastavnog procesa koje se mogu automatizovati pomoću specijalizovanih AI agenata, kao i za projektovanje sistema koji omogućava njihovu koordinaciju.

---

## 2. Nastavni proces i obrazovni modeli

### 2.1. Nastavni proces

Nastavni proces predstavlja organizovan skup aktivnosti usmerenih na ostvarivanje definisanih obrazovnih ciljeva. Obuhvata planiranje nastave, pripremu nastavnih sadržaja, realizaciju nastavnih aktivnosti i evaluaciju postignutih rezultata.

**Povezanost sa projektom:** Nastavni proces predstavlja osnovu sistema koji se modeluje kroz četiri međusobno povezane faze.

### 2.2. Kurikulum

Kurikulum predstavlja strukturisan obrazovni plan koji definiše šta učenici treba da nauče, koje nastavne teme će se obrađivati, koje kompetencije treba razviti i kako će se proveravati ostvareni rezultati.

**Povezanost sa projektom:** Agent za dizajn kurikuluma generiše nastavni plan koji predstavlja ulaz za naredne faze sistema.

### 2.3. Nastavni ciljevi i ishodi učenja

Nastavni ciljevi opisuju nameravane rezultate obrazovnog procesa, dok ishodi učenja preciziraju šta učenik treba da zna, razume ili bude sposoban da uradi nakon završetka određene aktivnosti.

Ishodi učenja treba da budu jasno definisani i merljivi.

**Primer:** Učenik će moći da objasni razliku između klasifikacije i regresije i prepozna odgovarajući pristup za zadati problem.

**Povezanost sa projektom:** Agent za definisanje nastavnih ciljeva formira ciljeve sa jedinstvenim identifikatorima koji se kasnije koriste za generisanje materijala i evaluaciju.

### 2.4. ADDIE model

ADDIE predstavlja model sistematskog projektovanja nastave koji obuhvata pet faza:

1. Analysis – analiza obrazovnih potreba.
2. Design – projektovanje nastavnog procesa.
3. Development – razvoj nastavnih materijala.
4. Implementation – realizacija nastave.
5. Evaluation – evaluacija rezultata i unapređenje.

**Povezanost sa projektom:** ADDIE predstavlja teorijsku osnovu za organizaciju nastavnog procesa. U projektu su aktivnosti ovog modela grupisane u četiri šire faze: dizajn kurikuluma, kreiranje nastavnih sadržaja, realizacija nastave i evaluacija.

**Izvor:** Branch (2009), *Instructional Design: The ADDIE Approach*.

### 2.5. Bloomova taksonomija

Bloomova taksonomija predstavlja okvir za klasifikaciju obrazovnih ciljeva prema nivoima kognitivne složenosti.

Revidirana taksonomija obuhvata šest nivoa: pamćenje, razumevanje, primenu, analizu, evaluaciju i kreiranje.

**Povezanost sa projektom:** Može se koristiti za definisanje nastavnih ciljeva i generisanje zadataka različitih nivoa složenosti.

**Izvor:** Anderson & Krathwohl (2001), *A Taxonomy for Learning, Teaching, and Assessing*.

### 2.6. Konstruktivno usklađivanje (Constructive Alignment)

Konstruktivno usklađivanje predstavlja princip prema kojem nastavni ciljevi, nastavne aktivnosti i metode evaluacije treba da budu međusobno povezani.

**Povezanost sa projektom:** Agent za proveru usklađenosti može analizirati da li generisani nastavni materijali i testovi odgovaraju ciljevima definisanim u kurikulumu.

**Izvor:** Biggs (1996), *Enhancing Teaching through Constructive Alignment*.

### 2.7. Nastavni materijali

Nastavni materijali predstavljaju resurse koji se koriste za objašnjavanje, uvežbavanje i usvajanje nastavnog sadržaja. Mogu obuhvatati lekcije, prezentacije, primere, zadatke i testove.

**Povezanost sa projektom:** Specijalizovani agenti generišu različite vrste nastavnih materijala na osnovu definisanih ciljeva učenja.

### 2.8. Instrukciona strategija

Instrukciona strategija predstavlja planirani način organizacije i izvođenja nastave radi ostvarivanja obrazovnih ciljeva.

Može obuhvatati objašnjavanje, demonstraciju, diskusiju, praktično vežbanje i problemsko učenje.

**Povezanost sa projektom:** Agent za instrukcionu strategiju određuje odgovarajući način podučavanja na osnovu ciljeva i karakteristika učenika.

### 2.9. Evaluacija nastavnog procesa

Evaluacija predstavlja sistematsku procenu ostvarenosti nastavnih ciljeva, kvaliteta nastavnih materijala i efikasnosti obrazovnog procesa.

Može obuhvatati formativnu evaluaciju tokom učenja i sumativnu evaluaciju nakon završetka određene nastavne celine.

**Povezanost sa projektom:** Agenti za evaluaciju analiziraju rezultate simuliranih učenika, proveravaju usklađenost materijala sa ciljevima i predlažu unapređenja.

### 2.10. Povratna sprega (Feedback Loop)

Povratna sprega predstavlja mehanizam kojim se rezultati određene aktivnosti koriste za korekciju prethodnih odluka ili procesa.

**Povezanost sa projektom:** Ako evaluacija pokaže da određeni nastavni cilj nije adekvatno obrađen, sistem može vratiti zahtev agentu za generisanje materijala radi dopune sadržaja.

---

## 3. Veštačka inteligencija i veliki jezički modeli

### 3.1. Veštačka inteligencija (AI)

Veštačka inteligencija predstavlja oblast računarstva koja se bavi razvojem sistema sposobnih da izvršavaju zadatke koji zahtevaju sposobnosti poput zaključivanja, planiranja, prepoznavanja obrazaca i obrade jezika.

**Povezanost sa projektom:** Veštačka inteligencija omogućava automatizaciju pojedinih aktivnosti nastavnog procesa.

### 3.2. Veliki jezički modeli (LLM)

Veliki jezički modeli predstavljaju modele mašinskog učenja, najčešće zasnovane na Transformer arhitekturi, trenirane na velikim količinama tekstualnih podataka.

Mogu se koristiti za razumevanje instrukcija, generisanje teksta, analizu informacija i rešavanje različitih zadataka.

**Povezanost sa projektom:** LLM modeli mogu predstavljati osnovu za implementaciju agenata koji generišu kurikulume, lekcije, zadatke i povratne informacije.

### 3.3. Prompt

Prompt predstavlja instrukciju ili skup informacija koji se prosleđuje jezičkom modelu kako bi se definisao zadatak i očekivani rezultat.

**Primer:** Generiši nastavnu lekciju o klasifikaciji namenjenu početnicima, na osnovu definisanih ciljeva učenja.

**Povezanost sa projektom:** Početne verzije agenata mogu se realizovati korišćenjem specijalizovanih promptova koji određuju njihovu ulogu i odgovornosti.

### 3.4. AI agent

AI agent predstavlja softversku komponentu koja prima informacije iz okruženja, obrađuje ih i izvršava aktivnosti radi ostvarivanja određenog cilja.

LLM agent može koristiti jezički model za donošenje odluka, generisanje rezultata i izbor narednih aktivnosti.

**Povezanost sa projektom:** Svaki agent ima definisan zadatak, ulazne podatke i očekivani izlaz. Na primer, agent za generisanje zadataka dobija nastavne ciljeve i proizvodi zadatke odgovarajuće težine.

### 3.5. Generisanje nastavnog sadržaja

Automatsko generisanje sadržaja predstavlja proces kreiranja novih tekstova, primera, zadataka i drugih materijala pomoću generativnih AI modela.

**Povezanost sa projektom:** U drugoj fazi sistema LLM agenti generišu nastavne sadržaje na osnovu prethodno definisanog kurikuluma.

### 3.6. Halucinacije LLM modela

Halucinacije predstavljaju situacije u kojima jezički model generiše netačne, izmišljene ili nepouzdane informacije, često predstavljene kao tačne.

**Povezanost sa projektom:** Potrebno je predvideti proveru tačnosti generisanih nastavnih sadržaja, posebno teorijskih objašnjenja, zadataka i referentnih rešenja.

---

## 4. Multiagentski sistemi

### 4.1. Multiagentski sistem (MAS)

Multiagentski sistem predstavlja sistem sastavljen od više agenata koji međusobno komuniciraju, sarađuju ili koordiniraju aktivnosti radi ostvarivanja pojedinačnih ili zajedničkih ciljeva.

**Povezanost sa projektom:** Celokupan nastavni proces realizuje se kroz saradnju više specijalizovanih agenata.

### 4.2. Specijalizacija agenata

Specijalizacija agenata podrazumeva dodeljivanje jasno definisanih odgovornosti pojedinačnim agentima.

**Primer:** Jedan agent generiše lekcije, drugi kreira zadatke, a treći proverava njihovu tačnost.

**Povezanost sa projektom:** Omogućava nezavisno razvijanje i unapređenje agenata za pojedinačne nastavne aktivnosti.

### 4.3. Koordinacija agenata

Koordinacija predstavlja usklađivanje aktivnosti više agenata kako bi njihovi rezultati doprineli ostvarivanju zajedničkog cilja.

**Povezanost sa projektom:** Agenti moraju izvršavati zadatke odgovarajućim redosledom i razmenjivati rezultate kako bi se realizovao kompletan nastavni proces.

### 4.4. Orkestracija agenata

Orkestracija predstavlja centralizovano upravljanje izvršavanjem agenata, njihovim redosledom, zavisnostima i razmenom podataka.

**Povezanost sa projektom:** Centralni orkestrator upravlja fazama nastavnog procesa, dok se unutar pojedinačnih faza može koristiti dodatna orkestracija specijalizovanih agenata.

### 4.5. Komunikacija između agenata

Komunikacija između agenata predstavlja razmenu informacija, zahteva i rezultata korišćenjem definisanih protokola i formata podataka.

**Povezanost sa projektom:** Izlaz jednog agenta predstavlja ulaz drugog agenta. Na primer, agent za generisanje lekcija prima ciljeve koje je prethodno definisao agent za kurikulum.

### 4.6. Memorija agenata

Memorija predstavlja mehanizam za čuvanje i ponovno korišćenje informacija o prethodnim događajima, interakcijama i rezultatima.

**Povezanost sa projektom:** Agenti učenici mogu čuvati informacije o prethodnim odgovorima, savladanim konceptima i identifikovanim greškama.

**Izvor:** Park et al. (2023), *Generative Agents: Interactive Simulacra of Human Behavior*.

### 4.7. Refleksija agenata (Reflection)

Refleksija predstavlja proces analize prethodnih iskustava radi izvođenja novih zaključaka i unapređenja budućih aktivnosti.

**Povezanost sa projektom:** Agent može analizirati rezultate prethodne simulacije i koristiti ih za predlaganje izmena nastavne strategije.

**Izvor:** Park et al. (2023), *Generative Agents*.

### 4.8. Simulirani agent učenik

Simulirani agent učenik predstavlja softverskog agenta koji modeluje određene karakteristike i ponašanja učenika u obrazovnom okruženju.

Može imati definisan nivo predznanja, interesovanja, prethodna iskustva i stanje znanja.

**Povezanost sa projektom:** U trećoj fazi koristi se za simulaciju interakcija sa agentom nastavnikom i praćenje promena u modelovanom znanju.

**Izvori:** *SimClass* (2025), *AgentSchool* (2026).

### 4.9. Agent nastavnik

Agent nastavnik predstavlja agenta zaduženog za izvođenje nastavnih aktivnosti, objašnjavanje gradiva, postavljanje pitanja i pružanje povratnih informacija.

**Povezanost sa projektom:** Koristi pripremljene nastavne materijale i komunicira sa simuliranim učenicima tokom realizacije nastave.

### 4.10. Sekvencijalno i paralelno izvršavanje agenata

Sekvencijalno izvršavanje podrazumeva da se zadaci izvršavaju određenim redosledom, pri čemu naredni agent može zavisiti od rezultata prethodnog.

Paralelno izvršavanje omogućava istovremeno pokretanje nezavisnih agenata.

**Povezanost sa projektom:** Engine treba da omogući definisanje zavisnosti i izbor odgovarajućeg načina izvršavanja agenata.

---

## 5. Softverska arhitektura multiagentskog sistema

### 5.1. Modularna arhitektura

Modularna arhitektura predstavlja organizaciju softverskog sistema u zasebne komponente sa jasno definisanim odgovornostima i interfejsima.

**Povezanost sa projektom:** Svaki agent predstavlja zasebnu komponentu koja se može razvijati, menjati ili zameniti bez potrebe za izmenom celokupnog sistema, pod uslovom da poštuje definisani interfejs.

### 5.2. Multiagentski engine

Multiagentski engine predstavlja softversku infrastrukturu koja omogućava upravljanje agentima, njihovom registracijom, pokretanjem, koordinacijom i razmenom rezultata.

**Povezanost sa projektom:** Planirano je projektovanje generičkog engine-a koji upravlja agentima raspoređenim kroz četiri faze nastavnog procesa.

### 5.3. Registar agenata (Agent Registry)

Registar agenata predstavlja mehanizam za evidentiranje dostupnih agenata i informacija o njihovim mogućnostima.

Može sadržati naziv agenta, njegovu ulogu, podržane zadatke, ulazne i izlazne formate i lokaciju izvršavanja.

**Povezanost sa projektom:** Engine može pronaći i pozvati odgovarajuće agente na osnovu registrovanih sposobnosti.

### 5.4. API (Application Programming Interface)

API predstavlja definisan način komunikacije između softverskih komponenti ili sistema.

**Povezanost sa projektom:** Eksterni agenti mogu biti dostupni putem API-ja, što omogućava njihovo povezivanje sa centralnim engine-om.

### 5.5. JSON (JavaScript Object Notation)

JSON predstavlja tekstualni format za strukturisano predstavljanje i razmenu podataka.

**Povezanost sa projektom:** Može se koristiti za predstavljanje kurikuluma, nastavnih ciljeva, rezultata agenata i evaluacionih izveštaja.

### 5.6. Plugin arhitektura

Plugin arhitektura omogućava proširivanje funkcionalnosti sistema dodavanjem novih komponenti koje poštuju unapred definisane interfejse.

**Povezanost sa projektom:** Cilj je da engine omogući uključivanje novih agenata bez značajnih izmena postojeće arhitekture.

### 5.7. Eksterni agent (Remote Agent)

Eksterni agent predstavlja agenta koji se izvršava izvan glavnog sistema i kome se pristupa putem mrežnog interfejsa.

**Povezanost sa projektom:** Predviđena je mogućnost registracije i pozivanja eksternih agenata preko definisanog API-ja, čime se demonstrira proširivost arhitekture.

### 5.8. Validacija podataka

Validacija podataka predstavlja proveru da li podaci zadovoljavaju unapred definisana pravila, strukturu i ograničenja.

**Povezanost sa projektom:** Izlaz svakog agenta može se proveravati pre prosleđivanja narednom agentu, kako bi se smanjio rizik od neispravnih ili nepotpunih rezultata.

---

## 6. Zaključak

Predstavljeni pojmovi čine teorijsku osnovu za istraživanje i razvoj sistema za simulaciju nastavnog procesa pomoću AI agenata.

Obrazovni modeli omogućavaju identifikaciju faza i aktivnosti nastavnog procesa, dok koncepti multiagentskih sistema pružaju osnovu za definisanje odgovornosti agenata i njihove saradnje.

Principi modularne softverske arhitekture omogućavaju projektovanje generičkog engine-a koji podržava registraciju, koordinaciju i izvršavanje agenata, uključujući mogućnost integracije eksternih rešenja.

Dokument će se dopunjavati novim pojmovima tokom daljeg istraživanja i razvoja sistema.

---

## 7. Literatura

1. Branch, R. M. (2009). *Instructional Design: The ADDIE Approach*. Springer. https://doi.org/10.1007/978-0-387-09506-6
2. Biggs, J. (1996). *Enhancing Teaching through Constructive Alignment*. Higher Education. https://doi.org/10.1007/BF00138871
3. Anderson, L. W., & Krathwohl, D. R. (2001). *A Taxonomy for Learning, Teaching, and Assessing*. Longman.
4. Zhang et al. (2025). *EduPlanner: LLM-Based Multiagent Systems for Customized and Intelligent Instructional Design*. https://arxiv.org/abs/2504.05370
5. Zhang et al. (2025). *Simulating Classroom Education with LLM-Empowered Agents*. https://aclanthology.org/2025.naacl-long.520/
6. Ye et al. (2026). *AgentSchool: An LLM-Powered Multi-Agent Simulation for Education*.
7. Qian et al. (2024). *ChatDev: Communicative Agents for Software Development*. https://doi.org/10.18653/v1/2024.acl-long.810
8. Park et al. (2023). *Generative Agents: Interactive Simulacra of Human Behavior*. https://doi.org/10.1145/3586183.3606763
9. VanLehn, K. (2011). *The Relative Effectiveness of Human Tutoring, Intelligent Tutoring Systems, and Other Tutoring Systems*. https://doi.org/10.1080/00461520.2011.611369
10. Kasneci et al. (2023). *ChatGPT for Good? On Opportunities and Challenges of Large Language Models for Education*. https://doi.org/10.1016/j.lindif.2023.102274
