-- =============================================================================
-- Season Summary — Résumé statistique par saison
-- =============================================================================
-- Cette vue agrège les statistiques clés par saison :
--   - Nombre de matchs avec scores complets
--   - Fréquence 1N2 observée
--   - Marge moyenne des bookmakers
--   - Couverture bookmakers (cotes de clôture)
-- =============================================================================

CREATE OR REPLACE VIEW v_season_summary AS
SELECT
    m.season,
    -- Matchs
    COUNT(DISTINCT m.id) AS total_matches,
    SUM(CASE WHEN m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL THEN 1 ELSE 0 END) AS matches_with_scores,
    SUM(CASE WHEN m.home_goals > m.away_goals THEN 1 ELSE 0 END) AS home_wins,
    SUM(CASE WHEN m.home_goals = m.away_goals THEN 1 ELSE 0 END) AS draws,
    SUM(CASE WHEN m.home_goals < m.away_goals THEN 1 ELSE 0 END) AS away_wins,
    -- Fréquences 1N2 (seulement pour les matchs avec scores)
    ROUND(100.0 * SUM(CASE WHEN m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL AND m.home_goals > m.away_goals THEN 1 ELSE 0 END)
         / NULLIF(SUM(CASE WHEN m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL THEN 1 ELSE 0 END), 0), 2) AS home_win_pct,
    ROUND(100.0 * SUM(CASE WHEN m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL AND m.home_goals = m.away_goals THEN 1 ELSE 0 END)
         / NULLIF(SUM(CASE WHEN m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL THEN 1 ELSE 0 END), 0), 2) AS draw_pct,
    ROUND(100.0 * SUM(CASE WHEN m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL AND m.home_goals < m.away_goals THEN 1 ELSE 0 END)
         / NULLIF(SUM(CASE WHEN m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL THEN 1 ELSE 0 END), 0), 2) AS away_win_pct,
    -- Buts
    ROUND(AVG(CASE WHEN m.home_goals IS NOT NULL THEN m.home_goals END), 2) AS avg_home_goals,
    ROUND(AVG(CASE WHEN m.away_goals IS NOT NULL THEN m.away_goals END), 2) AS avg_away_goals,
    SUM(CASE WHEN m.home_goals IS NOT NULL THEN m.home_goals ELSE 0 END) AS total_home_goals,
    SUM(CASE WHEN m.away_goals IS NOT NULL THEN m.away_goals ELSE 0 END) AS total_away_goals,
    -- Bookmakers (cotes de clôture avec marge calculable)
    COUNT(DISTINCT CASE WHEN mo.odds_type = 'closing' AND mo.home_odds > 0 AND mo.draw_odds > 0 AND mo.away_odds > 0
                        THEN mo.match_id END) AS matches_with_closing_odds,
    COUNT(DISTINCT mo.bookmaker) AS unique_bookmakers,
    ROUND(AVG(CASE WHEN mo.odds_type = 'closing' AND mo.home_odds > 0 AND mo.draw_odds > 0 AND mo.away_odds > 0
                   THEN ((1.0/mo.home_odds) + (1.0/mo.draw_odds) + (1.0/mo.away_odds) - 1.0) END) * 100, 2) AS avg_margin_pct
FROM matches m
LEFT JOIN match_odds mo ON m.id = mo.match_id
GROUP BY m.season
ORDER BY m.season;

-- =============================================================================
-- Exemple d'utilisation
-- =============================================================================
--
-- Résumé de toutes les saisons :
--   SELECT * FROM v_season_summary;
--
-- Comparaison des taux de nuls par saison :
--   SELECT season, draw_pct
--   FROM v_season_summary
--   ORDER BY season;
