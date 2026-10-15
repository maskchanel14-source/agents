# Dichiarazione di accessibilità (IT)

> **Modello.** Sostituire ogni `{{SEGNAPISTO}}`. Eliminare questa nota prima della pubblicazione. Non inventare il contatto per le segnalazioni, il termine di risposta né l'autorità competente — contrassegnare ogni valore mancante come `DA FORNIRE DAL CLIENTE` e risolverlo prima della pubblicazione. Denominazioni e basi giuridiche vanno verificate per lo Stato membro interessato (`VERIFY`).

---

# Dichiarazione di accessibilità per {{NOME_PRODOTTO}}

{{DENOMINAZIONE_LEGALE}} si impegna a rendere {{NOME_PRODOTTO}} accessibile in conformità ai requisiti della direttiva (UE) 2019/882, come recepita nell'ordinamento nazionale applicabile.

**Ambito di applicazione:** {{AMBITO — sito, applicazione, servizio e versione}}
**Data della dichiarazione:** {{DATA_PUBBLICAZIONE}}
**Ultima revisione:** {{DATA_REVISIONE}}
**Ultima valutazione:** {{DATA_VALUTAZIONE}}

## Stato di conformità

{{NOME_PRODOTTO}} è stato valutato rispetto alle **Web Content Accessibility Guidelines (WCAG) 2.1 livello AA**{{ e alla norma EN 301 549, ove applicabile}}.

**Stato di conformità: {{PIENAMENTE CONFORME | PARZIALMENTE CONFORME | NON CONFORME}}.**

{{IN CASO DI CONFORMITÀ PARZIALE — indicare con precisione quanto non soddisfa il requisito:}}
I seguenti elementi non soddisfano ancora pienamente il requisito. Per ciascuno sono indicati responsabile e data obiettivo:

| Area | Limitazione | Responsabile | Data obiettivo |
|---|---|---|---|
| {{AREA}} | {{LIMITAZIONE}} | {{CLIENTE | TERZA PARTE | PIATTAFORMA}} | {{DATA}} |

{{IN CASO DI CRITERI NON VALUTATI — dichiararlo anziché supporlo:}}
I seguenti criteri non sono stati valutati nell'ultima valutazione e sono registrati come **non valutati**, non come conformi: {{ELENCO}}. I test necessari a chiuderli sono previsti per il {{DATA}}.

## Contenuti non accessibili

{{LIMITAZIONI — essere specifici e indicare la parte responsabile. Non lasciar mai intendere il controllo su una superficie altrui.}}

- **{{COMPONENTE_DI_TERZI}}** è fornito da {{FORNITORE}} ed è reso al di fuori del nostro controllo. {{DESCRIVERE_LA_BARRIERA}}. Abbiamo richiesto la correzione per iscritto il {{DATA}} e {{STIAMO_VALUTANDO_ALTERNATIVE | SIAMO_IN_ATTESA_DI_RISPOSTA}}.
- **{{SUPERFICIE_DI_PIATTAFORMA}}** — ad esempio un checkout ospitato o un frame di pagamento — non è modificabile da parte nostra. {{DESCRIVERE_LA_LIMITAZIONE}}.

## Misure adottate per garantire l'accessibilità

- {{CADENZA_DEI_TEST}} — ad esempio: verifica automatizzata rispetto a WCAG 2.1 A e AA nella continuous integration a ogni rilascio, con blocco in caso di nuove violazioni.
- **Verifica manuale** dei seguenti percorsi cliente a ogni rilascio, solo tramite tastiera e con {{SCREEN_READER_E_VERSIONE}}: {{PERCORSI — tipicamente carrello, pagamento, accesso}}.
- {{PROCESSO_DI_RIMEDIO}} — come le criticità vengono classificate, priorizzate e chiuse.
- {{FORMAZIONE}} — requisiti di accessibilità per i team di progettazione e sviluppo.

## Combinazioni verificate

{{NOME_PRODOTTO}} è stato testato con le seguenti combinazioni:

| Browser | Sistema operativo | Tecnologia assistiva |
|---|---|---|
| {{BROWSER_VERSIONE}} | {{SO_VERSIONE}} | {{TA_VERSIONE, oppure «nessuna»}} |

{{SEGNALARE_EVENTUALI_DEGRADAZIONI_NOTE_IN_UNA_COMBINAZIONE_NON_TESTATA,_OPPURE_INDICARE_CHE_LE_ALTRE_COMBINAZIONI_NON_SONO_STATE_VALUTATE.}}

## Segnalazioni e contatti

Qualora riscontri una barriera all'accessibilità, o necessiti di informazioni in un formato diverso, può contattarci:

- **Email:** {{EMAIL_MONITORATA}}
- **Modulo:** {{URL_MODULO}}
- **Posta:** {{INDIRIZZO_POSTALE}}

La preghiamo di indicare la pagina o la schermata interessata, quale operazione intendeva svolgere e quale browser e tecnologia assistiva stava utilizzando. **Ci impegniamo a rispondere entro {{N}} giorni lavorativi** e a proporre una soluzione entro ulteriori {{N}} giorni lavorativi dalla risposta.

Può richiedere gratuitamente qualsiasi contenuto in un formato alternativo accessibile.

## Procedura di reclamo

Qualora non sia soddisfatto della nostra risposta, può rivolgersi all'autorità competente:

{{AUTORITÀ_NAZIONALE — riprendere da references/details.md oppure contrassegnare VERIFY. Non inventare mai la denominazione di un'autorità.}}

- **Autorità:** {{NOME_AUTORITÀ}} `{{VERIFY — verificare rispetto allo strumento nazionale vigente}}`
- **Contatto:** {{CONTATTO_AUTORITÀ}}
- **Base giuridica:** {{CITAZIONE_STRUMENTO_NAZIONALE}} di recepimento della direttiva (UE) 2019/882

{{OVE_APPLICABILE,_indicare la procedura di risoluzione alternativa delle controversie o la via di reclamo disponibile per i consumatori in tale Stato membro.}}

## Redazione della presente dichiarazione

- **Metodo:** {{METODO — verifica automatizzata, analisi statica del codice sorgente, verifica manuale tramite tastiera, verifica con screen reader, e da parte di chi}}
- **Valutazione eseguita da:** {{VALUTATORE — team interno, fornitore individuato oppure «autovalutazione»}}
- **Ambito valutato:** {{ROUTE,_TEMPLATE_E_VERSIONI_VALUTATE}}
- **Escluso:** {{COSA_NON_È_STATO_VALUTATO_E_PERCHÉ}}

La presente dichiarazione costituisce documentazione redatta sulla base di una valutazione tecnica. Non rappresenta una certificazione di conformità né un parere legale. Solo un valutatore indipendente può certificare la conformità, e qualsiasi questione giuridica relativa all'applicabilità della direttiva (UE) 2019/882 deve essere confermata da un avvocato abilitato nello Stato membro interessato.

---

**{{DENOMINAZIONE_LEGALE}}** · {{URL_PAGINA_CONTATTI}} · La presente dichiarazione è stata pubblicata il {{DATA_PUBBLICAZIONE}}.
