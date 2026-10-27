-- =============================================================================
-- Match Frequencies — Fréquences 1N2 par saison et globalement
-- =============================================================================
-- Cette vue calcule les fréquences observées de chaque issue 1N2
-- (victoire domicile, match nul, victoire extérieur) par saison
-- et globalement, uniquement pour les matchs avec scores complets.
--
-- Périmètre : matchs dont home_goals et away_goals sont non NULL.
-- Dénominateur : nombre de matchs dans ce périmètre.
-- =============================================================================

CREATE OR REPLACE VIEW v_match_frequencies AS
SELECT
    season,
    COUNT(*) AS total_matches,
    SUM(CASE WHEN home_goals > away_goals THEN 1 ELSE 0 END) AS home_wins,
    SUM(CASE WHEN home_goals = away_goals THEN 1 ELSE 0 END) AS draws,
    SUM(CASE WHEN home_goals < away_goals THEN 1 ELSE 0 END) AS away_wins,
    ROUND(100.0 * SUM(CASE WHEN home_goals > away_goals THEN 1 ELSE 0 END)
         / COUNT(*), 2) AS home_win_pct,
    ROUND(100.0 * SUM(CASE WHEN home_goals = away_goals THEN 1 ELSE 0 END)
         / COUNT(*), 2) AS draw_pct,
    ROUND(100.0 * SUM(CASE WHEN home_goals < away_goals THEN 1 ELSE 0 END)
         / COUNT(*), 2) AS away_win_pct
FROM matches
WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL
GROUP BY season
WITH ROLLUP;

-- =============================================================================
-- Exemples d'utilisation
-- =============================================================================
--
-- Fréquences 1N2 par saison :
--   SELECT * FROM v_match_frequencies WHERE season IS NOT NULL;
--
-- Fréquences 1N2 globales (toutes saisons confondues) :
--   SELECT * FROM v_match_frequencies WHERE season IS NULL;
--
-- Taux de nuls par saison (tri décroissant) :
--   SELECT season, draw_pct
--   FROM v_match_frequencies
--   WHERE season IS NOT NULL
--   ORDER BY draw_pct DESC;
