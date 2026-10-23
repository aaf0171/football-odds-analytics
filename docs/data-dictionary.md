# Dictionnaire des données — Football Odds Analytics

## Source

Football-Data.co.uk — https://www.football-data.co.uk/notes.txt

## Colonnes retenues pour le périmètre 1N2

### Métadonnées du match

| Colonne | Type source | Description | Usage analytique | Disponibilité |
|---|---|---|---|---|
| Div | Texte | Code de la division (`F1` = Ligue 1 française) | Vérification du périmètre | Toutes saisons |
| Date | Texte (`dd/mm/yyyy`) | Date du match | Clé temporelle, tri chronologique | Toutes saisons |
| Time | Texte (`HH:MM`) | Heure du coup d'envoi | Métadonnée, non utilisée en analyse | Toutes saisons |

### Équipes

| Colonne | Type source | Description | Usage analytique | Disponibilité |
|---|---|---|---|---|
| HomeTeam | Texte | Nom de l'équipe à domicile | Identification équipe domicile | Toutes saisons |
| AwayTeam | Texte | Nom de l'équipe à l'extérieur | Identification équipe extérieur | Toutes saisons |

### Résultats

| Colonne | Type source | Description | Usage analytique | Disponibilité |
|---|---|---|---|---|
| FTHG | Entier | Buts marqués par l'équipe à domicile à la fin du match | Calcul de l'issue 1N2 observée | Toutes saisons |
| FTAG | Entier | Buts marqués par l'équipe à l'extérieur à la fin du match | Calcul de l'issue 1N2 observée | Toutes saisons |
| FTR | Texte (`H`, `D`, `A`) | Résultat plein (Home=victoire domicile, Draw=nul, Away=victoire extérieur) | Variable cible 1N2 | Toutes saisons |
| HTHG | Entier | Buts mi-temps à domicile | Analyse half-time/full-time | Toutes saisons |
| HTAG | Entier | Buts mi-temps à l'extérieur | Analyse half-time/full-time | Toutes saisons |
| HTR | Texte (`H`, `D`, `A`) | Résultat mi-temps | Analyse mi-temps/plein temps | Toutes saisons |

### Statistiques de match (hors périmètre 1N2 initial)

| Colonne | Type source | Description | Usage analytique | Disponibilité |
|---|---|---|---|---|
| Attendance | Entier | Affluence au stade | Analyse fréquentielle | Toutes saisons récentes |
| Referee | Texte | Nom de l'arbitre | Analyse par arbitre (futur) | Toutes saisons récentes |
| HS | Entier | Tirs totaux à domicile | Analyse de performance (futur) | Toutes saisons récentes |
| AS | Entier | Tirs totaux à l'extérieur | Analyse de performance (futur) | Toutes saisons récentes |
| HST | Entier | Tirs cadrés à domicile | Analyse de performance (futur) | Toutes saisons récentes |
| AST | Entier | Tirs cadrés à l'extérieur | Analyse de performance (futur) | Toutes saisons récentes |
| HC | Entier | Corners à domicile | Analyse de performance (futur) | Toutes saisons récentes |
| AC | Entier | Corners à l'extérieur | Analyse de performance (futur) | Toutes saisons récentes |
| HY | Entier | Cartons jaunes à domicile | Analyse de performance (futur) | Toutes saisons récentes |
| AY | Entier | Cartons jaunes à l'extérieur | Analyse de performance (futur) | Toutes saisons récentes |
| HR | Entier | Cartons rouges à domicile | Analyse de performance (futur) | Toutes saisons récentes |
| AR | Entier | Cartons rouges à l'extérieur | Analyse de performance (futur) | Toutes saisons récentes |

### Cotes 1N2 — Bookmakers individuels

| Colonne prefix | Bookmaker | Usage analytique | Disponibilité |
|---|---|---|---|
| `B365` | Bet365 | Cotes de référence, bookmaker majeur | Toutes saisons récentes |
| `BWH` | Bet&Win | Cotes comparatives | Toutes saisons récentes |
| `BF` | Betfair | Cotes de la plateforme d'échange | Toutes saisons récentes |
| `PS` | Pinnacle | Cotes du bookmaker "sharp" de référence | Toutes saisons récentes |
| `WH` | William Hill | Cotes du bookmaker historique britannique | Toutes saisons récentes |
| `1XB` | 1XBet | Cotes du bookmaker en croissance | Toutes saisons récentes (depuis ~2016) |

Pour chaque bookmaker, 3 sous-colonnes :
- `H` = cote victoire domicile
- `D` = cote match nul
- `A` = cote victoire extérieur

### Cotes 1N2 — Statistiques du marché

| Colonne | Description | Usage analytique | Disponibilité |
|---|---|---|---|
| `Bb1X2` | Nombre de bookmakers utilisés pour les moyennes du marché | Indicateur de couverture du marché | Toutes saisons récentes |
| `MaxH`, `MaxD`, `MaxA` | Cotes maximales du marché (H/D/A) | Cote la plus offerte par un bookmaker | Toutes saisons récentes |
| `AvgH`, `AvgD`, `AvgA` | Cotes moyennes du marché (H/D/A) | Consensus du marché | Toutes saisons récentes |
| `BFEH`, `BFED`, `BFEA` | Cotes Betfair Exchange (H/D/A) | Cotes issues du marché d'échange, considérées comme très efficaces | Toutes saisons récentes |

### Cotes 1N2 — Cotes de clôture (Closing odds)

| Colonne prefix | Description | Usage analytique | Disponibilité |
|---|---|---|---|
| `B365C` | Cotes de clôture Bet365 | Cotes au moment du coup d'envoi, considérées comme les plus informatives | Toutes saisons récentes |
| `BWCH` | Cotes de clôture Bet&Win | — | Toutes saisons récentes |
| `BFCH` | Cotes de clôture Betfair | — | Toutes saisons récentes |
| `PSCH` | Cotes de clôture Pinnacle | — | Toutes saisons récentes |
| `WHCH` | Cotes de clôture William Hill | — | Toutes saisons récentes |
| `1XBCH` | Cotes de clôture 1XBet | — | Toutes saisons récentes |
| `MaxCH`, `MaxCD`, `MaxCA` | Cotes de clôture maximales du marché | — | Toutes saisons récentes |
| `AvgCH`, `AvgCD`, `AvgCA` | Cotes de clôture moyennes du marché | — | Toutes saisons récentes |
| `BFECH`, `BFEC`, `BFECA` | Cotes de clôture Betfair Exchange | — | Toutes saisons récentes |

## Colonnes non retenues (hors périmètre initial)

- Cotes Over/Under 2.5 (`>2.5`, `<2.5`) : marché différent (nombre de buts, pas 1N2)
- Cotes Asian Handicap (`AHh`, `AHH`) : marché différent
- Statistiques de match (tirs, corners, cartons, etc.) : utiles en phases ultérieures comme features pour les modèles, mais pas dans le périmètre initial 1N2

## Notes sur les variations entre saisons

- Les noms de bookmakers dans les colonnes peuvent varier selon les saisons (certains bookmakers ne sont plus listés).
- Les statistiques de match (tirs, corners, etc.) sont absentes des saisons les plus anciennes.
- Les cotes de clôture sont disponibles à partir d'une certaine saison (à vérifier par saison).
- **Action requise :** confronter les en-têtes de chaque fichier CSV au dictionnaire officiel `notes.txt` pour chaque saison ajoutée.

## Format du fichier CSV

- **Séparateur :** virgule (`,`)
- **Encodage :** UTF-8 avec BOM (Byte Order Mark)
- **Format de date :** `dd/mm/yyyy`
- **Valeurs manquantes :** représentées par chaîne vide dans le CSV (à convertir en `NULL` en SQL)
- **Ligne d'en-tête :** première ligne du fichier

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
| B365H, B365D, B365A | `match_odds` | `home_odds`, `draw_odds`, `away_odds` (bookmaker='bet365') |
| AvgH, AvgD, AvgA | `match_odds` | `home_odds`, `draw_odds`, `away_odds` (bookmaker='market_avg') |
| MaxH, MaxD, MaxA | `match_odds` | `home_odds`, `draw_odds`, `away_odds` (bookmaker='market_max') |
| BFEH, BFED, BFEA | `match_odds` | `home_odds`, `draw_odds`, `away_odds` (bookmaker='betfair_exchange') |
