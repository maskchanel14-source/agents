# Déclaration d'accessibilité (FR)

> **Modèle.** Remplacer tous les `{{ESPACE_RÉSERVÉ}}`. Supprimer cette note avant publication. Ne jamais inventer le contact de retour d'information, le délai de réponse ni l'autorité compétente — marquer toute valeur manquante `À FOURNIR PAR LE CLIENT` et la résoudre avant publication. Les dénominations et bases juridiques doivent être vérifiées pour l'État membre concerné (`VERIFY`).

---

# Déclaration d'accessibilité de {{NOM_DU_PRODUIT}}

{{DÉNOMINATION_LÉGALE}} s'engage à rendre {{NOM_DU_PRODUIT}} accessible conformément aux exigences de la directive (UE) 2019/882, telle que transposée en droit français.

**Périmètre :** {{PÉRIMÈTRE — site, application, service et version}}
**Date de la déclaration :** {{DATE_PUBLIÉE}}
**Dernière révision :** {{DATE_RÉVISÉE}}
**Dernière évaluation :** {{DATE_ÉVALUÉE}}

## État de conformité

{{NOM_DU_PRODUIT}} a été évalué au regard du **Référentiel général d'amélioration de l'accessibilité (RGAA)** et des **Web Content Accessibility Guidelines (WCAG) 2.1 niveau AA**{{, ainsi que de la norme EN 301 549 le cas échéant}}.

**État de conformité : {{CONFORME | PARTIELLEMENT CONFORME | NON CONFORME}}.**

{{EN CAS DE CONFORMITÉ PARTIELLE — énoncer clairement ce qui échoue :}}
Les éléments suivants ne satisfont pas encore pleinement au référentiel. Chacun est assorti d'un responsable et d'une date cible :

| Zone | Limitation | Responsable | Date cible |
|---|---|---|---|
| {{ZONE}} | {{LIMITATION}} | {{CLIENT | TIERS | PLATEFORME}} | {{DATE}} |

{{EN CAS DE CRITÈRES NON ÉVALUÉS — le déclarer plutôt que de le présumer :}}
Les critères suivants n'ont pas été évalués lors de la dernière évaluation et sont consignés comme **non évalués** plutôt que présumés conformes : {{LISTE}}. Les tests permettant de les clôturer sont planifiés pour le {{DATE}}.

## Contenus non accessibles

{{LIMITATIONS — être précis et nommer la partie responsable. Ne jamais laisser entendre un contrôle sur une surface que vous ne contrôlez pas.}}

- **{{COMPOSANT_TIERCE_PARTIE}}** est fourni par {{FOURNISSEUR}} et affiché hors de notre contrôle. {{DÉCRIRE_LA_BARRIERE}}. Nous avons demandé sa correction par écrit le {{DATE}} et {{EXAMINONS_DES_ALTERNATIVES | SOMMES_EN_ATTENTE_DE_RÉPONSE}}.
- **{{SURFACE_PLATEFORME}}** — par exemple un tunnel de commande hébergé ou un cadre de paiement — n'est pas modifiable par nos soins. {{DÉCRIRE_LA_LIMITATION}}.

## Mesures prises pour assurer l'accessibilité

- {{CADENCE_DE_TESTS}} — par exemple : analyse automatisée WCAG 2.1 A et AA dans l'intégration continue à chaque mise en production, avec blocage en cas de régression.
- **Tests manuels** des parcours clients suivants à chaque mise en production, au clavier uniquement et avec {{LECTEUR_D_ÉCRAN_ET_VERSION}} : {{PARCOURS — typiquement panier, paiement, connexion}}.
- {{PROCESSUS_DE_CORRECTION}} — manière dont les constats sont triés, priorisés et clôturés.
- {{FORMATION}} — exigences d'accessibilité applicables aux équipes de conception et de développement.

## Environnement de test

{{NOM_DU_PRODUIT}} a été testé avec les combinaisons suivantes :

| Navigateur | Système d'exploitation | Technologie d'assistance |
|---|---|---|
| {{NAVIGATEUR_VERSION}} | {{OS_VERSION}} | {{TA_VERSION, ou « aucune »}} |

{{SIGNALER_TOUTE_DÉGRADATION_CONNUE_DANS_UNE_COMBINAISON_NON_TESTÉE,_OU_INDIQUER_QUE_LES_AUTRES_COMBINAISONS_N_ONT_PAS_ÉTÉ_ÉVALUÉES.}}

## Retour d'information et contact

Si vous rencontrez une barrière d'accessibilité, ou si vous avez besoin d'une information dans un autre format, contactez-nous :

- **Courriel :** {{COURRIEL_SUIVI}}
- **Formulaire :** {{URL_FORMULAIRE}}
- **Courrier :** {{ADRESSE_POSTALE}}

Merci de préciser la page ou l'écran concerné, ce que vous cherchiez à faire, ainsi que le navigateur et la technologie d'assistance utilisés. **Nous répondons sous {{N}} jours ouvrés** et proposons une solution sous {{N}} jours ouvrés à compter de cette réponse.

Vous pouvez demander gratuitement tout contenu dans un format alternatif accessible.

## Voies de recours

Si notre réponse ne vous satisfait pas, vous pouvez saisir l'autorité compétente :

{{AUTORITÉ_NATIONALE — reprendre depuis references/details.md ou marquer VERIFY. Ne jamais inventer une dénomination d'autorité.}}

- **Autorité :** {{NOM_AUTORITÉ}} `{{VERIFY — vérifier au regard de l'instrument national en vigueur}}`
- **Contact :** {{CONTACT_AUTORITÉ}}
- **Fondement :** {{CITATION_INSTRUMENT_NATIONAL}} transposant la directive (UE) 2019/882

{{LE CAS ÉCHÉANT, mentionner la procédure de médiation ou la voie de réclamation ouverte aux consommateurs dans cet État membre.}}

## Établissement de cette déclaration d'accessibilité

- **Méthode :** {{MÉTHODE — analyse automatisée, analyse statique du code source, tests clavier manuels, tests au lecteur d'écran, et par qui}}
- **Évalué par :** {{ÉVALUATEUR — équipe interne, prestataire désigné ou « auto-évaluation »}}
- **Périmètre évalué :** {{ROUTES,_MODÈLES_ET_VERSIONS_ÉVALUÉS}}
- **Exclus :** {{CE_QUI_N_A_PAS_ÉTÉ_ÉVALUÉ_ET_POURQUOI}}

La présente déclaration constitue une documentation établie à partir d'une évaluation technique. Elle ne vaut ni certification de conformité ni conseil juridique. Seule une évaluation indépendante peut certifier la conformité, et toute question juridique relative à l'applicabilité de la directive (UE) 2019/882 doit être confirmée par un avocat qualifié dans l'État membre concerné.

---

**{{DÉNOMINATION_LÉGALE}}** · {{URL_PAGE_CONTACT}} · Cette déclaration a été publiée le {{DATE_PUBLIÉE}}.
