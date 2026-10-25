-- =============================================================================
-- Implicit Probabilities — Probabilités brutes et normalisées depuis les cotes
-- =============================================================================
-- Cette vue extrait les cotes 1N2 et calcule :
--   - p_brute = 1 / cote  (probabilité implicite brute)
--   - p_norm  = p_brute / somme(p_brute)  (probabilité normalisée, sans marge)
--
-- La normalisation n'est calculée que lorsque les trois cotes existent,
-- sont finies et strictement positives. Sinon, les probabilités normalisées
-- sont NULL.
--
-- Marge du bookmaker = (1/home + 1/draw + 1/away) - 1
-- =============================================================================

CREATE OR REPLACE VIEW v_implicit_probabilities AS
SELECT
    mo.id,
    mo.match_id,
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
    mo.bookmaker,
    mo.odds_type,
    mo.home_odds,
    mo.draw_odds,
    mo.away_odds,
    -- Probabilités brutes
    CASE
        WHEN mo.home_odds IS NOT NULL AND mo.home_odds > 0 THEN 1.0 / mo.home_odds
        ELSE NULL
    END AS prob_home_raw,
    CASE
        WHEN mo.draw_odds IS NOT NULL AND mo.draw_odds > 0 THEN 1.0 / mo.draw_odds
        ELSE NULL
    END AS prob_draw_raw,
    CASE
        WHEN mo.away_odds IS NOT NULL AND mo.away_odds > 0 THEN 1.0 / mo.away_odds
        ELSE NULL
    END AS prob_away_raw,
    -- Somme des probabilités brutes (inclut la marge du bookmaker)
    CASE
        WHEN mo.home_odds IS NOT NULL AND mo.home_odds > 0
         AND mo.draw_odds IS NOT NULL AND mo.draw_odds > 0
         AND mo.away_odds IS NOT NULL AND mo.away_odds > 0
        THEN (1.0 / mo.home_odds) + (1.0 / mo.draw_odds) + (1.0 / mo.away_odds)
        ELSE NULL
    END AS sum_probs_raw,
    -- Marge du bookmaker = sum(p_brute) - 1
    CASE
        WHEN mo.home_odds IS NOT NULL AND mo.home_odds > 0
         AND mo.draw_odds IS NOT NULL AND mo.draw_odds > 0
         AND mo.away_odds IS NOT NULL AND mo.away_odds > 0
        THEN ((1.0 / mo.home_odds) + (1.0 / mo.draw_odds) + (1.0 / mo.away_odds)) - 1.0
        ELSE NULL
    END AS bookmaker_margin,
    -- Probabilités normalisées (sans marge)
    CASE
        WHEN mo.home_odds IS NOT NULL AND mo.home_odds > 0
         AND mo.draw_odds IS NOT NULL AND mo.draw_odds > 0
         AND mo.away_odds IS NOT NULL AND mo.away_odds > 0
        THEN (1.0 / mo.home_odds) / ((1.0 / mo.home_odds) + (1.0 / mo.draw_odds) + (1.0 / mo.away_odds))
        ELSE NULL
    END AS prob_home_norm,
    CASE
        WHEN mo.home_odds IS NOT NULL AND mo.home_odds > 0
         AND mo.draw_odds IS NOT NULL AND mo.draw_odds > 0
         AND mo.away_odds IS NOT NULL AND mo.away_odds > 0
        THEN (1.0 / mo.draw_odds) / ((1.0 / mo.home_odds) + (1.0 / mo.draw_odds) + (1.0 / mo.away_odds))
        ELSE NULL
    END AS prob_draw_norm,
    CASE
        WHEN mo.home_odds IS NOT NULL AND mo.home_odds > 0
         AND mo.draw_odds IS NOT NULL AND mo.draw_odds > 0
         AND mo.away_odds IS NOT NULL AND mo.away_odds > 0
        THEN (1.0 / mo.away_odds) / ((1.0 / mo.home_odds) + (1.0 / mo.draw_odds) + (1.0 / mo.away_odds))
        ELSE NULL
    END AS prob_away_norm
FROM match_odds mo
JOIN matches m ON mo.match_id = m.id
JOIN teams ht ON m.home_team_id = ht.id
JOIN teams at ON m.away_team_id = at.id;

-- =============================================================================
-- Exemples d'utilisation
-- =============================================================================
--
-- Marge moyenne par bookmaker (cotes de clôture) :
--   SELECT bookmaker,
--          COUNT(*) AS matches,
--          ROUND(AVG(bookmaker_margin) * 100, 2) AS avg_margin_pct
--   FROM v_implicit_probabilities
--   WHERE bookmaker_margin IS NOT NULL AND odds_type = 'closing'
--   GROUP BY bookmaker
--   ORDER BY avg_margin_pct;
--
-- Probabilités normalisées moyennes par saison :
--   SELECT season,
--          ROUND(AVG(prob_home_norm) * 100, 2) AS avg_home_prob,
--          ROUND(AVG(prob_draw_norm) * 100, 2) AS avg_draw_prob,
--          ROUND(AVG(prob_away_norm) * 100, 2) AS avg_away_prob
--   FROM v_implicit_probabilities
--   WHERE prob_home_norm IS NOT NULL AND odds_type = 'closing'
--   GROUP BY season
--   ORDER BY season;
--
-- Calibration : comparer probabilités normalisées vs fréquences observées
--   SELECT season,
--          ROUND(AVG(prob_home_norm) * 100, 2) AS implied_home_pct,
--          ROUND(100.0 * SUM(CASE WHEN result_1n2 = 'H' THEN 1 ELSE 0 END) / COUNT(*), 2) AS actual_home_pct
--   FROM v_implicit_probabilities
--   WHERE prob_home_norm IS NOT NULL AND result_1n2 IS NOT NULL AND odds_type = 'closing'
--   GROUP BY season
--   ORDER BY season;
