# Toegankelijkheidsverklaring (NL)

> **Sjabloon.** Vervang elke `{{PLAATSHOUDER}}`. Verwijder deze notitie vóór publicatie. Verzin het feedbackcontact, de reactietermijn of de bevoegde autoriteit **niet** — markeer elke ontbrekende waarde als `DOOR OPDRACHTGEVER AAN TE LEVEREN` en los deze vóór publicatie op. Benamingen en rechtsgrondslagen dienen per lidstaat te worden geverifieerd (`VERIFY`).

---

# Toegankelijkheidsverklaring voor {{PRODUCTNAAM}}

{{STATUTAIRE_NAAM}} verbindt zich ertoe {{PRODUCTNAAM}} toegankelijk te maken overeenkomstig de eisen van Richtlijn (EU) 2019/882, zoals omgezet in de toepasselijke nationale wetgeving.

**Werkingssfeer:** {{WERKINGSSFEER — website, applicatie, dienst en versie}}
**Datum verklaring:** {{DATUM_GEPUBLICEERD}}
**Laatst herzien:** {{DATUM_HERZIEN}}
**Laatst beoordeeld:** {{DATUM_BEOORDEELD}}

## Conformiteitsstatus

{{PRODUCTNAAM}} is beoordeeld aan de hand van de **Web Content Accessibility Guidelines (WCAG) 2.1 niveau AA**{{ en, waar van toepassing, EN 301 549}}.

**Conformiteitsstatus: {{VOLLEDIG CONFORM | GEDEELTELIJK CONFORM | NIET CONFORM}}.**

{{BIJ GEDEELTELIJKE CONFORMITEIT — benoem concreet wat niet voldoet:}}
De volgende onderdelen voldoen nog niet volledig aan de norm. Voor elk onderdeel zijn verantwoordelijke en streefdatum opgenomen:

| Onderdeel | Beperking | Verantwoordelijke | Streefdatum |
|---|---|---|---|
| {{ONDERDEEL}} | {{BEPERKING}} | {{EIGEN | DERDE | PLATFORM}} | {{DATUM}} |

{{BIJ NIET-BEOORDEELDE CRITERIA — meld dit in plaats van het aan te nemen:}}
De volgende criteria zijn bij de laatste beoordeling niet getest en zijn vastgelegd als **niet beoordeeld**, niet als conform: {{LIJST}}. De tests om deze af te ronden staan gepland voor {{DATUM}}.

## Niet-toegankelijke content

{{BEPERKINGEN — wees specifiek en benoem de verantwoordelijke partij. Wek nooit de indruk controle te hebben over een oppervlak dat u niet beheert.}}

- **{{COMPONENT_VAN_DERDE}}** wordt geleverd door {{LEVERANCIER}} en wordt buiten onze invloedssfeer weergegeven. {{BESCHRIJF_DE_BARRIERE}}. Wij hebben op {{DATUM}} schriftelijk om herstel verzocht en {{ONDERZOEKEN_ALTERNATIEVEN | WACHTEN_OP_ANTWOORD}}.
- **{{PLATFORMOPPERVLAK}}** — bijvoorbeeld een gehoste checkout of een betalingsframe — is door ons niet aanpasbaar. {{BESCHRIJF_DE_BEPERKING}}.

## Maatregelen om toegankelijkheid te borgen

- {{TESTCADANS}} — bijvoorbeeld: geautomatiseerde toetsing aan WCAG 2.1 A en AA in continuous integration bij elke release, met een blokkade bij nieuwe overtredingen.
- **Handmatige tests** van de volgende klantreizen bij elke release, uitsluitend met toetsenbord en met {{SCREENREADER_EN_VERSIE}}: {{REIZEN — doorgaans winkelwagen, betaling, inloggen}}.
- {{HERSTELPROCES}} — hoe bevindingen worden gewogen, geprioriteerd en afgerond.
- {{TRAINING}} — toegankelijkheidseisen voor de ontwerp- en ontwikkelteams.

## Geteste combinaties

{{PRODUCTNAAM}} is getest met de volgende combinaties:

| Browser | Besturingssysteem | Hulptechnologie |
|---|---|---|
| {{BROWSER_VERSIE}} | {{OS_VERSIE}} | {{HT_VERSIE, of "geen"}} |

{{MELD_ELKE_BEKENDE_VERMINDERING_IN_EEN_NIET_GETESTE_COMBINATIE,_OF_VERMELD_DAT_ANDERE_COMBINATIES_NIET_ZIJN_BEOORDEELD.}}

## Feedback en contactgegevens

Als u een toegankelijkheidsbarrière tegenkomt, of informatie in een ander formaat nodig heeft, neem dan contact met ons op:

- **E-mail:** {{GEMONITORD_EMAILADRES}}
- **Formulier:** {{FORMULIER_URL}}
- **Post:** {{POSTADRES}}

Vermeld de betreffende pagina of het betreffende scherm, wat u probeerde te doen en welke browser en hulptechnologie u gebruikte. **Wij reageren binnen {{N}} werkdagen** en doen binnen {{N}} werkdagen na dat antwoord een oplossing voor.

U kunt elke inhoud van deze website kosteloos opvragen in een toegankelijk alternatief formaat.

## Klachtenprocedure

Bent u niet tevreden met ons antwoord, dan kunt u zich wenden tot de bevoegde autoriteit:

{{NATIONALE_AUTORITEIT — overnemen uit references/details.md of markeren als VERIFY. Verzin nooit een autoriteitsnaam.}}

- **Autoriteit:** {{AUTORITEIT_NAAM}} `{{VERIFY — toetsen aan het geldende nationale omzettingsbesluit}}`
- **Contact:** {{AUTORITEIT_CONTACT}}
- **Rechtsgrondslag:** {{NATIONALE_CITAAT}} tot omzetting van Richtlijn (EU) 2019/882

{{VERMELD_INDIEN_VAN_TOEPASSING de procedure voor alternatieve geschillenbeslechting of de consumentenklachtroute die in deze lidstaat beschikbaar is.}}

## Totstandkoming van deze verklaring

- **Methode:** {{METHODE — geautomatiseerde analyse, statische bronnocodeanalyse, handmatige toetsenbordtests, screenreadertests, en door wie}}
- **Beoordeeld door:** {{BEOORDELAAR — intern team, benoemde partij of "zelfevaluatie"}}
- **Beoordeelde omvang:** {{ROUTES,_TEMPLATES_EN_VERSIES}}
- **Uitgesloten:** {{WAT_NIET_IS_BEOORDEELD_EN_WAAROM}}

Deze verklaring is documentatie op basis van een technische beoordeling. Zij vormt geen conformiteitscertificering en geen juridisch advies. Uitsluitend een onafhankelijke beoordelaar kan conformiteit certificeren, en elke juridische vraag over de toepasselijkheid van Richtlijn (EU) 2019/882 dient te worden bevestigd door een gekwalificeerde advocaat in de betreffende lidstaat.

---

**{{STATUTAIRE_NAAM}}** · {{CONTACTPAGINA_URL}} · Deze verklaring is gepubliceerd op {{DATUM_GEPUBLICEERD}}.
