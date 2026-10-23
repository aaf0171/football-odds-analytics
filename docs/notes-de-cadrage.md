# Note de cadrage — Football Odds Analytics

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

## Découvertes de T1 — Audit

### Colonnes manquantes dans le CSV 2024-25
- **16 colonnes absentes** : `Referee`, `HHW`, `AHW`, `HFKC`, `AFKC`, `HO`, `AO`, `HBP`, `ABP`, `Bb1X2`, `BbMxH`, `BbAvH`, `BbMxD`, `BbAvD`, `BbMxA`, `BbAvA`
- Les métriques Betbrain (`Bb*`) sont supprimées des CSV récents — utiliser `Max*` / `Avg*` comme substitut.

### Disponibilité bookmakers 1N2 ouverture (2024-25)
| Bookmaker | Couverture |
|---|---|
| Bet365 | 100% (306/306) |
| Betfair | 100% |
| Pinnacle | 100% |
| 1XBet | 97,1% (297/306) |
| William Hill | 76,5% (234/306) |
| Bet&Win | 61,8% (189/306) |

### Formats
- Date : `dd/mm/yyyy` (4 chiffres — contrairement au dictionnaire officiel `dd/mm/yy`)
- Cotes : décimales (int ou float)
- Résultats : `H`, `D`, `A`

## Découvertes de T2 — Comparaison inter-saisons

### Schémas différents
- **2024-25** : 119 colonnes (6 bookmakers ouverture + 6 clôture, incluant `BF`, `1XB`, `BFE`)
- **2023-24** : 105 colonnes (4 bookmakers ouverture + 6 clôture, incluant `IW`, `VC`)
- **2022-23** : 105 colonnes (4 bookmakers ouverture + 6 clôture, incluant `IW`, `VC`)

### 93 colonnes communes à toutes les saisons
Ce sont les colonnes de référence du pipeline.

### Bookmakers saisonniers
- **Betfair (`BF`)**, **1XBet (`1XB`)**, **Betfair Exchange (`BFE`)** : uniquement 2024-25
- **Interwetten (`IW`)**, **VC Bet (`VC`)** : 2022-23 et 2023-24 uniquement

### Noms d'équipes
- Noms stables au sein d'une saison
- **13 équipes** présentes dans les 3 saisons
- `Paris SG` (et non `Paris Saint-Germain`)
- Montées/descentes changent la composition entre saisons

### Couverture bookmakers par saison
| Bookmaker | 2024-25 | 2023-24 | 2022-23 |
|---|---|---|---|
| Bet365 | 100% | 100% | 100% |
| William Hill | 76,5% | 100% | 100% |
| Pinnacle | 100% | 100% | 100% |
| Bet&Win | 61,8% | ~100% | ~100% |
| Betfair | 100% | N/A | N/A |
| 1XBet | 97,1% | N/A | N/A |
| Interwetten | N/A | ~100% | ~100% |
| VC Bet | N/A | ~100% | ~100% |

## Critères d'acceptation T1

- [x] Source et conditions d'utilisation documentées (`docs/data-source.md`)
- [x] Colonnes nécessaires identifiées et confrontées au dictionnaire officiel (`docs/data-dictionary.md`)
- [x] Limites et valeurs manquantes connues (`docs/data-audit.md`)
- [x] Une saison peut être lue avec un script Python simple (`data/F1_2024-2025_inspection.py`)
- [x] CSV de la saison 2024-2025 téléchargé et inspecté (`data/F1_2024-2025.csv`, 306 matchs, 119 colonnes)
- [x] Questions analytiques définies (`docs/methodology.md`)

## Critères d'acceptation T2

- [x] Dictionnaire de données mis à jour avec toutes les saisons (`docs/data-dictionary.md`)
- [x] Variations de schéma documentées (`docs/data-schema-variations.md`)
- [x] 3 CSV téléchargés et inspectés : 2024-25, 2023-24, 2022-23
- [x] Script de comparaison inter-saisons (`data/compare_seasons.py`)
- [x] Mapping bookmakers CSV → SQL identifié
- [x] 93 colonnes communes identifiées comme colonne vertébrale du pipeline

## Prochaines étapes (T3 — Définir le modèle relationnel)

- [ ] Définir tables `teams`, `matches`, `match_odds`, `etl_runs`
- [ ] Définir clés primaires, étrangères, contraintes
- [ ] Créer `sql/schema.sql`
- [ ] Définir stratégie de déduplication des matchs
- [ ] Créer diagramme relationnel
- [ ] Configurer Docker Compose pour MariaDB (`compose.yaml`)
- [ ] Créer `docs/architecture.md`

## Livrables T1

| Fichier | Description |
|---|---|
| `docs/data-source.md` | Source, license, compétition, saisons, marché |
| `docs/data-dictionary.md` | Dictionnaire des colonnes avec mappage SQL (mis à jour T2) |
| `docs/data-audit.md` | Confrontation CSV / dictionnaire, valeurs manquantes |
| `docs/methodology.md` | Questions analytiques et approche |
| `docs/notes-de-cadrage.md` | Cette fiche |
| `data/F1_2024-2025.csv` | Échantillon de données (306 matchs) |
| `data/F1_2023-2024.csv` | Données saison 2023-24 (306 matchs) |
| `data/F1_2022-2023.csv` | Données saison 2022-23 (380 matchs) |
| `data/F1_2024-2025_inspection.py` | Script Python standard library pour inspection |
| `data/compare_seasons.py` | Script Python de comparaison inter-saisons |
| `data/README.md` | Instructions d'obtention des données |
| `docs/data-schema-variations.md` | Variations de schéma entre saisons (T2) |
| `.gitignore` | Exclusion des données brutes et artifacts |
