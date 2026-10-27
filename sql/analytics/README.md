# Requêtes analytiques

Ce dossier contient les vues SQL créées lors de la Phase 7 (T7) et de la Phase 8 (T8).

## Vues T7 — Transformations et probabilités

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

## Vues T8 — Analyse exploratoire

### `04_match_frequencies.sql` — Fréquences 1N2

Fréquences observées de chaque issue 1N2 par saison et globalement :

| Vue | Description |
|---|---|
| `v_match_frequencies` | Fréquences victoire domicile, nul, extérieur par saison |

Périmètre : matchs avec scores complets uniquement.

### `05_goal_distribution.sql` — Distribution des buts

Distribution des buts (domicile, extérieur, total) par saison :

| Vue | Description |
|---|---|
| `v_goal_distribution` | Moyennes et tranches de buts (0, 1, 2, 3, 4, 5+) |

Tranches utilisées : 0, 1, 2, 3, 4, 5+ buts.

### `06_odds_ranges.sql` — Résultats par tranche de cotes

Fréquences observées dans chaque tranche de cote du bookmaker (clôture) :

| Vue | Description |
|---|---|
| `v_odds_ranges` | Résultats 1N2, probabilités implicites et marges par tranche de cote |

Tranches de cotes : `[1.00-1.50[`, `[1.50-2.00[`, `[2.00-3.00[`, `[3.00-5.00[`, `[5.00+]`.

### `07_bookmaker_comparison.sql` — Comparaison des bookmakers

Indicateurs comparatifs par bookmaker (clôture uniquement) :

| Vue | Description |
|---|---|
| `v_bookmaker_comparison` | Marge, cotes moyennes, écarts implicite vs observé |

Filtrage recommandé : `matches_count >= 50` pour une interprétation fiable.

### `08_data_coverage.sql` — Couverture et qualité des données

Métriques de couverture par saison :

| Vue | Description |
|---|---|
| `v_data_coverage` | Taux de complétude des scores et cotes, bookmakers actifs, couverture temporelle |

Indicateurs : complétude des scores, couverture cotes de clôture, cotes complètes, nombre de bookmakers.

## Chargement des vues

Exécuter les scripts dans l'ordre :

```bash
mysql -u football -p football_odds < sql/analytics/01_match_results.sql
mysql -u football -p football_odds < sql/analytics/02_implicit_probabilities.sql
mysql -u football -p football_odds < sql/analytics/03_season_summary.sql
mysql -u football -p football_odds < sql/analytics/04_match_frequencies.sql
mysql -u football -p football_odds < sql/analytics/05_goal_distribution.sql
mysql -u football -p football_odds < sql/analytics/06_odds_ranges.sql
mysql -u football -p football_odds < sql/analytics/07_bookmaker_comparison.sql
mysql -u football -p football_odds < sql/analytics/08_data_coverage.sql
```

Ou via le conteneur MariaDB :

```bash
docker compose exec mariadb mysql -u football -pfootball football_odds < sql/analytics/01_match_results.sql
docker compose exec mariadb mysql -u football -pfootball football_odds < sql/analytics/02_implicit_probabilities.sql
docker compose exec mariadb mysql -u football -pfootball football_odds < sql/analytics/03_season_summary.sql
docker compose exec mariadb mysql -u football -pfootball football_odds < sql/analytics/04_match_frequencies.sql
docker compose exec mariadb mysql -u football -pfootball football_odds < sql/analytics/05_goal_distribution.sql
docker compose exec mariadb mysql -u football -pfootball football_odds < sql/analytics/06_odds_ranges.sql
docker compose exec mariadb mysql -u football -pfootball football_odds < sql/analytics/07_bookmaker_comparison.sql
docker compose exec mariadb mysql -u football -pfootball football_odds < sql/analytics/08_data_coverage.sql
```

## Tests des requêtes

Pour vérifier le bon fonctionnement des requêtes, exécuter les exemples d'utilisation fournis en fin de chaque fichier SQL. Les résultats doivent :
- Retourner des lignes sans erreur
- Avoir des dénominateurs cohérents (pas de division par zéro)
- Ne pas produire de valeurs NULL inattendues dans les pourcentages
