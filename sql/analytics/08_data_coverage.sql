-- =============================================================================
-- Data Coverage — Couverture et qualité des données
-- =============================================================================
-- Cette vue mesure la couverture des données par saison et par bookmaker :
--   - Nombre total de matchs et matchs avec scores complets
--   - Nombre de matchs avec cotes (ouverture et clôture)
--   - Pourcentage de cotes complètes (3 cotes non NULL)
--   - Nombre de bookmakers actifs
--   - Couverture temporelle (date min/max)
--
-- Ces indicateurs permettent d'évaluer la fiabilité de chaque analyse.
-- =============================================================================

CREATE OR REPLACE VIEW v_data_coverage AS
SELECT
    season_stats.season,
    -- Matchs
    season_stats.total_matches,
    season_stats.matches_with_scores,
    season_stats.matches_missing_scores,
    -- Cotes (subquery to avoid multiplication from LEFT JOIN)
    COALESCE(odds_stats.total_odds_records, 0) AS total_odds_records,
    COALESCE(odds_stats.matches_with_closing_odds, 0) AS matches_with_closing_odds,
    COALESCE(odds_stats.matches_with_opening_odds, 0) AS matches_with_opening_odds,
    COALESCE(odds_stats.matches_with_complete_closing_odds, 0) AS matches_with_complete_closing_odds,
    -- Pourcentages
    ROUND(100.0 * season_stats.matches_with_scores / season_stats.total_matches, 2) AS score_completeness_pct,
    ROUND(100.0 * COALESCE(odds_stats.matches_with_closing_odds, 0) / season_stats.total_matches, 2) AS closing_odds_coverage_pct,
    ROUND(100.0 * COALESCE(odds_stats.matches_with_complete_closing_odds, 0) / season_stats.total_matches, 2) AS complete_closing_odds_pct,
    -- Bookmakers
    COALESCE(odds_stats.unique_bookmakers, 0) AS unique_bookmakers,
    -- Couverture temporelle
    season_stats.earliest_match,
    season_stats.latest_match
FROM (
    SELECT
        season,
        COUNT(*) AS total_matches,
        SUM(CASE WHEN home_goals IS NOT NULL AND away_goals IS NOT NULL THEN 1 ELSE 0 END) AS matches_with_scores,
        SUM(CASE WHEN home_goals IS NULL OR away_goals IS NULL THEN 1 ELSE 0 END) AS matches_missing_scores,
        MIN(match_date) AS earliest_match,
        MAX(match_date) AS latest_match
    FROM matches
    GROUP BY season
) season_stats
LEFT JOIN (
    SELECT
        season,
        COUNT(*) AS total_odds_records,
        COUNT(DISTINCT CASE WHEN odds_type = 'closing' THEN match_id END) AS matches_with_closing_odds,
        COUNT(DISTINCT CASE WHEN odds_type = 'opening' THEN match_id END) AS matches_with_opening_odds,
        COUNT(DISTINCT CASE WHEN odds_type = 'closing'
                            AND home_odds IS NOT NULL
                            AND draw_odds IS NOT NULL
                            AND away_odds IS NOT NULL
                       THEN match_id END) AS matches_with_complete_closing_odds,
        COUNT(DISTINCT bookmaker) AS unique_bookmakers
    FROM match_odds
    JOIN matches mo_m ON match_odds.match_id = mo_m.id
    GROUP BY season
) odds_stats ON season_stats.season = odds_stats.season
ORDER BY season_stats.season;

-- =============================================================================
-- Exemples d'utilisation
-- =============================================================================
--
-- Couverture des données par saison :
--   SELECT * FROM v_data_coverage;
--
-- Matchs sans cotes de clôture :
--   SELECT total_matches - matches_with_closing_odds AS matches_without_closing
--   FROM v_data_coverage;
--
-- Qualité des scores (pourcentage de matchs avec scores complets) :
--   SELECT season, score_completeness_pct
--   FROM v_data_coverage
--   ORDER BY score_completeness_pct;
