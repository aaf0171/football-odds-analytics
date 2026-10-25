# Dictionnaire des données — Football Odds Analytics

## Source

Football-Data.co.uk — https://www.football-data.co.uk/notes.txt

## Couverture des saisons

| Saison | Lignes | Colonnes | Bookmakers ouverture | Bookmakers clôture |
|---|---|---|---|---|
| 2024-2025 | 306 | 119 | BF, WH, 1XB, BW, PS, B365 | BFE, 1XB, WH, PS, BW, B365 |
| 2023-2024 | 306 | 105 | IWH/IWD/IWA, VCH/VCD/VCA, WH, PS, B365 | BW, PS, WH, IW, VC, B365 |
| 2022-2023 | 380 | 105 | IWH/IWD/IWA, VCH/VCD/VCA, WH, PS, B365 | BW, PS, WH, IW, VC, B365 |

**Note 2022-23 :** 380 lignes car la Ligue 1 comptait 20 équipes cette saison.

**Note :** 306 = 34×18÷2 pour les saisons à 18 équipes (34 journées × 18 matchs/journée ÷ 2 équipes par match).

Pour les détails complets des variations, voir `docs/data-schema-variations.md`.

## Colonnes retenues pour le périmètre 1N2

### Métadonnées du match

| Colonne | Type source | Description | Usage analytique | Saisons |
|---|---|---|---|---|
| Div | Texte | Code de la division (`F1` = Ligue 1 française) | Vérification du périmètre | Toutes |
| Date | Texte (`dd/mm/yyyy`) | Date du match | Clé temporelle, tri chronologique | Toutes |
| Time | Texte (`HH:MM`) | Heure du coup d'envoi | Métadonnée, non utilisée en analyse | Toutes |

### Équipes

| Colonne | Type source | Description | Usage analytique | Saisons |
|---|---|---|---|---|
| HomeTeam | Texte | Nom de l'équipe à domicile | Identification équipe domicile (join `teams`) | Toutes |
| AwayTeam | Texte | Nom de l'équipe à l'extérieur | Identification équipe extérieur (join `teams`) | Toutes |

**Noms d'équipes :** `Paris SG` (et non `Paris Saint-Germain`), `Le Havre`, `St Etienne`, etc. Les noms sont stables au sein d'une saison mais les équipes changent entre saisons (montées, descentes).

### Résultats

| Colonne | Type source | Description | Usage analytique | Saisons |
|---|---|---|---|---|
| FTHG | Entier | Buts à domicile FT | Calcul de l'issue 1N2 | Toutes |
| FTAG | Entier | Buts à l'extérieur FT | Calcul de l'issue 1N2 | Toutes |
| FTR | Texte (`H`, `D`, `A`) | Résultat plein | Variable cible 1N2 | Toutes |
| HTHG | Entier | Buts mi-temps domicile | Analyse mi-temps/plein | Toutes |
| HTAG | Entier | Buts mi-temps extérieur | Analyse mi-temps/plein | Toutes |
| HTR | Texte (`H`, `D`, `A`) | Résultat mi-temps | Analyse HT/FT | Toutes |

### Statistiques de match (hors périmètre 1N2 initial)

| Colonne | Type source | Description | Usage analytique | Saisons |
|---|---|---|---|---|
| HS | Entier | Tirs totaux domicile | Performance (futur) | Toutes |
| AS | Entier | Tirs totaux extérieur | Performance (futur) | Toutes |
| HST | Entier | Tirs cadrés domicile | Performance (futur) | Toutes |
| AST | Entier | Tirs cadrés extérieur | Performance (futur) | Toutes |
| HF | Entier | Fautes domicile | Performance (futur) | Toutes |
| AF | Entier | Fautes extérieur | Performance (futur) | Toutes |
| HC | Entier | Corners domicile | Performance (futur) | Toutes |
| AC | Entier | Corners extérieur | Performance (futur) | Toutes |
| HY | Entier | Cartons jaunes domicile | Performance (futur) | Toutes |
| AY | Entier | Cartons jaunes extérieur | Performance (futur) | Toutes |
| HR | Entier | Cartons rouges domicile | Performance (futur) | Toutes |
| AR | Entier | Cartons rouges extérieur | Performance (futur) | Toutes |

**Colonnes statistiquement absentes de F1 :** `Referee`, `HHW`, `AHW`, `HFKC`, `AFKC`, `HO`, `AO`, `HBP`, `ABP`, `Attendance` — jamais présentes dans les CSV Ligue 1 récentes.

**Colonnes Betbrain absentes :** `Bb1X2`, `BbMxH`, `BbAvH`, `BbMxD`, `BbAvD`, `BbMxA`, `BbAvA` — supprimées des CSV récents. Utiliser `Max*` / `Avg*` comme substitut.

## Bookmakers — Abréviations CSV → noms internes

Le pipeline doit mapper les préfixes CSV vers des noms lisibles pour la base de données :

| Préfixe CSV | Bookmaker | Nom interne SQL | Saisons |
|---|---|---|---|
| `B365` | Bet365 | `bet365` | Toutes |
| `BWH` / `BW` | Bet&Win | `betandwin` | Toutes |
| `BF` | Betfair | `betfair` | 2024-25 uniquement |
| `BFE` | Betfair Exchange | `betfair_exchange` | 2024-25 uniquement |
| `PS` | Pinnacle | `pinnacle` | Toutes |
| `WH` | William Hill | `william_hill` | Toutes |
| `1XB` | 1XBet | `1xbet` | 2024-25 uniquement |
| `IW` | Interwetten | `interwetten` | 2022-23, 2023-24 uniquement |
| `VC` | VC Bet | `vc_bet` | 2022-23, 2023-24 uniquement |

Pour chaque bookmaker, 3 sous-colonnes :
- `H` = cote victoire domicile
- `D` = cote match nul
- `A` = cote victoire extérieur

**Couverture bookmakers 1N2 ouverture (2024-25) :**

| Bookmaker | Couverture |
|---|---|
| Bet365 | 100% (306/306) |
| Betfair | 100% |
| Pinnacle | 100% (PSD: toutes float) |
| 1XBet | 97,1% (297/306) |
| William Hill | 76,5% (234/306) |
| Bet&Win | 61,8% (189/306) |

## Cotes de marché

| Colonne | Description | Usage analytique | Saisons |
|---|---|---|---|
| `MaxH`, `MaxD`, `MaxA` | Cotes maximales du marché (H/D/A) | Cote la plus offerte | Toutes |
| `AvgH`, `AvgD`, `AvgA` | Cotes moyennes du marché (H/D/A) | Consensus du marché | Toutes |

## Cotes de clôture (Closing odds)

| Colonne prefix | Description | Usage analytique | Saisons |
|---|---|---|---|
| `B365C` | Cotes de clôture Bet365 | Références (coup d'envoi) | Toutes |
| `BWCH` | Cotes de clôture Bet&Win | — | Toutes |
| `PSCH` | Cotes de clôture Pinnacle | — | Toutes |
| `WHCH` | Cotes de clôture William Hill | — | Toutes |
| `1XBCH` | Cotes de clôture 1XBet | — | 2024-25 uniquement |
| `BFCH` | Cotes de clôture Betfair | — | 2024-25 uniquement |
| `IWCH` | Cotes de clôture Interwetten | — | 2022-23, 2023-24 |
| `VCCH` | Cotes de clôture VC Bet | — | 2022-23, 2023-24 |
| `MaxCH`, `MaxCD`, `MaxCA` | Cotes de clôture maximales | — | Toutes |
| `AvgCH`, `AvgCD`, `AvgCA` | Cotes de clôture moyennes | — | Toutes |
| `BFECH` | Cotes de clôture Betfair Exchange | — | 2024-25 uniquement |

**Note :** Les cotes de clôture sont considérées comme les plus informatives car elles reflètent l'ensemble de l'information disponible au moment du coup d'envoi.

## Colonnes non retenues (hors périmètre initial)

- Cotes Over/Under 2.5 (`>2.5`, `<2.5`) : marché différent
- Cotes Asian Handicap (`AHh`, `AHH`) : marché différent
- Statistiques de match (tirs, corners, cartons) : utiles en phases ultérieures comme features pour les modèles

## Champs calculés (Phase 7 / T7)

### Issue 1N2 (`result_1n2`)

Dérivée des scores finaux dans `pipeline/transform.py` et la vue `v_match_results` :

| Source | Calcul | Valeur |
|---|---|---|
| `home_goals > away_goals` | — | `H` |
| `home_goals = away_goals` | — | `D` |
| `home_goals < away_goals` | — | `A` |
| `home_goals` ou `away_goals` est `NULL` | — | `NULL` |

### Probabilités implicites brutes

Calculées dans `pipeline/transform.py` et la vue `v_implicit_probabilities` :

| Champ SQL / Python | Formule |
|---|---|
| `prob_home_raw` | `1 / home_odds` |
| `prob_draw_raw` | `1 / draw_odds` |
| `prob_away_raw` | `1 / away_odds` |

Si une cote est `NULL`, nulle ou négative, la probabilité brute correspondante est `NULL`.

### Probabilités implicites normalisées

Calculées dans `pipeline/transform.py` et la vue `v_implicit_probabilities` :

| Champ SQL / Python | Formule |
|---|---|
| `prob_home_norm` | `(1/home_odds) / (1/home + 1/draw + 1/away)` |
| `prob_draw_norm` | `(1/draw_odds) / (1/home + 1/draw + 1/away)` |
| `prob_away_norm` | `(1/away_odds) / (1/home + 1/draw + 1/away)` |

Calculées uniquement lorsque les trois cotes sont valides. Sinon, toutes sont `NULL`.

### Marge du bookmaker

| Champ SQL | Formule |
|---|---|
| `bookmaker_margin` | `(1/home + 1/draw + 1/away) - 1` |

En pourcentage, représente le pourcentage théorique perdu par un parieur sur des mises équilibrées.

## Mappage vers le modèle relationnel

| Colonne CSV | Table cible | Colonne SQL |
|---|---|---|
| Div | `matches` | `competition` |
| Date | `matches` | `match_date` (conversion en DATE) |
| HomeTeam | `matches` | `home_team` (join vers `teams`) |
| AwayTeam | `matches` | `away_team` (join vers `teams`) |
| FTHG | `matches` | `home_goals` |
| FTAG | `matches` | `away_goals` |
| FTR | `matches` | `result_1n2` (optionnel, dérivable) |
| B365H, B365D, B365A | `match_odds` | `home_odds`, `draw_odds`, `away_odds` (`bookmaker='bet365'`) |
| AvgH, AvgD, AvgA | `match_odds` | `home_odds`, `draw_odds`, `away_odds` (`bookmaker='market_avg'`) |
| MaxH, MaxD, MaxA | `match_odds` | `home_odds`, `draw_odds`, `away_odds` (`bookmaker='market_max'`) |
| BFEH, BFED, BFEA | `match_odds` | `home_odds`, `draw_odds`, `away_odds` (`bookmaker='betfair_exchange'`) |

## Formats du fichier CSV

- **Séparateur :** virgule (`,`)
- **Encodage :** UTF-8 avec BOM (Byte Order Mark)
- **Format de date :** `dd/mm/yyyy` (4 chiffres — contrairement au dictionnaire officiel qui indique `dd/mm/yy`)
- **Valeurs manquantes :** chaîne vide dans le CSV (→ `NULL` en SQL)
- **Ligne d'en-tête :** première ligne du fichier
- **Ordre des colonnes :** identique sur toutes les saisons pour les 93 colonnes communes
