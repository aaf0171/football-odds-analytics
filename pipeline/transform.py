"""Transformations et calculs de probabilités implicites.

Calculer l'issue 1N2 à partir des scores finaux et les probabilités
implicites brutes et normalisées à partir des cotes décimales.

Règles
------
1. Issue 1N2 :
   - `H` si home_goals > away_goals
   - `D` si home_goals == away_goals
   - `A` si home_goals < away_goals
   - `None` si l'un des scores est manquant

2. Probabilité brute :
   - `p_brute = 1 / cote` pour chaque cote valide (finie et > 0)

3. Probabilité normalisée :
   - `p_norm = p_brute / somme(p_brute)` uniquement si les trois cotes
     existent, sont finies et strictement positives.
   - Sinon, toutes les probabilités normalisées sont `None`.

4. Les cotes manquantes ou invalides ne sont jamais imputées.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Règles de transformation
# ---------------------------------------------------------------------------

@dataclass
class MatchTransformed:
    """Match enrichi avec issue 1N2 calculée."""

    source_match_key: str = ""
    home_goals: int | None = None
    away_goals: int | None = None
    result_1n2: str | None = None  # "H", "D", "A", None
    season: str = ""

    @staticmethod
    def from_match(match: dict[str, Any]) -> "MatchTransformed":
        h = match.get("home_goals")
        a = match.get("away_goals")

        if h is not None and a is not None:
            if h > a:
                result = "H"
            elif h < a:
                result = "A"
            else:
                result = "D"
        else:
            result = None

        return MatchTransformed(
            source_match_key=match.get("source_match_key", ""),
            home_goals=h,
            away_goals=a,
            result_1n2=result,
            season=match.get("season", ""),
        )


@dataclass
class OddTransformed:
    """Cote enrichie avec probabilités brutes et normalisées."""

    source_match_key: str = ""
    bookmaker: str = ""
    odds_type: str = ""
    home_odds: float | None = None
    draw_odds: float | None = None
    away_odds: float | None = None

    home_prob_raw: float | None = None
    draw_prob_raw: float | None = None
    away_prob_raw: float | None = None

    home_prob_norm: float | None = None
    draw_prob_norm: float | None = None
    away_prob_norm: float | None = None

    @staticmethod
    def from_odd(odd: dict[str, Any]) -> "OddTransformed":
        return OddTransformed(
            source_match_key=odd.get("source_match_key", ""),
            bookmaker=odd.get("bookmaker", ""),
            odds_type=odd.get("odds_type", ""),
            home_odds=odd.get("home_odds"),
            draw_odds=odd.get("draw_odds"),
            away_odds=odd.get("away_odds"),
        )


@dataclass
class TransformStats:
    """Statistiques de transformation."""

    matches_transformed: int = 0
    matches_result_computed: int = 0
    matches_result_missing: int = 0
    odds_transformed: int = 0
    odds_norm_computed: int = 0
    odds_norm_missing: int = 0
    transformed_at: str = ""

    def summary(self) -> str:
        return (
            f"Transformation ({self.transformed_at}):\n"
            f"  Matchs transformés :    {self.matches_transformed}\n"
            f"  Issue 1N2 calculée :    {self.matches_result_computed}\n"
            f"  Issue 1N2 manquante :   {self.matches_result_missing}\n"
            f"  Cotes transformées :    {self.odds_transformed}\n"
            f"  Probas normalisées :    {self.odds_norm_computed}\n"
            f"  Probas non normalis. :  {self.odds_norm_missing}"
        )


# ---------------------------------------------------------------------------
# Fonctions de calcul de probabilités
# ---------------------------------------------------------------------------

def _compute_raw_prob(odds: float | None) -> float | None:
    """Calculer la probabilité brute : p = 1 / cote.

    Retourne None si la cote est manquante, nulle, négative ou infinie.
    """
    if odds is None:
        return None
    if odds <= 0 or math.isinf(odds):
        return None
    return 1.0 / odds


def _compute_normalized_probs(
    home_prob: float | None,
    draw_prob: float | None,
    away_prob: float | None,
) -> tuple[float | None, float | None, float | None]:
    """Calculer les probabilités normalisées.

    Ne normalise que si les trois probabilités brutes sont valides.
    Retourne (None, None, None) sinon.
    """
    if home_prob is None or draw_prob is None or away_prob is None:
        return None, None, None

    total = home_prob + draw_prob + away_prob
    if total <= 0:
        return None, None, None

    return (
        home_prob / total,
        draw_prob / total,
        away_prob / total,
    )


def transform_matches(
    matches_data: list[dict[str, Any]],
) -> list[MatchTransformed]:
    """Transformer la liste des matchs : calculer l'issue 1N2."""
    transformed = [MatchTransformed.from_match(m) for m in matches_data]
    return transformed


def transform_odds(
    odds_data: list[dict[str, Any]],
) -> list[OddTransformed]:
    """Transformer la liste des cotes : calculer probabilités brutes et normalisées."""
    transformed = []
    for odd in odds_data:
        t = OddTransformed.from_odd(odd)

        t.home_prob_raw = _compute_raw_prob(t.home_odds)
        t.draw_prob_raw = _compute_raw_prob(t.draw_odds)
        t.away_prob_raw = _compute_raw_prob(t.away_odds)

        t.home_prob_norm, t.draw_prob_norm, t.away_prob_norm = (
            _compute_normalized_probs(
                t.home_prob_raw, t.draw_prob_raw, t.away_prob_raw
            )
        )

        transformed.append(t)

    return transformed


def transform_all(
    matches_data: list[dict[str, Any]],
    odds_data: list[dict[str, Any]],
) -> tuple[list[MatchTransformed], list[OddTransformed], TransformStats]:
    """Transformer matchs et cotes et retourner les statistiques."""
    transformed_matches = transform_matches(matches_data)
    transformed_odds = transform_odds(odds_data)

    stats = TransformStats(
        matches_transformed=len(transformed_matches),
        matches_result_computed=sum(
            1 for m in transformed_matches if m.result_1n2 is not None
        ),
        matches_result_missing=sum(
            1 for m in transformed_matches if m.result_1n2 is None
        ),
        odds_transformed=len(transformed_odds),
        odds_norm_computed=sum(
            1 for o in transformed_odds
            if o.home_prob_norm is not None
            and o.draw_prob_norm is not None
            and o.away_prob_norm is not None
        ),
        odds_norm_missing=sum(
            1 for o in transformed_odds
            if o.home_prob_norm is None
            and o.draw_prob_norm is None
            and o.away_prob_norm is None
        ),
        transformed_at=datetime.now(timezone.utc).isoformat(),
    )

    logger.info(
        "Transformation terminée : %s",
        stats.summary(),
    )

    return transformed_matches, transformed_odds, stats
