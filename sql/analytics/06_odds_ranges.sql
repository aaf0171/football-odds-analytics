-- =============================================================================
-- Odds Ranges — Résultats observés par tranche de cotes
-- =============================================================================
-- Cette vue regroupe les matchs par tranche de cote du bookmaker (cote de clôture)
-- et calcule la fréquence observée de chaque issue 1N2 dans chaque tranche.
--
-- Tranches de cotes : [1.00-1.50[, [1.50-2.00[, [2.00-3.00[, [3.00-5.00[, [5.00+]
-- Pourcentage de victoires à domicile dans chaque tranche.
-- Nombre d'observations dans chaque tranche.
--
-- Limite : cette analyse ne prouve pas de causalité. Elle décrit
-- les fréquences observées conditionnellement aux tranches de cotes.
-- =============================================================================

CREATE OR REPLACE VIEW v_odds_ranges AS
SELECT
    CASE
        WHEN o.home_odds < 1.5 THEN '[1.00-1.50['
        WHEN o.home_odds < 2.0 THEN '[1.50-2.00['
        WHEN o.home_odds < 3.0 THEN '[2.00-3.00['
        WHEN o.home_odds < 5.0 THEN '[3.00-5.00['
        ELSE '[5.00+]'
    END AS odds_range,
    COUNT(*) AS matches_count,
    SUM(CASE WHEN m.result_1n2 = 'H' THEN 1 ELSE 0 END) AS home_wins,
    SUM(CASE WHEN m.result_1n2 = 'D' THEN 1 ELSE 0 END) AS draws,
    SUM(CASE WHEN m.result_1n2 = 'A' THEN 1 ELSE 0 END) AS away_wins,
    ROUND(100.0 * SUM(CASE WHEN m.result_1n2 = 'H' THEN 1 ELSE 0 END) / COUNT(*), 2) AS home_win_pct,
    ROUND(100.0 * SUM(CASE WHEN m.result_1n2 = 'D' THEN 1 ELSE 0 END) / COUNT(*), 2) AS draw_pct,
    ROUND(100.0 * SUM(CASE WHEN m.result_1n2 = 'A' THEN 1 ELSE 0 END) / COUNT(*), 2) AS away_win_pct,
    -- Moyenne des probabilités normalisées domicile dans la tranche
    ROUND(AVG(o.prob_home_norm), 4) AS avg_implied_home_prob,
    -- Marge moyenne du bookmaker dans la tranche
    ROUND(AVG(o.bookmaker_margin) * 100, 2) AS avg_margin_pct,
    -- Cote moyenne dans la tranche
    ROUND(AVG(o.home_odds), 2) AS avg_home_odds
FROM v_implicit_probabilities o
JOIN v_match_results m ON o.match_id = m.id
WHERE o.odds_type = 'closing'
  AND o.home_odds IS NOT NULL
  AND m.result_1n2 IS NOT NULL
GROUP BY odds_range
ORDER BY
    CASE odds_range
        WHEN '[1.00-1.50[' THEN 1
        WHEN '[1.50-2.00[' THEN 2
        WHEN '[2.00-3.00[' THEN 3
        WHEN '[3.00-5.00[' THEN 4
        WHEN '[5.00+]' THEN 5
    END;

-- =============================================================================
-- Exemples d'utilisation
-- =============================================================================
--
-- Résultats observés par tranche de cote domicile :
--   SELECT * FROM v_odds_ranges;
--
-- Comparaison probabilité implicite vs fréquence observée :
--   SELECT odds_range,
--          avg_implied_home_prob * 100 AS implied_pct,
--          home_win_pct AS observed_pct,
--          ROUND(avg_implied_home_prob * 100 - home_win_pct, 2) AS bias
--   FROM v_odds_ranges
--   WHERE matches_count >= 10;
