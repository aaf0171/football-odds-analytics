# Requêtes analytiques

Ce dossier contient les vues SQL créées lors de la Phase 7 (T7).

## Vues disponibles

### `01_match_results.sql` — Issue 1N2 calculée

Calcule l'issue 1N2 à partir des scores finaux :

| Vue | Description |
|---|---|
| `v_match_results` | Matchs avec issue 1N2 dérivée des scores (H/D/A/NULL) |

L'issue est calculée uniquement lorsque les deux scores sont disponibles :
- `H` : `home_goals > away_goals`
- `D` : `home_goals = away_goals`
- `A` : `home_goals < away_goals`
- `NULL` : un ou les deux scores sont manquants

### `02_implicit_probabilities.sql` — Probabilités implicites

Calcule les probabilités brutes et normalisées depuis les cotes :

| Vue | Description |
|---|---|
| `v_implicit_probabilities` | Cotes, probabilités brutes, normalisées, marge bookmaker |

Formules :
- `p_brute = 1 / cote`
- `p_norm = p_brute / (p_home_brute + p_draw_brute + p_away_brute)`
- `marge = p_home_brute + p_draw_brute + p_away_brute - 1`

La normalisation n'est calculée que lorsque les trois cotes existent et sont strictement positives.

### `03_season_summary.sql` — Résumé par saison

Agrégats statistiques par saison :

| Vue | Description |
|---|---|
| `v_season_summary` | Fréquences 1N2, buts, marge bookmaker par saison |

## Chargement des vues

Exécuter les scripts dans l'ordre :

```bash
mysql -u football -p football_odds < sql/analytics/01_match_results.sql
mysql -u football -p football_odds < sql/analytics/02_implicit_probabilities.sql
mysql -u football -p football_odds < sql/analytics/03_season_summary.sql
```

Ou via le conteneur MariaDB :

```bash
docker compose exec mariadb mysql -u football -pfootball football_odds < sql/analytics/01_match_results.sql
docker compose exec mariadb mysql -u football -pfootball football_odds < sql/analytics/02_implicit_probabilities.sql
docker compose exec mariadb mysql -u football -pfootball football_odds < sql/analytics/03_season_summary.sql
```
