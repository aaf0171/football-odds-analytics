"""Tests du chargement en base (pipeline/load.py).

Ces tests vérifient les stats de chargement et l'idempotence
via un appel réel au pipeline (requiert MariaDB en cours d'exécution).
"""

from pipeline.extract import extract_season
from pipeline.load import LoadStats, load_season


class TestLoadStats:
    def test_summary_format(self):
        stats = LoadStats(
            teams_upserted=18,
            matches_upserted=306,
            odds_upserted=2060,
            duration_seconds=1.5,
        )
        summary = stats.summary()
        assert "18" in summary
        assert "306" in summary
        assert "2060" in summary
        assert "1.5" in summary


class TestLoadIdempotence:
    def test_first_load(self):
        """Premier chargement : la charge se termine avec succès.
        La vérification exacte des compteurs dépend de l'état de la BDD;
        on vérifie surtout l'absence d'exception.
        """
        matches, odds, stats = extract_season("2024-2025")
        load_stats = load_season("2024-2025", matches, odds, stats.lines_read, stats.lines_skipped)
        # Le chargement ne doit pas lever d'exception
        assert load_stats.duration_seconds > 0
        assert load_stats.odds_errors == 0

    def test_second_load_no_duplicates(self):
        """Deuxième chargement : 0 match upserté."""
        matches, odds, stats = extract_season("2024-2025")
        # Première exécution
        load_season("2024-2025", matches, odds, stats.lines_read, stats.lines_skipped)
        # Deuxième exécution
        load_stats = load_season("2024-2025", matches, odds, stats.lines_read, stats.lines_skipped)
        assert load_stats.matches_upserted == 0

    def test_etl_runs_tracked(self):
        """Chaque exécution crée un enregistrement dans etl_runs."""
        matches, odds, stats = extract_season("2024-2025")
        load_season("2024-2025", matches, odds, stats.lines_read, stats.lines_skipped)
        load_season("2024-2025", matches, odds, stats.lines_read, stats.lines_skipped)

        from pipeline.load import _build_engine
        from sqlalchemy import text

        engine = _build_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT COUNT(*) FROM etl_runs "
                    "WHERE season = '2024-2025' AND status = 'success'"
                )
            )
            count = result.scalar()
        # Au moins 2 runs (ceux du test actuel)
        assert count >= 2

    def test_data_consistency(self):
        """Vérifie les comptes de tables après chargement."""
        matches, odds, stats = extract_season("2024-2025")
        load_season("2024-2025", matches, odds, stats.lines_read, stats.lines_skipped)

        from pipeline.load import _build_engine
        from sqlalchemy import text

        engine = _build_engine()
        with engine.connect() as conn:
            team_count = conn.execute(text("SELECT COUNT(*) FROM teams")).scalar()
            match_count = conn.execute(text("SELECT COUNT(*) FROM matches")).scalar()
            odds_count = conn.execute(text("SELECT COUNT(*) FROM match_odds")).scalar()

        assert team_count == 18
        assert match_count == 306
        assert odds_count == 2060

    def test_duration_recorded(self):
        """La durée de chargement est enregistrée."""
        matches, odds, stats = extract_season("2024-2025")
        load_stats = load_season("2024-2025", matches, odds, stats.lines_read, stats.lines_skipped)
        assert load_stats.duration_seconds > 0
