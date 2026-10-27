-- =============================================================================
-- Goal Distribution — Distribution des buts par match
-- =============================================================================
-- Cette vue décrit la distribution des buts à domicile, à l'extérieur
-- et le total de buts par match, uniquement pour les matchs avec scores complets.
--
-- Tranches de buts : 0, 1, 2, 3, 4, 5+.
-- Moyennes et médianes arrondies à 2 décimales.
-- =============================================================================

CREATE OR REPLACE VIEW v_goal_distribution AS
SELECT
    season,
    COUNT(*) AS total_matches,
    -- Moyennes
    ROUND(AVG(home_goals), 2) AS avg_home_goals,
    ROUND(AVG(away_goals), 2) AS avg_away_goals,
    ROUND(AVG(home_goals + away_goals), 2) AS avg_total_goals,
    -- Tranches : total buts (0, 1, 2, 3, 4, 5+)
    SUM(CASE WHEN home_goals + away_goals = 0 THEN 1 ELSE 0 END) AS goals_0,
    SUM(CASE WHEN home_goals + away_goals = 1 THEN 1 ELSE 0 END) AS goals_1,
    SUM(CASE WHEN home_goals + away_goals = 2 THEN 1 ELSE 0 END) AS goals_2,
    SUM(CASE WHEN home_goals + away_goals = 3 THEN 1 ELSE 0 END) AS goals_3,
    SUM(CASE WHEN home_goals + away_goals = 4 THEN 1 ELSE 0 END) AS goals_4,
    SUM(CASE WHEN home_goals + away_goals >= 5 THEN 1 ELSE 0 END) AS goals_5plus,
    -- Pourcentages tranches total buts
    ROUND(100.0 * SUM(CASE WHEN home_goals + away_goals = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_0,
    ROUND(100.0 * SUM(CASE WHEN home_goals + away_goals = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_1,
    ROUND(100.0 * SUM(CASE WHEN home_goals + away_goals = 2 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_2,
    ROUND(100.0 * SUM(CASE WHEN home_goals + away_goals = 3 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_3,
    ROUND(100.0 * SUM(CASE WHEN home_goals + away_goals = 4 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_4,
    ROUND(100.0 * SUM(CASE WHEN home_goals + away_goals >= 5 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_5plus,
    -- Tranches : buts domicile (0, 1, 2, 3+)
    SUM(CASE WHEN home_goals = 0 THEN 1 ELSE 0 END) AS home_goals_0,
    SUM(CASE WHEN home_goals = 1 THEN 1 ELSE 0 END) AS home_goals_1,
    SUM(CASE WHEN home_goals = 2 THEN 1 ELSE 0 END) AS home_goals_2,
    SUM(CASE WHEN home_goals >= 3 THEN 1 ELSE 0 END) AS home_goals_3plus,
    -- Tranches : buts extérieur (0, 1, 2, 3+)
    SUM(CASE WHEN away_goals = 0 THEN 1 ELSE 0 END) AS away_goals_0,
    SUM(CASE WHEN away_goals = 1 THEN 1 ELSE 0 END) AS away_goals_1,
    SUM(CASE WHEN away_goals = 2 THEN 1 ELSE 0 END) AS away_goals_2,
    SUM(CASE WHEN away_goals >= 3 THEN 1 ELSE 0 END) AS away_goals_3plus
FROM matches
WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL
GROUP BY season
ORDER BY season;

-- =============================================================================
-- Exemples d'utilisation
-- =============================================================================
--
-- Distribution des buts par saison :
--   SELECT * FROM v_goal_distribution;
--
-- Comparaison moyenne de buts domicile/extérieur :
--   SELECT season, avg_home_goals, avg_away_goals, avg_total_goals
--   FROM v_goal_distribution
--   ORDER BY avg_total_goals DESC;
--
-- Taux de matchs sans but par saison :
--   SELECT season, pct_0
--   FROM v_goal_distribution
--   ORDER BY pct_0 DESC;
