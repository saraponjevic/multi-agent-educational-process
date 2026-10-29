# Identifikacija agenata

Predstavljeni agenti čine **početni katalog planiranih komponenti**. U prvoj implementaciji biće realizovane njihove jednostavne verzije, dok će se pojedini agenti kasnije dodatno razvijati.

## Faza 1 – Dizajn kurikuluma

**1. Agent za analizu obrazovnih potreba**
- Zadatak: Utvrđuje obrazovne potrebe ciljne grupe.
- Ulaz: Oblast, ciljna grupa, zahtevi.
- Izlaz: Lista obrazovnih potreba.

**2. Agent za analizu predznanja**
- Zadatak: Analizira početni nivo znanja učenika.
- Ulaz: Profil učenika, oblast.
- Izlaz: Procena predznanja i potrebnih preduslova.

**3. Agent za analizu postojećih kurikuluma**
- Zadatak: Pronalazi i upoređuje postojeće nastavne programe.
- Ulaz: Oblast, dostupni kurikulumi ili izvori.
- Izlaz: Uporedna analiza tema i ishoda učenja.

**4. Agent za identifikaciju kompetencija**
- Zadatak: Definiše znanja i veštine koje učenici treba da steknu.
- Ulaz: Obrazovne potrebe, analiza kurikuluma.
- Izlaz: Lista kompetencija.

**5. Agent za definisanje nastavnih ciljeva**
- Zadatak: Formuliše merljive ciljeve učenja.
- Ulaz: Kompetencije, predznanje.
- Izlaz: Nastavni ciljevi sa ID-jevima i kognitivnim nivoima.

**6. Agent za strukturiranje nastavnog plana**
- Zadatak: Organizuje nastavne teme, redosled i zavisnosti.
- Ulaz: Nastavni ciljevi, kompetencije.
- Izlaz: Strukturisan nastavni plan.

**7. Agent za planiranje evaluacije**
- Zadatak: Definiše načine provere ostvarenosti nastavnih ciljeva.
- Ulaz: Nastavni ciljevi.
- Izlaz: Plan evaluacije po ciljevima.

**8. Agent za validaciju kurikuluma**
- Zadatak: Proverava potpunost, strukturu i konzistentnost kurikuluma.
- Ulaz: Generisani kurikulum.
- Izlaz: Izveštaj o validaciji.

**Rezultat faze:** Strukturisan i validiran kurikulum sa nastavnim ciljevima i planom evaluacije.

## Faza 2 – Kreiranje nastavnih sadržaja

**1. Agent za izbor instrukcione strategije**
- Zadatak: Bira odgovarajući način podučavanja.
- Ulaz: Kurikulum, profil učenika.
- Izlaz: Predlog instrukcione strategije.

**2. Agent za planiranje nastavnih aktivnosti**
- Zadatak: Planira aktivnosti nastavnika i učenika.
- Ulaz: Nastavni ciljevi, instrukciona strategija.
- Izlaz: Plan nastavnih aktivnosti.

**3. Agent za generisanje lekcija**
- Zadatak: Kreira teorijska objašnjenja nastavnih jedinica.
- Ulaz: Nastavni ciljevi, teme, nivo učenika.
- Izlaz: Tekst lekcije.

**4. Agent za generisanje primera**
- Zadatak: Kreira primere za objašnjenje koncepata.
- Ulaz: Lekcija, nastavni ciljevi.
- Izlaz: Skup primera.

**5. Agent za generisanje zadataka**
- Zadatak: Kreira zadatke različitih nivoa težine.
- Ulaz: Nastavni ciljevi, lekcije.
- Izlaz: Skup zadataka.

**6. Agent za rešavanje zadataka**
- Zadatak: Rešava generisane zadatke.
- Ulaz: Zadaci.
- Izlaz: Predložena referentna rešenja.

**7. Agent za proveru tačnosti materijala**
- Zadatak: Proverava ispravnost objašnjenja, primera i rešenja.
- Ulaz: Nastavni materijali, referentni izvori.
- Izlaz: Izveštaj o uočenim greškama.

**8. Agent za proveru kvaliteta materijala**
- Zadatak: Procenjuje jasnoću, potpunost i prilagođenost sadržaja.
- Ulaz: Nastavni materijali, kriterijumi kvaliteta.
- Izlaz: Ocena kvaliteta i preporuke.

**9. Agent za formatiranje i eksport**
- Zadatak: Pretvara sadržaj u odgovarajući format.
- Ulaz: Pripremljeni materijali, željeni format.
- Izlaz: PDF, Markdown ili HTML dokument.

**10. Agent za organizaciju i distribuciju materijala**
- Zadatak: Organizuje materijale po nastavnim jedinicama i priprema ih za korišćenje.
- Ulaz: Materijali, nastavni plan.
- Izlaz: Organizovana kolekcija materijala.

**Rezultat faze:** Pripremljeni nastavni materijali, primeri, zadaci i aktivnosti povezani sa ciljevima kurikuluma.

## Faza 3 – Realizacija nastave

**1. Agent za pripremu nastavnog scenarija**
- Zadatak: Definiše početne uslove simulacije.
- Ulaz: Nastavni plan, materijali, profili učenika.
- Izlaz: Nastavni scenario.

**2. Agent nastavnik (Teaching Agent)**
- Zadatak: Izvodi lekciju, objašnjava gradivo i komunicira sa učenicima.
- Ulaz: Nastavni scenario, materijali, pitanja učenika.
- Izlaz: Objašnjenja, pitanja i odgovori.

**3. Agent učenik (Student Agent)**
- Zadatak: Simulira učenika koji učestvuje u nastavi.
- Ulaz: Profil učenika, stanje znanja, nastavne aktivnosti.
- Izlaz: Odgovori, pitanja i reakcije.

Moguće je kreirati više instanci učenika sa različitim nivoima predznanja: početni, srednji i napredni.

**4. Agent za upravljanje stanjem znanja učenika**
- Zadatak: Prati procenjeno znanje i pogrešna razumevanja učenika.
- Ulaz: Odgovori i interakcije učenika.
- Izlaz: Ažurirano stanje znanja.

**5. Agent za prilagođavanje nastave**
- Zadatak: Predlaže prilagođavanje objašnjenja i zadataka.
- Ulaz: Stanje znanja učenika, nastavne aktivnosti.
- Izlaz: Predlog prilagođavanja nastave.

**6. Agent za upravljanje učionicom (Classroom Controller)**
- Zadatak: Upravlja redosledom interakcija u simulaciji.
- Ulaz: Nastavni scenario, trenutno stanje simulacije.
- Izlaz: Sledeća aktivnost ili učesnik.

**7. Agent za praćenje nastavnih aktivnosti**
- Zadatak: Beleži tok simulacije i aktivnosti učesnika.
- Ulaz: Interakcije nastavnika i učenika.
- Izlaz: Zapis nastavnog procesa.

**Rezultat faze:** Simuliran nastavni proces sa zapisanim interakcijama i procenjenim stanjem znanja učenika.

## Faza 4 – Evaluacija nastavnog procesa

**1. Agent za generisanje testova**
- Zadatak: Kreira testove na osnovu nastavnih ciljeva.
- Ulaz: Kurikulum, nastavni ciljevi.
- Izlaz: Testovi i pitanja.

**2. Agent za ocenjivanje odgovora**
- Zadatak: Ocenjuje odgovore učenika prema definisanim kriterijumima.
- Ulaz: Odgovori, referentna rešenja, kriterijumi.
- Izlaz: Ocene i obrazloženja.

**3. Agent za analizu grešaka učenika**
- Zadatak: Identifikuje česte greške i pogrešna razumevanja.
- Ulaz: Odgovori i rezultati testiranja.
- Izlaz: Analiza grešaka.

**4. Agent za analizu ostvarenosti nastavnih ciljeva**
- Zadatak: Procenjuje ostvarenje pojedinačnih ciljeva učenja.
- Ulaz: Nastavni ciljevi, rezultati evaluacije.
- Izlaz: Procena ostvarenosti ciljeva.

**5. Agent za proveru usklađenosti**
- Zadatak: Proverava povezanost ciljeva, materijala, aktivnosti i testova.
- Ulaz: Kurikulum, materijali, testovi.
- Izlaz: Izveštaj o usklađenosti i nedostacima.

**6. Agent za evaluaciju kvaliteta (Evaluator Agent)**
- Zadatak: Procenjuje kvalitet nastavnog procesa prema definisanim kriterijumima.
- Ulaz: Kurikulum, materijali, rezultati simulacije.
- Izlaz: Ocena kvaliteta i obrazloženje.

**7. Agent za optimizaciju (Optimizer Agent)**
- Zadatak: Predlaže unapređenja nastavnog procesa.
- Ulaz: Rezultati evaluacije, identifikovani problemi.
- Izlaz: Predlog korekcija.

**8. Agent za upravljanje povratnom spregom**
- Zadatak: Određuje koje prethodne aktivnosti treba ponoviti.
- Ulaz: Predložene korekcije.
- Izlaz: Zahtev za ponovno izvršavanje odgovarajućeg agenta.

**9. Agent za generisanje izveštaja**
- Zadatak: Formira završni izveštaj o rezultatima i kvalitetu nastave.
- Ulaz: Rezultati evaluacije, analize i korekcije.
- Izlaz: Završni izveštaj.

**Rezultat faze:** Izveštaj o rezultatima simulacije, ostvarenosti nastavnih ciljeva i predlozima za unapređenje.

## Orkestracija i povezivanje agenata

Pored identifikovanih agenata, sistem će sadržati generički engine koji omogućava:

- Registraciju i kategorizaciju agenata prema fazama i odgovornostima.
- Centralnu orkestraciju nastavnog procesa.
- Koordinaciju izvršavanja agenata unutar pojedinačnih faza.
- Sekvencijalno i paralelno izvršavanje kada to zavisnosti dozvoljavaju.
- Razmenu strukturisanih ulaznih i izlaznih podataka.
- Integraciju eksternih agenata putem definisanog API-ja.
- Povratnu spregu i ponovno izvršavanje pojedinih aktivnosti.

Orkestratori predstavljaju infrastrukturne komponente sistema i nisu uključeni u broj obrazovnih agenata.

