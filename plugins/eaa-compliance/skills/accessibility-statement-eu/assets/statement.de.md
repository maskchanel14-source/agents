# Erklärung zur Barrierefreiheit (DE)

> **Vorlage.** Alle `{{PLATZHALTER}}` ersetzen. Diesen Hinweis vor der Veröffentlichung löschen. Feedback-Kontakt, Antwortfrist und Aufsichtsbehörde **nicht** erfinden — fehlende Werte mit `VOM AUFTRAGGEBER ZU LIEFERN` markieren und vor Veröffentlichung klären. Bezeichnungen und Rechtsgrundlagen sind für den jeweiligen Mitgliedstaat zu prüfen (`VERIFY`).

---

# Erklärung zur Barrierefreiheit für {{PRODUKT_NAME}}

Die {{ORGANISATION_RECHTSNAME}} ist bemüht, {{PRODUKT_NAME}} im Einklang mit den Anforderungen der Richtlinie (EU) 2019/882 sowie dem Barrierefreiheitsstärkungsgesetz (BFSG) barrierefrei zugänglich zu machen.

**Geltungsbereich:** {{GELTUNGSBEREICH — Website, Anwendung, Dienstleistung und Version}}
**Datum der Erklärung:** {{DATUM_VERÖFFENTLICHT}}
**Zuletzt geprüft:** {{DATUM_GEPRÜFT}}
**Zuletzt bewertet:** {{DATUM_BEWERTET}}

## Stand der Vereinbarkeit mit den Anforderungen

{{PRODUKT_NAME}} wurde anhand der **Web Content Accessibility Guidelines (WCAG) 2.1 Level AA**{{ sowie EN 301 549, sofern einschlägig}} bewertet.

**Vereinbarkeitsstatus: {{VOLLSTÄNDIG VEREINBAR | TEILWEISE VEREINBAR | NICHT VEREINBAR}}.**

{{BEI TEILWEISER VEREINBARKEIT — die nicht erfüllten Anforderungen konkret benennen:}}
Die nachstehenden Inhalte und Funktionen sind derzeit nicht vollständig barrierefrei. Für jeden Punkt sind Verantwortung und Zieltermin ausgewiesen:

| Bereich | Einschränkung | Verantwortung | Zieltermin |
|---|---|---|---|
| {{BEREICH}} | {{EINSCHRÄNKUNG}} | {{EIGEN | DRITTER | PLATTFORM}} | {{DATUM}} |

{{BEI NICHT BEWERTETEN KRITERIEN — offenlegen statt annehmen:}}
Die folgenden Erfolgskriterien wurden bei der letzten Bewertung nicht geprüft und sind als **nicht bewertet** ausgewiesen, nicht als vereinbar angenommen: {{LISTE}}. Die Prüfung ist für {{DATUM}} vorgesehen.

## Nicht barrierefreie Inhalte

{{EINSCHRÄNKUNGEN — konkret benennen und die verantwortliche Stelle nennen. Niemals Kontrolle über eine fremde Oberfläche suggerieren.}}

- **{{FREMDKOMPONENTE}}** wird von {{ANBIETER}} bereitgestellt und außerhalb unseres Einflussbereichs dargestellt. {{BARRIERE_BESCHREIBEN}}. Wir haben am {{DATUM}} schriftlich um Behebung gebeten und {{PRÜFEN_ALTERNATIVEN | WARTEN_AUF_ANTWORT}}.
- **{{PLATTFORM_OBERFLÄCHE}}** — etwa ein gehosteter Checkout oder ein Zahlungsrahmen — ist durch uns nicht veränderbar. {{EINSCHRÄNKUNG_BESCHREIBEN}}.

## Maßnahmen zur Sicherstellung der Barrierefreiheit

- {{PRÜFKADENZ}} — zum Beispiel: automatisierte Prüfung gegen WCAG 2.1 A und AA in der Continuous Integration bei jedem Release, mit Abbruch bei neu auftretenden Verstößen.
- **Manuelle Prüfung** der folgenden Kundenvorgänge bei jedem Release, ausschließlich per Tastatur sowie mit {{SCREENREADER_UND_VERSION}}: {{VORGÄNGE — in der Regel Warenkorb, Bezahlung, Anmeldung}}.
- {{BEHEBUNGSPROZESS}} — wie Befunde priorisiert, umgesetzt und abgenommen werden.
- {{SCHULUNG}} — Barrierefreiheitsanforderungen für Design und Entwicklung.

## Geprüfte Kombinationen

{{PRODUKT_NAME}} wurde mit folgenden Kombinationen getestet:

| Browser | Betriebssystem | Hilfstechnologie |
|---|---|---|
| {{BROWSER_VERSION}} | {{OS_VERSION}} | {{HILFSTECHNOLOGIE_VERSION oder „keine“}} |

{{BEKANNTE_EINSCHRÄNKUNGEN_IN_NICHT_GEPRÜFTEN_KOMBINATIONEN_NENNEN_ODER_AUSWEISEN,_DASS_SIE_NICHT_BEWERTET_WURDEN.}}

## Feedback und Kontaktangaben

Wenn Sie eine Barriere feststellen oder Informationen in einer anderen Form benötigen, wenden Sie sich bitte an uns:

- **E-Mail:** {{ÜBERWACHTE_EMAIL}}
- **Formular:** {{FORMULAR_URL}}
- **Post:** {{POSTANSCHRIFT}}

Bitte teilen Sie uns die betroffene Seite oder Maske mit, was Sie tun wollten und welchen Browser sowie welche Hilfstechnologie Sie verwendet haben. **Wir antworten innerhalb von {{N}} Werktagen** und schlagen innerhalb weiterer {{N}} Werktage nach dieser Antwort eine Lösung vor.

Sie können sämtliche Inhalte dieser Website kostenfrei in einem barrierefreien Alternativformat anfordern.

## Durchsetzungsverfahren

Sollten Sie auch nach Ihrem Feedback an uns keine zufriedenstellende Antwort erhalten, können Sie sich an die zuständige Stelle wenden:

{{AUFSICHTSBEHÖRDE — aus references/details.md übernehmen oder mit VERIFY markieren. Behördennamen niemals erfinden.}}

- **Zuständige Stelle:** {{BEHÖRDE_NAME}} `{{VERIFY — gegen die geltende nationale Fassung prüfen}}`
- **Kontakt:** {{BEHÖRDE_KONTAKT}}
- **Rechtsgrundlage:** {{NATIONALE_FUNDSTELLE}} zur Umsetzung der Richtlinie (EU) 2019/882

{{GEgebenenfalls zusätzlich das Schlichtungsverfahren oder die Verbraucherbeschwerdestelle des Mitgliedstaats nennen.}}

## Erstellung dieser Erklärung

- **Methode:** {{METHODE — automatisierte Prüfung, statische Quellcodeanalyse, manuelle Tastaturprüfung, Screenreader-Prüfung, sowie durch wen}}
- **Bewertet durch:** {{PRÜFER — internes Team, benannter Dienstleister oder „Selbstbewertung“}}
- **Umfang:** {{GEPRÜFTE_ROUTES_TEMPLATES_UND_VERSIONEN}}
- **Ausgenommen:** {{WAS_NICHT_GEPRÜFT_WURDE_UND_WARUM}}

Diese Erklärung ist eine Dokumentation auf Grundlage einer technischen Bewertung. Sie ist keine Konformitätszertifizierung und keine Rechtsberatung. Eine Zertifizierung der Konformität kann nur eine unabhängige Bewertungsstelle vornehmen; Rechtsfragen zur Anwendbarkeit der Richtlinie (EU) 2019/882 sind durch eine in dem betreffenden Mitgliedstaat zugelassene Rechtsanwältin oder einen zugelassenen Rechtsanwalt zu bestätigen.

---

**{{ORGANISATION_RECHTSNAME}}** · {{KONTAKTSEITE_URL}} · Diese Erklärung wurde am {{DATUM_VERÖFFENTLICHT}} veröffentlicht.
