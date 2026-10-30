# Predlog arhitekture multiagentskog sistema za simulaciju nastavnog procesa

## 1. Osnovna ideja arhitekture

Za projekat „Simulacija nastavnog procesa pomoću AI agenata“ predlaže se **modularna multiagentska arhitektura sa hijerarhijskom orkestracijom**.

Osnovna ideja je da se celokupan nastavni proces podeli na četiri međusobno povezane faze:

1. **Dizajn kurikuluma** – definisanje nastavnih ciljeva, kompetencija i plana nastave.
2. **Kreiranje nastavnih sadržaja** – generisanje lekcija, primera, zadataka i drugih materijala.
3. **Realizacija nastave** – simulacija nastavnog procesa kroz interakciju nastavničkih i učeničkih agenata.
4. **Evaluacija i unapređenje** – provera rezultata, analiza uspešnosti i predlaganje poboljšanja.

Svaka faza sadrži specijalizovane agente koji izvršavaju konkretne zadatke.

Za organizaciju njihovog rada predlaže se korišćenje **LangGraph framework-a**, uz razvoj sopstvenog generičkog engine-a za registraciju, pronalaženje i pozivanje agenata.

Cilj je da sistem bude modularan, proširiv i sposoban da povezuje različite vrste agenata, uključujući lokalne i eksterne agente.

## 2. Glavne komponente arhitekture

### 2.1. Generički engine

Generički engine predstavlja centralni infrastrukturni deo sistema koji omogućava rad sa različitim agentima.

Njegove osnovne odgovornosti su:

- Registracija i pronalaženje agenata.
- Izbor odgovarajućeg agenta za određeni zadatak.
- Pozivanje lokalnih i eksternih agenata.
- Obrada rezultata i grešaka tokom izvršavanja.
- Povezivanje mehanizama za registraciju, pozivanje i orkestraciju.

**Primer:** Kada je potrebno generisati lekciju, engine pronalazi agenta koji poseduje tu sposobnost i omogućava njegovo izvršavanje.

Engine treba da podrži proizvoljan broj registrovanih agenata, uključujući više agenata sa istom sposobnošću.

### 2.2. Agent Registry

Agent Registry predstavlja katalog dostupnih agenata.

Za svakog agenta čuva informacije kao što su:

- Jedinstveni identifikator i naziv.
- Faza kojoj pripada.
- Zadaci i sposobnosti koje poseduje.
- Način izvršavanja (lokalni ili eksterni).
- Očekivani ulazni i izlazni podaci.

**Primer:** Ako je potreban agent za generisanje zadataka, sistem preko registra pronalazi agenta koji može da izvrši taj zadatak.

Registry ne izvršava zadatke, već omogućava da sistem zna koji agenti postoje i za šta su zaduženi.

### 2.3. Agent Invoker / Adapter

Agent Invoker predstavlja komponentu zaduženu za pozivanje izabranog agenta.

Na osnovu informacija iz registra određuje kako će agent biti pokrenut.

Podržava dva osnovna načina izvršavanja:

- **Lokalni agenti** – Python funkcije ili LLM agenti koji se izvršavaju unutar sistema.
- **Eksterni agenti** – agenti koji se nalaze na drugom serveru i pozivaju se putem HTTP API-ja.

Invoker prosleđuje potrebne ulazne podatke, preuzima rezultat i obrađuje eventualne greške.

**Primer:** Agent za generisanje lekcija može biti lokalna Python komponenta, ali i eksterni servis. Ostatak sistema koristi isti način zahtevanja zadatka, bez obzira na lokaciju agenta.

### 2.4. Glavni orkestrator

Glavni orkestrator upravlja celokupnim nastavnim procesom.

Njegova uloga je da:

- Pokreće četiri faze odgovarajućim redosledom.
- Obezbeđuje prenos rezultata između faza.
- Prati završetak pojedinačnih faza.
- Upravlja povratnom spregom nakon evaluacije.

**Primer:** Nakon što prva faza generiše kurikulum, glavni orkestrator pokreće drugu fazu, koja na osnovu tog kurikuluma kreira nastavne materijale.

Za realizaciju glavnog orkestratora predlaže se LangGraph.

### 2.5. Fazni orkestratori

Svaka od četiri faze ima sopstveni fazni orkestrator.

Njegova uloga je da organizuje rad agenata unutar određene faze.

Fazni orkestratori omogućavaju:

- Sekvencijalno izvršavanje zavisnih zadataka.
- Paralelno izvršavanje nezavisnih zadataka.
- Prenos rezultata između agenata.
- Ponovno izvršavanje pojedinih aktivnosti kada je potrebno.

**Primer:** U fazi kreiranja nastavnih sadržaja prvo se generiše lekcija. Nakon toga agent za primere i agent za zadatke mogu paralelno da rade na osnovu iste lekcije.

U LangGraph-u svaka faza može biti predstavljena kao zaseban podgraf.

### 2.6. Specijalizovani agenti

Specijalizovani agenti izvršavaju konkretne zadatke nastavnog procesa.

U početnoj analizi identifikovane su **34 funkcionalne uloge agenata**, raspoređene kroz četiri faze:

- Faza 1 – 8 agenata.
- Faza 2 – 10 agenata.
- Faza 3 – 7 tipova agenata.
- Faza 4 – 9 agenata.

Agenti mogu koristiti LLM modele, obične Python funkcije ili eksterne servise.

Nije neophodno da svaki agent odmah bude složen AI sistem. U početnoj implementaciji mogu se koristiti jednostavne verzije agenata, koje će kasnije biti unapređivane.

### 2.7. Zajedničko stanje (State)

Zajedničko stanje predstavlja strukturu u kojoj se čuvaju podaci potrebni tokom izvršavanja nastavnog procesa.

Može sadržati:

- Korisnički zahtev i temu kursa.
- Nastavne ciljeve i kurikulum.
- Generisane nastavne materijale.
- Profile i stanje znanja simuliranih učenika.
- Rezultate simulacije.
- Rezultate evaluacije.

**Primer:** Agent za generisanje lekcija koristi nastavne ciljeve koje je prethodno definisao agent iz prve faze.

Na taj način izlaz jednog agenta postaje ulaz drugog, bez potrebe da svi agenti međusobno direktno komuniciraju.

## 3. Način rada sistema

Korisnik na početku unosi temu kursa, ciljnu grupu i osnovne zahteve.

Generički engine pokreće proces, a glavni orkestrator upravlja izvršavanjem četiri faze.

**Faza 1 – Dizajn kurikuluma**

Agenti analiziraju obrazovne potrebe, predznanje, postojeće kurikulume i definišu ciljeve i plan nastave.

Rezultat je strukturisan kurikulum koji predstavlja osnovu za sledeću fazu.

**Faza 2 – Kreiranje nastavnih sadržaja**

Na osnovu kurikuluma agenti generišu lekcije, primere, zadatke i ostale nastavne materijale.

Rezultat su materijali koji će se koristiti u simulaciji nastave.

**Faza 3 – Realizacija nastave**

Agent nastavnik i simulirani učenički agenti učestvuju u nastavnim aktivnostima.

Classroom Controller koordinira njihove interakcije, dok drugi agenti prate stanje znanja i beleže tok simulacije.

Rezultat su zapis simulacije i procenjeno stanje znanja simuliranih učenika.

**Faza 4 – Evaluacija i unapređenje**

Agenti generišu testove, ocenjuju odgovore, analiziraju greške i proveravaju ostvarenost nastavnih ciljeva.

Na osnovu rezultata formiraju se izveštaj i predlozi poboljšanja.

Ako evaluacija otkrije problem, glavni orkestrator može ponovo pokrenuti odgovarajuće aktivnosti iz prethodnih faza.

Ovaj mehanizam predstavlja **povratnu spregu**, koja omogućava iterativno unapređenje rezultata.

## 4. Zašto je izabran LangGraph?

LangGraph je odabran kao najpogodniji početni kandidat za orkestraciju zbog sledećih mogućnosti:

- Organizacija procesa kroz grafove i podgrafove.
- Definisanje redosleda izvršavanja agenata.
- Sekvencijalno i paralelno izvršavanje.
- Razmena podataka preko zajedničkog stanja.
- Uslovni prelazi i povratna sprega.
- Povezivanje lokalnih i eksternih agenata kroz Python kod.

Posebno je pogodan za organizaciju četiri faze nastavnog procesa, jer svaka faza može biti predstavljena kao zaseban podgraf.

**Važno je razlikovati LangGraph i generički engine.**

LangGraph obezbeđuje mehanizme za upravljanje tokom izvršavanja, dok sopstveni engine obezbeđuje generičku registraciju, pronalaženje i pozivanje agenata.

Samostalni razvoj Agent Registry-ja i mehanizma za pozivanje agenata predstavlja važan projektni doprinos.

## 5. Glavne prednosti predložene arhitekture

**Modularnost** – sistem je podeljen na nezavisne komponente i četiri jasno definisane faze.

**Proširivost** – moguće je dodavati nove agente i zamenjivati postojeće implementacije.

**Fleksibilnost** – agenti mogu biti Python funkcije, LLM agenti ili eksterni servisi.

**Koordinacija** – glavni i fazni orkestratori upravljaju redosledom izvršavanja.

**Razmena podataka** – zajedničko stanje omogućava povezivanje agenata i faza.

**Paralelizacija** – nezavisni zadaci mogu se izvršavati istovremeno.

**Povratna sprega** – rezultati evaluacije mogu se koristiti za ponovno izvršavanje i unapređenje prethodnih aktivnosti.

## 6. Plan početne implementacije

U prvoj verziji planirano je razvijanje jednostavnog prototipa koji demonstrira osnovne mogućnosti arhitekture.

Prvo bi se implementirali Agent Registry, mehanizam za pozivanje agenata i jednostavan LangGraph tok.

Zatim bi se povezalo nekoliko osnovnih agenata, uključujući po jednog predstavnika iz svake faze.

Nakon toga bi se dodali prenos podataka, jednostavna povratna sprega i primer pozivanja eksternog agenta preko HTTP API-ja.

U kasnijim iteracijama sistem bi se proširivao dodatnim agentima i naprednijim LLM funkcionalnostima.

## 7. Zaključak

Na osnovu istraživanja framework-a i identifikacije agenata, kao početno rešenje predlaže se **modularna multiagentska arhitektura sa hijerarhijskom orkestracijom**.

Arhitektura kombinuje LangGraph za upravljanje tokom izvršavanja i sopstveni generički engine za registraciju, pronalaženje i pozivanje agenata.

Glavni orkestrator upravlja sa četiri faze nastavnog procesa, dok fazni orkestratori koordiniraju specijalizovane agente unutar pojedinačnih faza.

Zajedničko stanje omogućava prenos podataka između faza, a povratna sprega omogućava unapređenje rezultata na osnovu evaluacije.

**Osnovni cilj predložene arhitekture jeste razvoj fleksibilnog i proširivog sistema u kojem različiti AI agenti mogu sarađivati u realizaciji celokupnog nastavnog procesa.**

Ovo predstavlja početni arhitektonski predlog koji će biti potvrđen i dodatno razrađen kroz implementaciju prototipa.
