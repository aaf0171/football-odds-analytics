-- =============================================================================
-- Bookmaker Comparison — Marge et performance par bookmaker
-- =============================================================================
-- Cette vue compare les bookmakers selon plusieurs indicateurs :
--   - Marge moyenne (cotes de clôture uniquement)
--   - Nombre de matchs couverts
--   - Fréquence implicite vs fréquence observée
--
-- Les comparaisons ne sont fiables que si le nombre de matchs est suffisant.
-- Un minimum de 50 matchs est recommandé pour l'interprétation.
-- =============================================================================

CREATE OR REPLACE VIEW v_bookmaker_comparison AS
SELECT
    o.bookmaker,
    COUNT(*) AS matches_count,
    COUNT(DISTINCT o.season) AS seasons_covered,
    -- Marge moyenne du bookmaker (cotes de clôture uniquement)
    ROUND(AVG(o.bookmaker_margin) * 100, 2) AS avg_margin_pct,
    MIN(o.bookmaker_margin) AS min_margin,
    MAX(o.bookmaker_margin) AS max_margin,
    -- Cotes moyennes
    ROUND(AVG(o.home_odds), 2) AS avg_home_odds,
    ROUND(AVG(o.draw_odds), 2) AS avg_draw_odds,
    ROUND(AVG(o.away_odds), 2) AS avg_away_odds,
    -- Probabilités implicites moyennes
    ROUND(AVG(o.prob_home_norm) * 100, 2) AS avg_implied_home_pct,
    ROUND(AVG(o.prob_draw_norm) * 100, 2) AS avg_implied_draw_pct,
    ROUND(AVG(o.prob_away_norm) * 100, 2) AS avg_implied_away_pct,
    -- Fréquences observées (si les matchs ont un résultat connu)
    ROUND(100.0 * SUM(CASE WHEN o.result_1n2 = 'H' THEN 1 ELSE 0 END) / COUNT(*), 2) AS obs_home_pct,
    ROUND(100.0 * SUM(CASE WHEN o.result_1n2 = 'D' THEN 1 ELSE 0 END) / COUNT(*), 2) AS obs_draw_pct,
    ROUND(100.0 * SUM(CASE WHEN o.result_1n2 = 'A' THEN 1 ELSE 0 END) / COUNT(*), 2) AS obs_away_pct,
    -- Écart implicite vs observé (home)
    ROUND(AVG(o.prob_home_norm) * 100 - 100.0 * SUM(CASE WHEN o.result_1n2 = 'H' THEN 1 ELSE 0 END) / COUNT(*), 2) AS home_bias_pct
FROM v_implicit_probabilities o
WHERE o.odds_type = 'closing'
  AND o.prob_home_norm IS NOT NULL
GROUP BY o.bookmaker
ORDER BY avg_margin_pct ASC;

-- =============================================================================
-- Exemples d'utilisation
-- =============================================================================
--
-- Comparaison des bookmakers par marge :
--   SELECT * FROM v_bookmaker_comparison;
--
-- Bookmakers avec le plus de matchs couverts :
--   SELECT bookmaker, matches_count, avg_margin_pct
--   FROM v_bookmaker_comparison
--   WHERE matches_count >= 50
--   ORDER BY matches_count DESC;
--
-- Écart implicite vs observé (home wins) :
--   SELECT bookmaker,
--          avg_implied_home_pct,
--          obs_home_pct,
--          home_bias_pct
--   FROM v_bookmaker_comparison
--   ORDER BY ABS(home_bias_pct) DESC;
