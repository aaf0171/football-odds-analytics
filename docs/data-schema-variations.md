# Variations de schéma entre saisons — Ligue 1

## Source

Football-Data.co.uk — https://www.football-data.co.uk/francem.php
Dictionnaire officiel : https://www.football-data.co.uk/notes.txt

## Résumé par saison

| Saison | Lignes | Colonnes | Bookmakers ouverture | Bookmakers clôture |
|---|---|---|---|---|
| 2024-2025 | 306 | 119 | BF, WH, 1XB, BW, PS, B365 | BFE, 1XB, WH, PS, BW, B365 |
| 2023-2024 | 306 | 105 | IWH/IWD/IWA, VCH/VCD/VCA, WH, PS, B365 | BW, PS, WH, IW, VC, B365 |
| 2022-2023 | 380 | 105 | IWH/IWD/IWA, VCH/VCD/VCA, WH, PS, B365 | BW, PS, WH, IW, VC, B365 |

**Note :** La saison 2022-2023 a 380 lignes (au lieu de 306 = 34×18÷2) car la Ligue 1 comptait 20 équipes cette saison-là. Les saisons 2023-24 et 2024-25 comptent 18 équipes (306 matchs).

## Bookmakers — Changements majeurs

### Ouverture (pre-closing odds)

| Bookmaker | Abréviation | 2024-25 | 2023-24 | 2022-23 | Commentaire |
|---|---|---|---|---|---|
| Betfair | `BF` | ✅ 100% | ❌ | ❌ | Apparu en 2024-25 |
| William Hill | `WH` | ✅ 76,5% | ✅ | ✅ | Consistant |
| 1XBet | `1XB` | ✅ 97,1% | ❌ | ❌ | Apparu en 2024-25 |
| Bet&Win | `BW` | ❌ (clôture) | ✅ (clôture) | ✅ (clôture) | Déplacé en clôture 2024-25 |
| Pinnacle | `PS` | ✅ 100% | ✅ | ✅ | Toujours présent |
| Bet365 | `B365` | ✅ 100% | ✅ | ✅ | Toujours présent |
| Interwetten | `IW` | ❌ | ✅ | ✅ | Absent depuis 2024-25 |
| VC Bet | `VC` | ❌ | ✅ | ✅ | Absent depuis 2024-25 (VC Bet → BetVictor) |
| Betbrain | `Bb` | ❌ | ❌ | ❌ | Métriques Betbrain supprimées depuis longtemps |

**Implication pour le pipeline :** Il faut mapper les bookmakers par saison. La clé `bookmaker` en base de données doit accepter les noms lisibles (`"betfair"`, `"william_hill"`, etc.), pas les préfixes CSV.

### Clôture (closing odds)

| Bookmaker | Abréviation | 2024-25 | 2023-24 | 2022-23 | Commentaire |
|---|---|---|---|---|---|
| Betfair Exchange | `BFE` | ✅ 100% | ❌ | ❌ | Apparu en 2024-25 |
| 1XBet | `1XB` | ✅ ~100% | ❌ | ❌ | Apparu en 2024-25 |
| William Hill | `WH` | ✅ 76,5% | ✅ | ✅ | Consistant |
| Pinnacle | `PS` | ✅ 100% | ✅ | ✅ | Toujours présent |
| Bet&Win | `BW` | ✅ 61,8% | ✅ | ✅ | Toujours présent |
| Bet365 | `B365` | ✅ 100% | ✅ | ✅ | Toujours présent |
| Interwetten | `IW` | ❌ | ✅ | ✅ | Absent depuis 2024-25 |
| VC Bet | `VC` | ❌ | ✅ | ✅ | Absent depuis 2024-25 |

## Colonnes absentes dans certaines saisons

### 2024-25 uniquement (14 colonnes supplémentaires)

Ces colonnes sont **exclusives** à la saison 2024-25 :

| Colonne | Bookmaker | Type |
|---|---|---|
| `BFH`, `BFD`, `BFA` | Betfair (ouverture) | 1N2 |
| `1XBH`, `1XBD`, `1XBA` | 1XBet (ouverture) | 1N2 |
| `BFEH`, `BFED`, `BFEA` | Betfair Exchange (ouverture) | 1N2 |
| `BFE>2.5`, `BFE<2.5` | Betfair Exchange O/U 2.5 | Over/Under |
| `BFCH`, `BFCD`, `BFCA` | Betfair (clôture) | 1N2 |
| `1XBCH`, `1XBCD`, `1XBCA` | 1XBet (clôture) | 1N2 |
| `BFECAHH`, `BFECAHA` | Betfair Exchange AH clôture | Asian Handicap |

**Raison :** Betfair, 1XBet et Betfair Exchange ont été ajoutés aux CSV récents.

### 2023-24 et 2022-23 uniquement (14 colonnes)

Ces colonnes sont **exclusives** à 2023-24 et 2022-23 :

| Colonne | Bookmaker | Type |
|---|---|---|
| `IWH`, `IWD`, `IWA` | Interwetten (ouverture) | 1N2 |
| `VCH`, `VCD`, `VCA` | VC Bet (ouverture) | 1N2 |
| `IWCH`, `IWCD`, `IWCA` | Interwetten (clôture) | 1N2 |
| `VCCH`, `VCCD`, `VCCA` | VC Bet (clôture) | 1N2 |

**Note :** Interwetten et VC Bet sont absents de 2024-25.

### Colonnes communes à toutes les saisons

Les 93 colonnes suivantes sont **présentes dans les 3 saisons**. Ce sont les colonnes de référence pour le pipeline :

`Div`, `Date`, `Time`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`, `FTR`, `HTHG`, `HTAG`, `HTR`,
`HS`, `AS`, `HST`, `AST`, `HF`, `AF`, `HC`, `AC`, `HY`, `AY`, `HR`, `AR`,
`B365H`, `B365D`, `B365A`,
`BWH`, `BWD`, `BWA`,
`PSH`, `PSD`, `PSA`,
`WHH`, `WHD`, `WHA`,
`MaxH`, `MaxD`, `MaxA`,
`AvgH`, `AvgD`, `AvgA`,
`B365>2.5`, `B365<2.5`, `P>2.5`, `P<2.5`,
`Max>2.5`, `Max<2.5`, `Avg>2.5`, `Avg<2.5`,
`AHh`, `B365AHH`, `B365AHA`, `PAHH`, `PAHA`,
`MaxAHH`, `MaxAHA`, `AvgAHH`, `AvgAHA`,
`B365CH`, `B365CD`, `B365CA`,
`BWCH`, `BWCD`, `BWCA`,
`PSCH`, `PSCD`, `PSCA`,
`WHCH`, `WHCD`, `WHCA`,
`MaxCH`, `MaxCD`, `MaxCA`,
`AvgCH`, `AvgCD`, `AvgCA`,
`B365C>2.5`, `B365C<2.5`, `PC>2.5`, `PC<2.5`,
`MaxC>2.5`, `MaxC<2.5`, `AvgC>2.5`, `AvgC<2.5`,
`AHCh`, `B365CAHH`, `B365CAHA`, `PCAHH`, `PCAHA`,
`MaxCAHH`, `MaxCAHA`, `AvgCAHH`, `AvgCAHA`

## Colonnes systématiquement absentes (toutes saisons)

| Colonne | Description | Statut |
|---|---|---|
| `Referee` | Arbitre du match | Jamais en F1 récentes |
| `HHW` / `AHW` | Touches (hit woodwork) | Jamais en F1 |
| `HFKC` / `AFKC` | Coups francs concédés | Jamais en F1 |
| `HO` / `AO` | Hors-jeux | Jamais en F1 |
| `HBP` / `ABP` | Points de sanctions | Jamais en F1 |
| `Bb1X2` | Nombre de bookmakers Betbrain | Supprimé des CSV récents |
| `BbMxH`, `BbAvH`, `BbMxD`, `BbAvD`, `BbMxA`, `BbAvA` | Métriques Betbrain | Supprimé des CSV récents |
| `Attendance` | Affluence | Jamais en F1 |

**Conséquence :** Les statistiques de match disponibles sont limitées à :
`tirs, tirs cadrés, corners, fautes, cartons jaunes, cartons rouges`

## Noms d'équipes — Consistance

### Équipes présentes dans les 3 saisons (12)

`Brest`, `Lens`, `Lille`, `Lyon`, `Marseille`, `Monaco`, `Nantes`, `Nice`, `Paris SG`, `Reims`, `Rennes`, `Strasbourg`, `Toulouse`

### Équipes mutées

| Équipe | 2022-23 | 2023-24 | 2024-25 | Statut |
|---|---|---|---|---|
| Paris SG | ✅ | ✅ | ✅ | Stable |
| St Etienne | ❌ | ❌ | ✅ | Relégué 2021-22, remonté 2024-25 |
| Angers | ✅ | ❌ | ✅ | Monté 2022-23, relégué 2023-24, remonté 2024-25 |
| Auxerre | ✅ | ❌ | ✅ | Monté 2022-23, relégué 2023-24, remonté 2024-25 |
| Lorient | ✅ | ✅ | ❌ | Relégué 2023-24 |
| Clermont | ✅ | ✅ | ❌ | Relégué 2023-24 |
| Metz | ❌ | ✅ | ❌ | Promu 2023-24, relégué 2024-25 |
| Le Havre | ❌ | ✅ | ✅ | Promu 2023-24 |
| Ajaccio | ✅ | ❌ | ❌ | Relégué 2022-23 |
| Troyes | ✅ | ❌ | ❌ | Relégué 2022-23 |

**Conséquence :** Les noms d'équipes sont **consistants au sein d'une saison** mais les équipes changent entre saisons. La table `teams` doit avoir un `name` et potentiellement un `source_team_name` pour gérer les variations. `Paris SG` (et non `Paris Saint-Germain`) est le nom utilisé.

## Formats de date

| Saison | Format | Exemple |
|---|---|---|
| 2024-25 | `dd/mm/yyyy` | `16/08/2024` |
| 2023-24 | `dd/mm/yyyy` | `16/08/2023` |
| 2022-23 | `dd/mm/yyyy` | `16/08/2022` |

**Note :** Le dictionnaire officiel (`notes.txt`) indique `dd/mm/yy` (2 chiffres pour l'année), mais en pratique c'est `dd/mm/yyyy` (4 chiffres). Les scripts doivent gérer les 4 chiffres.

## Implications pour le modèle SQL

1. **La table `match_odds` doit accepter des bookmakers variés selon la saison.** La colonne `bookmaker` doit être une chaîne de caractères lisible.
2. **Le pipeline d'ingestion doit mapper les préfixes CSV → noms de bookmakers :**
   - `BF` → `betfair` (2024-25 uniquement)
   - `1XB` → `1xbet` (2024-25 uniquement)
   - `BFE` → `betfair_exchange` (2024-25 uniquement)
   - `IW` → `interwetten` (2022-23, 2023-24 uniquement)
   - `VC` → `vc_bet` (2022-23, 2023-24 uniquement)
   - `B365` → `bet365`
   - `BWH` → `betandwin`
   - `PS` → `pinnacle`
   - `WH` → `william_hill`
3. **Les colonnes de clôture sont présentes dans les 3 saisons** — la table `match_odds` doit avoir un champ `odds_type` (ex: `"opening"`, `"closing"`).
4. **Les bookmakers absents d'une saison seront NULL dans la table `match_odds`** — c'est le comportement attendu et documenté.
5. **Les statistiques de match sont limitées** dans F1 (pas d'arbitre, pas de corners détaillés au-delà du count, etc.).

## Recommandations

- Utiliser les **93 colonnes communes** comme colonne vertébrale du pipeline.
- Les **colonnes saisonnières** (`BF`, `1XB`, `BFE`, `IW`, `VC`) doivent être traitées avec un mapping par saison.
- La **clé de déduplication** peut être `(competition, match_date, home_team, away_team)` — les dates sont uniques pour un match en Ligue 1.
- Les **noms d'équipes** sont stables dans le CSV, mais une table de correspondance `teams` avec un `source_team_name` est recommandée pour les futures saisons.
