-- =============================================================================
-- Match Results — Issue 1N2 calculée depuis les scores
-- =============================================================================
-- Cette vue calcule l'issue 1N2 à partir des scores finaux (FTHG, FTAG).
-- Elle sert de référence pour les analyses exploratoires et les évaluations
-- de modèles.
--
-- L'issue 1N2 :
--   H = victoire domicile (home_goals > away_goals)
--   D = match nul (home_goals = away_goals)
--   A = victoire extérieur (home_goals < away_goals)
--   NULL = score manquant
-- =============================================================================

CREATE OR REPLACE VIEW v_match_results AS
SELECT
    m.id,
    m.source_match_key,
    m.competition,
    m.season,
    m.match_date,
    ht.source_team_name AS home_team,
    at.source_team_name AS away_team,
    m.home_goals,
    m.away_goals,
    CASE
        WHEN m.home_goals IS NULL OR m.away_goals IS NULL THEN NULL
        WHEN m.home_goals > m.away_goals THEN 'H'
        WHEN m.home_goals < m.away_goals THEN 'A'
        ELSE 'D'
    END AS result_1n2,
    m.home_goals_ht,
    m.away_goals_ht
FROM matches m
JOIN teams ht ON m.home_team_id = ht.id
JOIN teams at ON m.away_team_id = at.id;

-- =============================================================================
-- Exemples d'utilisation
-- =============================================================================
--
-- Fréquence 1N2 par saison :
--   SELECT season, result_1n2, COUNT(*) as count
--   FROM v_match_results
--   WHERE result_1n2 IS NOT NULL
--   GROUP BY season, result_1n2
--   ORDER BY season, result_1n2;
--
-- Taux de victoire à domicile par saison :
--   SELECT season,
--          COUNT(*) AS total,
--          SUM(CASE WHEN result_1n2 = 'H' THEN 1 ELSE 0 END) AS home_wins,
--          ROUND(100.0 * SUM(CASE WHEN result_1n2 = 'H' THEN 1 ELSE 0 END) / COUNT(*), 2) AS home_win_pct
--   FROM v_match_results
--   WHERE result_1n2 IS NOT NULL
--   GROUP BY season
--   ORDER BY season;
--
-- Matchs sans résultat calculable (scores manquants) :
--   SELECT source_match_key, home_goals, away_goals
--   FROM v_match_results
--   WHERE result_1n2 IS NULL;
