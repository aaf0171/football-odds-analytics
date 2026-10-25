"""Tests de transformation et calcul de probabilités (pipeline/transform.py)."""

from pipeline.transform import (
    MatchTransformed,
    OddTransformed,
    TransformStats,
    _compute_raw_prob,
    _compute_normalized_probs,
    transform_all,
    transform_matches,
    transform_odds,
)


class TestComputeRawProb:
    """Tests de probabilité brute : p = 1 / cote."""

    def test_odds_2_00(self):
        """Cote 2.00 → probabilité brute 0.5."""
        assert _compute_raw_prob(2.00) == 0.5

    def test_odds_4_00(self):
        """Cote 4.00 → probabilité brute 0.25."""
        assert _compute_raw_prob(4.00) == 0.25

    def test_odds_1_50(self):
        """Cote 1.50 → probabilité brute ≈ 0.6667."""
        assert abs(_compute_raw_prob(1.50) - 0.6666667) < 0.0000001

    def test_odds_10_00(self):
        """Cote 10.00 → probabilité brute 0.1."""
        assert _compute_raw_prob(10.00) == 0.1

    def test_odds_1_01(self):
        """Cote minimale 1.01 → probabilité brute ≈ 0.9901."""
        assert abs(_compute_raw_prob(1.01) - (1.0 / 1.01)) < 0.0000001

    def test_none_odds(self):
        """Cote None → probabilité None."""
        assert _compute_raw_prob(None) is None

    def test_zero_odds(self):
        """Cote 0.0 → probabilité None."""
        assert _compute_raw_prob(0.0) is None

    def test_negative_odds(self):
        """Cote négative → probabilité None."""
        assert _compute_raw_prob(-1.0) is None

    def test_very_small_positive(self):
        """Cote positive très petite → probabilité > 0."""
        assert _compute_raw_prob(0.001) == 1000.0


class TestComputeNormalizedProbs:
    """Tests de probabilités normalisées."""

    def test_valid_triplet(self):
        """Trois probabilités valides → normalisation à 1."""
        h, d, a = _compute_normalized_probs(0.5, 0.3, 0.2)
        assert h is not None
        assert d is not None
        assert a is not None
        assert abs((h + d + a) - 1.0) < 0.0000001

    def test_normalization_bet365_example(self):
        """Exemple réel : Bet365 opening pour un match PSG."""
        # Cotes typiques : 1.85, 3.60, 4.20
        h_raw = 1.0 / 1.85
        d_raw = 1.0 / 3.60
        a_raw = 1.0 / 4.20
        h_norm, d_norm, a_norm = _compute_normalized_probs(h_raw, d_raw, a_raw)
        total = h_norm + d_norm + a_norm
        assert abs(total - 1.0) < 0.0000001
        # Le favori (cote la plus basse) doit avoir la plus haute probabilité
        assert h_norm > d_norm
        assert h_norm > a_norm

    def test_missing_home(self):
        """Cote domicile manquante → toutes les normalisées None."""
        h, d, a = _compute_normalized_probs(None, 0.3, 0.2)
        assert h is None
        assert d is None
        assert a is None

    def test_missing_draw(self):
        """Cote nul manquante → toutes les normalisées None."""
        h, d, a = _compute_normalized_probs(0.5, None, 0.3)
        assert h is None
        assert d is None
        assert a is None

    def test_missing_away(self):
        """Cote extérieur manquante → toutes les normalisées None."""
        h, d, a = _compute_normalized_probs(0.5, 0.3, None)
        assert h is None
        assert d is None
        assert a is None

    def test_all_none(self):
        """Trois None → trois None."""
        h, d, a = _compute_normalized_probs(None, None, None)
        assert h is None and d is None and a is None

    def test_zero_sum(self):
        """Somme nulle → None (cas pathologique)."""
        h, d, a = _compute_normalized_probs(0.0, 0.0, 0.0)
        # 0.0 est un cas spécial : _compute_raw_prob retourne None pour <= 0
        # Donc ce test vérifie le comportement si on passe 0.0 directement
        # (normalement impossible via _compute_raw_prob)
        assert h is None and d is None and a is None


class TestMatchTransformed:
    """Tests de transformation des matchs."""

    def test_home_win(self):
        """Victoire domicile → 'H'."""
        match = {
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "home_goals": 3,
            "away_goals": 1,
            "season": "2024-2025",
        }
        t = MatchTransformed.from_match(match)
        assert t.result_1n2 == "H"

    def test_draw(self):
        """Match nul → 'D'."""
        match = {
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "home_goals": 2,
            "away_goals": 2,
            "season": "2024-2025",
        }
        t = MatchTransformed.from_match(match)
        assert t.result_1n2 == "D"

    def test_away_win(self):
        """Victoire extérieur → 'A'."""
        match = {
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "home_goals": 0,
            "away_goals": 1,
            "season": "2024-2025",
        }
        t = MatchTransformed.from_match(match)
        assert t.result_1n2 == "A"

    def test_missing_home_goals(self):
        """Score domicile manquant → result_1n2 None."""
        match = {
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "home_goals": None,
            "away_goals": 1,
            "season": "2024-2025",
        }
        t = MatchTransformed.from_match(match)
        assert t.result_1n2 is None

    def test_missing_away_goals(self):
        """Score extérieur manquant → result_1n2 None."""
        match = {
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "home_goals": 2,
            "away_goals": None,
            "season": "2024-2025",
        }
        t = MatchTransformed.from_match(match)
        assert t.result_1n2 is None

    def test_zero_zero(self):
        """Score 0-0 → 'D'."""
        match = {
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "home_goals": 0,
            "away_goals": 0,
            "season": "2024-2025",
        }
        t = MatchTransformed.from_match(match)
        assert t.result_1n2 == "D"


class TestOddTransformed:
    """Tests de transformation des cotes."""

    def test_full_triplet(self):
        """Triplet complet → probabilités calculées."""
        odd = {
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "bookmaker": "bet365",
            "odds_type": "closing",
            "home_odds": 1.85,
            "draw_odds": 3.60,
            "away_odds": 4.20,
        }
        transformed = transform_odds([odd])[0]

        # Probas brutes
        assert transformed.home_prob_raw is not None
        assert abs(transformed.home_prob_raw - (1.0 / 1.85)) < 0.0000001
        assert abs(transformed.draw_prob_raw - (1.0 / 3.60)) < 0.0000001
        assert abs(transformed.away_prob_raw - (1.0 / 4.20)) < 0.0000001

        # Probas normalisées
        assert transformed.home_prob_norm is not None
        total_norm = transformed.home_prob_norm + transformed.draw_prob_norm + transformed.away_prob_norm
        assert abs(total_norm - 1.0) < 0.0000001

    def test_missing_draw_odds(self):
        """Cote nul manquante → normalisées None."""
        odd = {
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "bookmaker": "bet365",
            "odds_type": "closing",
            "home_odds": 1.85,
            "draw_odds": None,
            "away_odds": 4.20,
        }
        transformed = transform_odds([odd])[0]
        assert transformed.home_prob_raw is not None
        assert transformed.draw_prob_raw is None
        assert transformed.away_prob_raw is not None
        assert transformed.home_prob_norm is None

    def test_all_missing_odds(self):
        """Toutes cotes manquantes → tout à None."""
        odd = {
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "bookmaker": "bet365",
            "odds_type": "closing",
            "home_odds": None,
            "draw_odds": None,
            "away_odds": None,
        }
        transformed = transform_odds([odd])[0]
        assert transformed.home_prob_raw is None
        assert transformed.draw_prob_raw is None
        assert transformed.away_prob_raw is None
        assert transformed.home_prob_norm is None


class TestTransformStats:
    """Tests des statistiques de transformation."""

    def test_summary_contains_counters(self):
        """Le résumé contient les compteurs."""
        stats = TransformStats(
            matches_transformed=306,
            matches_result_computed=300,
            matches_result_missing=6,
            odds_transformed=2060,
            odds_norm_computed=1800,
            odds_norm_missing=260,
        )
        summary = stats.summary()
        assert "306" in summary
        assert "2060" in summary
        assert "1800" in summary


class TestTransformAll:
    """Tests d'intégration de la transformation complète."""

    def test_full_transform(self):
        """Transform_all retourne les bons types et compteurs."""
        matches = [
            {
                "source_match_key": "F1|2024-08-16|PSG|Lens",
                "home_goals": 3,
                "away_goals": 1,
                "season": "2024-2025",
            },
            {
                "source_match_key": "F1|2024-08-17|Rennes|Nice",
                "home_goals": 1,
                "away_goals": 1,
                "season": "2024-2025",
            },
        ]
        odds = [
            {
                "source_match_key": "F1|2024-08-16|PSG|Lens",
                "bookmaker": "bet365",
                "odds_type": "closing",
                "home_odds": 1.85,
                "draw_odds": 3.60,
                "away_odds": 4.20,
            },
            {
                "source_match_key": "F1|2024-08-16|PSG|Lens",
                "bookmaker": "bet365",
                "odds_type": "closing",
                "home_odds": None,
                "draw_odds": 3.60,
                "away_odds": 4.20,
            },
        ]
        t_matches, t_odds, stats = transform_all(matches, odds)

        assert len(t_matches) == 2
        assert len(t_odds) == 2
        assert stats.matches_transformed == 2
        assert stats.matches_result_computed == 2
        assert stats.odds_transformed == 2
        assert stats.odds_norm_computed == 1
        assert stats.odds_norm_missing == 1

    def test_empty_transform(self):
        """Entrées vides → sorties vides, compteurs à zéro."""
        t_matches, t_odds, stats = transform_all([], [])
        assert len(t_matches) == 0
        assert len(t_odds) == 0
        assert stats.matches_transformed == 0
        assert stats.odds_transformed == 0
