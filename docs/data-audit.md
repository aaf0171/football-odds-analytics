# Audit des données — Confrontation CSV / dictionnaire Football-Data.co.uk

## Méthodologie

- **Source CSV** : `data/F1_2024-2025.csv` (306 lignes, 119 colonnes)
- **Source dictionnaire** : https://www.football-data.co.uk/notes.txt
- **Écart** : `columns_definitions.txt` (copie locale du dictionnaire)

## Confrontation colonne par colonne

### 1. Colonnes identifiées (matching 1:1)

Toutes les 119 colonnes du CSV correspondent à une entrée du dictionnaire `notes.txt`.

| Colonne | Définition dictionnaire | Statut |
|---|---|---|
| `Div` | Div = League Division | ✅ |
| `Date` | Date = Match Date (dd/mm/yy) | ✅ |
| `Time` | Time = Time of match kick off | ✅ |
| `HomeTeam` | HomeTeam = Home Team | ✅ |
| `AwayTeam` | AwayTeam = Away Team | ✅ |
| `FTHG` | FTHG and HG = Full Time Home Team Goals | ✅ |
| `FTAG` | FTAG and AG = Full Time Away Team Goals | ✅ |
| `FTR` | FTR and Res = Full Time Result | ✅ |
| `HTHG` | HTHG = Half Time Home Team Goals | ✅ |
| `HTAG` | HTAG = Half Time Away Team Goals | ✅ |
| `HTR` | HTR = Half Time Result | ✅ |
| `HS` | HS = Home Team Shots | ✅ |
| `AS` | AS = Away Team Shots | ✅ |
| `HST` | HST = Home Team Shots on Target | ✅ |
| `AST` | AST = Away Team Shots on Target | ✅ |
| `HC` | HC = Home Team Corners | ✅ |
| `AC` | AC = Away Team Corners | ✅ |
| `HF` | HF = Home Team Fouls Committed | ✅ |
| `AF` | AF = Away Team Fouls Committed | ✅ |
| `HY` | HY = Home Team Yellow Cards | ✅ |
| `AY` | AY = Away Team Yellow Cards | ✅ |
| `HR` | HR = Home Team Red Cards | ✅ |
| `AR` | AR = Away Team Red Cards | ✅ |
| `B365H` | B365H = Bet365 home win odds | ✅ |
| `B365D` | B365D = Bet365 draw odds | ✅ |
| `B365A` | B365A = Bet365 away win odds | ✅ |
| `BWH` | BWH = Bet&Win home win odds | ✅ |
| `BWD` | BWD = Bet&Win draw odds | ✅ |
| `BWA` | BWA = Bet&Win away win odds | ✅ |
| `BFH` | BFH = Betfair home win odds | ✅ |
| `BFD` | BFD = Betfair draw odds | ✅ |
| `BFA` | BFA = Betfair away win odds | ✅ |
| `PSH` | PSH and PH = Pinnacle home win odds | ✅ |
| `PSD` | PSD and PD = Pinnacle draw odds | ✅ |
| `PSA` | PSA and PA = Pinnacle away win odds | ✅ |
| `WHH` | WHH = William Hill home win odds | ✅ |
| `WHD` | WHD = William Hill draw odds | ✅ |
| `WHA` | WHA = William Hill away win odds | ✅ |
| `1XBH` | 1XBH = 1XBet home win odds | ✅ |
| `1XBD` | 1XBD = 1XBet draw odds | ✅ |
| `1XBA` | 1XBA = 1XBet away win odds | ✅ |
| `MaxH` | MaxH = Market maximum home win odds | ✅ |
| `MaxD` | MaxD = Market maximum draw win odds | ✅ |
| `MaxA` | MaxA = Market maximum away win odds | ✅ |
| `AvgH` | AvgH = Market average home win odds | ✅ |
| `AvgD` | AvgD = Betbrain average draw win odds | ✅ |
| `AvgA` | AvgA = Betbrain average away win odds | ✅ |
| `BFEH` | BFEH = Betfair Exchange home win odds | ✅ |
| `BFED` | BFED = Betfair Exchange draw odds | ✅ |
| `BFEA` | BFEA = Betfair Exchange away win odds | ✅ |

### 2. Colonnes absentes du CSV (documentées mais non présentes en 2024-25)

| Colonne | Définition | Statut |
|---|---|---|
| `Referee` | Match Referee | ❌ Absente du CSV |
| `HHW` | Home Team Hit Woodwork | ❌ Absente |
| `AHW` | Away Team Hit Woodwork | ❌ Absente |
| `HFKC` | Home Team Free Kicks Conceded | ❌ Absente |
| `AFKC` | Away Team Free Kicks Conceded | ❌ Absente |
| `HO` | Home Team Offsides | ❌ Absente |
| `AO` | Away Team Offsides | ❌ Absente |
| `HBP` | Home Team Bookings Points | ❌ Absente |
| `ABP` | Away Team Bookings Points | ❌ Absente |
| `Bb1X2` | Number of BetBrain bookmakers | ❌ Absente |
| `BbMxH` | Betbrain maximum home win odds | ❌ Absente |
| `BbAvH` | Betbrain average home win odds | ❌ Absente |
| `BbMxD` | Betbrain maximum draw win odds | ❌ Absente |
| `BbAvD` | Betbrain average draw win odds | ❌ Absente |
| `BbMxA` | Betbrain maximum away win odds | ❌ Absente |
| `BbAvA` | Betbrain average away win odds | ❌ Absente |

> **Observation majeure** : Les colonnes `Bb*` (Betbrain) sont absentes du CSV 2024-25. Football-Data ne les inclut plus pour les saisons récentes. Le CSV utilise `Max*` et `Avg*` comme substitut.

### 3. Valeurs manquantes par bookmaker (1N2 ouverture)

| Bookmaker | Colonne | Lignes nulles | % |
|---|---|---|---|
| **Bet&Win** | `BWH`, `BWD`, `BWA` | 117 | 38.2% |
| **William Hill** | `WHH`, `WHD`, `WHA` | 72 | 23.5% |
| **1XBet** | `1XBH`, `1XBD`, `1XBA` | 9 | 2.9% |
| **Bet365** | `B365H`, `B365D`, `B365A` | 0 | 0% |
| **Betfair** | `BFH`, `BFD`, `BFA` | 0 | 0% |
| **Pinnacle** | `PSH`, `PSD`, `PSA` | 0 (PSD: toutes float) | 0% |

### 4. Valeurs manquantes par bookmaker (closing odds)

| Bookmaker | Colonne | Lignes nulles | % |
|---|---|---|---|
| **Bet&Win** | `BWCH`, `BWCD`, `BWCA` | 117 | 38.2% |
| **William Hill** | `WHCH`, `WHCD`, `WHCA` | 72 | 23.5% |
| **1XBet** | `1XBCH`, `1XBCD`, `1XBCA` | 0 (1XBCH: toutes float) | 0% |
| **Bet365** | `B365CH`, `B365CD`, `B365CA` | 0 | 0% |
| **Betfair** | `BFCH`, `BFCD`, `BFCA` | 0 | 0% |
| **Pinnacle** | `PSCH`, `PSCD`, `PSCA` | 0 (PSCD: toutes float) | 0% |

### 5. Valeurs manquantes hors 1N2

| Colonne | Lignes nulles | % |
|---|---|---|
| `P>2.5`, `P<2.5` (Pinnacle OU) | 2 | 0.7% |
| `PC>2.5`, `PC<2.5` (Pinnacle OU C) | 2 | 0.7% |
| `BFE>2.5`, `BFE<2.5` (Betfair OU) | 5 | 1.6% |
| `BFEAHH`, `BFEAHA` (Betfair AH) | 3 | 1.0% |
| `BFECAHH`, `BFECAHA` (Betfair AH C) | 0 | 0% |

### 6. Formats et types détectés

| Colonne | Type(s) détecté(s) | Format | Exemple |
|---|---|---|---|
| `Div` | str | code compétition | `F1` |
| `Date` | str | `dd/mm/yyyy` (ex: `16/08/2024`) | `16/08/2024` |
| `Time` | str | `HH:MM` (24h) | `19:45` |
| `HomeTeam`, `AwayTeam` | str | nom d'équipe | `Le Havre` |
| `FTHG`, `FTAG` | int | buts | `2` |
| `FTR` | char | `H`, `D`, `A` | `A` |
| `HTHG`, `HTAG` | int | buts mi-temps | `1` |
| `HTR` | char | `H`, `D`, `A` | `A` |
| Stats (`HS`, `AS`...) | int | compteur | `14` |
| Cotes (`B365H`, etc.) | float ou int | décimales | `2.10`, `2` |
| Moyennes (`AvgH`) | float | décimales | `2.1234` |

### 7. Conventions de nommage

| Suffixe | Signification | Exemple |
|---|---|---|
| `H` / `D` / `A` | Home / Draw / Away | `B365H`, `B365D`, `B365A` |
| `C` après bookmaker | Closing odds (cotes de clôture) | `B365CH` |
| `>2.5` / `<2.5` | Over / Under 2.5 buts | `B365>2.5` |
| `C>2.5` / `C<2.5` | Closing Over / Under | `B365C>2.5` |
| `AH` | Asian Handicap | `PAHH`, `PAHA` |
| `AHCh` | Closing Asian Handicap | `AHCh` |

## Limites et précautions

1. **Absence de `Referee`** : colonne arbitre non incluse dans les CSV récents. Impacte l'analyse de l'impact arbitral sur les cotes.
2. **Absence de `Bb*`** : métriques Betbrain supprimées. Utiliser `Max*` et `Avg*` comme substituts.
3. **Données de bois touchés** (`HHW`/`AHW`) non disponibles.
4. **Bookings Points** (`HBP`/`ABP`) non disponibles (seules les cartes sont présentes).
5. **Free Kicks Conceded** (`HFKC`/`AFKC`) non disponibles.
6. **Offsides** (`HO`/`AO`) non disponibles.
7. **Covariance bookmaker / saison** : Bet&Win absent pour 38.2% des matchs (117/306). William Hill absent pour 23.5% (72/306). Vérifier au cas par cas par saison.

## Script d'inspection

Un script Python utilisant uniquement le standard library est disponible :

```bash
python3 data/F1_2024-2025_inspection.py
```

Pour une saison différente :

```bash
python3 data/F1_2024-2025_inspection.py data/F1_2023-2024.csv
```

## Critère d'acceptation vérifié

- ✅ **Une saison peut être lue avec un script Python simple** : `data/F1_2024-2025_inspection.py` fonctionne avec uniquement `csv` et `collections` (standard library).
- ✅ **Source et conditions d'utilisation documentées** : `docs/data-source.md`
- ✅ **Colonnes identifiées et confrontées** : cette fiche
- ✅ **Limites et valeurs manquantes connues** : section "Limites et précautions"
