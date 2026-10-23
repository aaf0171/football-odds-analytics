# Note de cadrage — Ticket T1

## Récapitulatif des décisions

| Décision | Valeur retenue |
|---|---|
| Source de données | Football-Data.co.uk |
| Compétition | Ligue 1 française (code `F1`) |
| Saisons | 2024-2025 (priorité), 2023-2024, 2022-2023 |
| Marché | 1N2 (victoire domicile, nul, victoire extérieur) |
| Bookmakers cibles | Bet365, Betfair Exchange, Pinnacle, Bet&Win, William Hill, 1XBet |
| Cotes d'intérêt | Ouverture (H/D/A), moyennes/max du marché, Betfair Exchange, clôture |
| Questions analytiques | Voir `docs/methodology.md` |
| Conditions d'utilisation | Usage personnel/analyse uniquement, pas de redistribution |

## Découvertes de l'audit

### Colonnes manquantes dans le CSV 2024-25
- **16 colonnes absentes** : `Referee`, `HHW`, `AHW`, `HFKC`, `AFKC`, `HO`, `AO`, `HBP`, `ABP`, `Bb1X2`, `BbMxH`, `BbAvH`, `BbMxD`, `BbAvD`, `BbMxA`, `BbAvA`
- Les métriques Betbrain (`Bb*`) ont été supprimées des CSV récents — utiliser `Max*` / `Avg*` comme substitut.

### Disponibilité bookmakers (1N2 ouverture)
| Bookmaker | Couverture | Commentaire |
|---|---|---|
| Bet365 | 100% (306/306) | — |
| Betfair | 100% | — |
| Pinnacle | 100% (PSD: toutes float) | — |
| 1XBet | 97.1% (297/306) | 9 matchs sans cotes |
| William Hill | 76.5% (234/306) | 72 matchs sans cotes |
| Bet&Win | 61.8% (189/306) | 117 matchs sans cotes |

### Formats
- Date : `dd/mm/yyyy` (ex: `16/08/2024`) — attention, année sur 4 chiffres (contrairement au dictionnaire qui indique `dd/mm/yy`)
- Cotes : décimales (int ou float)
- Resultats : `H`, `D`, `A`

## Critères d'acceptation T1

- [x] Source et conditions d'utilisation documentées (`docs/data-source.md`)
- [x] Colonnes nécessaires identifiées et confrontées au dictionnaire officiel (`docs/data-dictionary.md`)
- [x] Limites et valeurs manquantes connues (`docs/data-audit.md`)
- [x] Une saison peut être lue avec un script Python simple (`data/F1_2024-2025_inspection.py`)
- [x] CSV de la saison 2024-2025 téléchargé et inspecté (`data/F1_2024-2025.csv`, 306 matchs, 119 colonnes)
- [x] Questions analytiques définies (`docs/methodology.md`)

## Livrables T1

| Fichier | Description |
|---|---|
| `docs/data-source.md` | Source, license, compétition, saisons, marché |
| `docs/data-dictionary.md` | Dictionnaire des colonnes avec mappage SQL |
| `docs/data-audit.md` | Confrontation CSV / dictionnaire, valeurs manquantes |
| `docs/methodology.md` | Questions analytiques et approche |
| `docs/notes-de-cadrage.md` | Cette fiche |
| `data/F1_2024-2025.csv` | Échantillon de données |
| `data/F1_2024-2025_inspection.py` | Script Python standard library pour inspection |
| `data/README.md` | Instructions d'obtention des données |
| `.gitignore` | Exclusion des données brutes et artifacts |

## Prochaines étapes (T2 — Étudier le CSV source)

- [ ] Comparer les en-têtes entre saisons (2024-25, 2023-24, 2022-23)
- [ ] Documenter les variations de schéma entre saisons
- [ ] Identifier les colonnes non documentées ou ambiguës
- [ ] Vérifier la consistance des noms d'équipes
- [ ] Préparer le modèle SQL pour la table `matches` et `odds`
