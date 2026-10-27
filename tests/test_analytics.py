"""Tests pour les requêtes analytiques T8 (analyse exploratoire SQL).

Les tests vérifient que les vues SQL créées dans sql/analytics/
retournent des résultats cohérents sur une base MariaDB chargée
avec le pipeline.
"""
import os
import pytest
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ["MARIADB_HOST"]
DB_PORT = int(os.environ["MARIADB_PORT"])
DB_USER = os.environ["MARIADB_USER"]
DB_PASSWORD = os.environ["MARIADB_PASSWORD"]
DB_NAME = os.environ["MARIADB_DATABASE"]


def get_connection():
    """Retourne une connexion MariaDB ou skip si indisponible."""
    try:
        return pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
        )
    except pymysql.MySQLError as exc:
        pytest.skip(f"MariaDB non disponible : {exc}")


class TestViewExists:
    """Chaque vue T8 doit exister sans erreur."""

    VIEWS = [
        "v_match_frequencies",
        "v_goal_distribution",
        "v_odds_ranges",
        "v_bookmaker_comparison",
        "v_data_coverage",
    ]

    @pytest.mark.parametrize("view_name", VIEWS)
    def test_view_exists(self, view_name):
        """La vue {view_name} existe dans la base."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    """SELECT table_name FROM information_schema.views
                       WHERE table_schema = %s AND table_name = %s""",
                    (DB_NAME, view_name),
                )
                assert c.fetchone() is not None, f"Vue {view_name} introuvable"
        finally:
            conn.close()


class TestMatchFrequencies:
    """v_match_frequencies : fréquences 1N2 par saison."""

    def test_returns_rows(self):
        """La vue retourne au moins une ligne."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute("SELECT * FROM v_match_frequencies WHERE season IS NOT NULL")
                rows = c.fetchall()
                assert len(rows) > 0
        finally:
            conn.close()

    def test_percentages_sum_to_100(self):
        """home_win_pct + draw_pct + away_win_pct ≈ 100."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT home_win_pct, draw_pct, away_win_pct "
                    "FROM v_match_frequencies WHERE season IS NOT NULL"
                )
                for row in c.fetchall():
                    total = float(row["home_win_pct"]) + float(row["draw_pct"]) + float(row["away_win_pct"])
                    assert 99.9 <= total <= 100.1, f"Somme des pourcentages = {total}"
        finally:
            conn.close()

    def test_all_matches_accounted(self):
        """home_wins + draws + away_wins = total_matches."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT total_matches, home_wins, draws, away_wins "
                    "FROM v_match_frequencies WHERE season IS NOT NULL"
                )
                for row in c.fetchall():
                    total = int(row["home_wins"]) + int(row["draws"]) + int(row["away_wins"])
                    assert total == int(row["total_matches"])
        finally:
            conn.close()

    def test_global_totals(self):
        """La ligne globale (season IS NULL) existe."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute("SELECT * FROM v_match_frequencies WHERE season IS NULL")
                row = c.fetchone()
                assert row is not None
                assert row["home_wins"] > 0
        finally:
            conn.close()


class TestGoalDistribution:
    """v_goal_distribution : distribution des buts."""

    def test_returns_rows(self):
        """La vue retourne au moins une ligne."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute("SELECT * FROM v_goal_distribution")
                rows = c.fetchall()
                assert len(rows) > 0
        finally:
            conn.close()

    def test_goal_tranches_sum(self):
        """La somme des tranches de buts total = total_matches."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT total_matches, goals_0, goals_1, goals_2, "
                    "goals_3, goals_4, goals_5plus "
                    "FROM v_goal_distribution"
                )
                for row in c.fetchall():
                    total = (
                        int(row["goals_0"])
                        + int(row["goals_1"])
                        + int(row["goals_2"])
                        + int(row["goals_3"])
                        + int(row["goals_4"])
                        + int(row["goals_5plus"])
                    )
                    assert total == int(row["total_matches"])
        finally:
            conn.close()

    def test_pct_tranches_sum(self):
        """La somme des pourcentages de tranches total ≈ 100."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT pct_0, pct_1, pct_2, pct_3, pct_4, pct_5plus "
                    "FROM v_goal_distribution"
                )
                for row in c.fetchall():
                    total = sum(float(row[k]) for k in ["pct_0", "pct_1", "pct_2", "pct_3", "pct_4", "pct_5plus"])
                    assert 99.9 <= total <= 100.1, f"Somme des % tranches = {total}"
        finally:
            conn.close()

    def test_home_goal_tranches_sum(self):
        """La somme des tranches buts domicile = total_matches."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT total_matches, home_goals_0, home_goals_1, "
                    "home_goals_2, home_goals_3plus FROM v_goal_distribution"
                )
                for row in c.fetchall():
                    total = (
                        int(row["home_goals_0"])
                        + int(row["home_goals_1"])
                        + int(row["home_goals_2"])
                        + int(row["home_goals_3plus"])
                    )
                    assert total == int(row["total_matches"])
        finally:
            conn.close()


class TestOddsRanges:
    """v_odds_ranges : résultats par tranche de cotes."""

    def test_returns_rows(self):
        """La vue retourne au moins une ligne."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute("SELECT * FROM v_odds_ranges")
                rows = c.fetchall()
                assert len(rows) > 0
        finally:
            conn.close()

    def test_all_ranges_present(self):
        """Les 5 tranches de cotes sont présentes."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute("SELECT odds_range FROM v_odds_ranges")
                ranges = {row["odds_range"] for row in c.fetchall()}
                expected = {"[1.00-1.50[", "[1.50-2.00[", "[2.00-3.00[", "[3.00-5.00[", "[5.00+]"}
                assert expected.issubset(ranges), f"Tranches manquantes : {expected - ranges}"
        finally:
            conn.close()

    def test_range_percentages_sum(self):
        """Pour chaque tranche, home_win_pct + draw_pct + away_win_pct ≈ 100."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT odds_range, home_win_pct, draw_pct, away_win_pct "
                    "FROM v_odds_ranges"
                )
                for row in c.fetchall():
                    total = (
                        float(row["home_win_pct"])
                        + float(row["draw_pct"])
                        + float(row["away_win_pct"])
                    )
                    assert 99.9 <= total <= 100.1, (
                        f"Tranche {row['odds_range']} : somme = {total}"
                    )
        finally:
            conn.close()

    def test_probs_between_0_1(self):
        """Les probabilités implicites moyennes sont entre 0 et 1."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT odds_range, avg_implied_home_prob FROM v_odds_ranges"
                )
                for row in c.fetchall():
                    prob = float(row["avg_implied_home_prob"])
                    assert 0 <= prob <= 1, (
                        f"Tranche {row['odds_range']} : prob = {prob}"
                    )
        finally:
            conn.close()

    def test_ordered_by_odds(self):
        """Les tranches sont triées par ordre croissant de cote."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute("SELECT odds_range FROM v_odds_ranges")
                ranges = [row["odds_range"] for row in c.fetchall()]
                expected_order = [
                    "[1.00-1.50[",
                    "[1.50-2.00[",
                    "[2.00-3.00[",
                    "[3.00-5.00[",
                    "[5.00+]",
                ]
                for i in range(len(ranges) - 1):
                    assert ranges.index(ranges[i]) < ranges.index(ranges[i + 1])
        finally:
            conn.close()


class TestBookmakerComparison:
    """v_bookmaker_comparison : comparaison des bookmakers."""

    def test_returns_rows(self):
        """La vue retourne au moins une ligne."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute("SELECT * FROM v_bookmaker_comparison")
                rows = c.fetchall()
                assert len(rows) > 0
        finally:
            conn.close()

    def test_all_bookmakers_present(self):
        """Tous les bookmakers avec cotes de clôture valides sont dans la vue."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT DISTINCT bookmaker FROM match_odds "
                    "WHERE odds_type = 'closing' "
                    "AND home_odds > 0 AND draw_odds > 0 AND away_odds > 0 "
                    "ORDER BY bookmaker"
                )
                db_bookmakers = {row["bookmaker"] for row in c.fetchall()}
                c.execute("SELECT bookmaker FROM v_bookmaker_comparison")
                view_bookmakers = {row["bookmaker"] for row in c.fetchall()}
                assert db_bookmakers == view_bookmakers
        finally:
            conn.close()

    def test_margin_positive(self):
        """La marge moyenne est positive (les bookmakers font du profit)."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT bookmaker, avg_margin_pct FROM v_bookmaker_comparison"
                )
                for row in c.fetchall():
                    assert float(row["avg_margin_pct"]) >= 0, (
                        f"{row['bookmaker']} : marge = {row['avg_margin_pct']}"
                    )
        finally:
            conn.close()

    def test_observations_same_as_base(self):
        """Le nombre de matchs corresponde au nombre de cotes de clôture valides."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT COUNT(DISTINCT match_id) AS expected "
                    "FROM match_odds WHERE odds_type = 'closing' "
                    "AND home_odds > 0 AND draw_odds > 0 AND away_odds > 0"
                )
                expected = int(c.fetchone()["expected"])
                c.execute("SELECT SUM(matches_count) AS actual FROM v_bookmaker_comparison")
                actual = int(c.fetchone()["actual"])
                assert expected == actual
        finally:
            conn.close()


class TestDataCoverage:
    """v_data_coverage : couverture et qualité des données."""

    def test_returns_rows(self):
        """La vue retourne au moins une ligne."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute("SELECT * FROM v_data_coverage")
                rows = c.fetchall()
                assert len(rows) > 0
        finally:
            conn.close()

    def test_score_completeness_100(self):
        """Tous les matchs ont des scores (100% de complétude)."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT season, score_completeness_pct "
                    "FROM v_data_coverage"
                )
                for row in c.fetchall():
                    assert float(row["score_completeness_pct"]) == 100.0
        finally:
            conn.close()

    def test_closing_odds_coverage_100(self):
        """Tous les matchs ont des cotes de clôture (100% de couverture)."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT season, closing_odds_coverage_pct "
                    "FROM v_data_coverage"
                )
                for row in c.fetchall():
                    assert float(row["closing_odds_coverage_pct"]) == 100.0
        finally:
            conn.close()

    def test_complete_closing_odds_100(self):
        """Toutes les cotes de clôture sont complètes (3 cotes non NULL)."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT season, complete_closing_odds_pct "
                    "FROM v_data_coverage"
                )
                for row in c.fetchall():
                    assert float(row["complete_closing_odds_pct"]) == 100.0
        finally:
            conn.close()

    def test_dates_ordered(self):
        """La date la plus ancienne est bien avant la plus récente."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT earliest_match, latest_match FROM v_data_coverage"
                )
                for row in c.fetchall():
                    assert row["earliest_match"] <= row["latest_match"]
        finally:
            conn.close()


class TestCrossViewConsistency:
    """Vérifications de cohérence entre vues."""

    def test_frequencies_match_total(self):
        """Les fréquences totales correspondent au nombre de matchs."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT SUM(total_matches) AS total FROM v_match_frequencies WHERE season IS NOT NULL"
                )
                freq_total = int(c.fetchone()["total"])
                c.execute(
                    "SELECT total_matches FROM v_data_coverage"
                )
                coverage_total = int(c.fetchone()["total_matches"])
                assert freq_total == coverage_total
        finally:
            conn.close()

    def test_seasons_align(self):
        """Les saisons de toutes les vues correspondent."""
        conn = get_connection()
        try:
            with conn.cursor() as c:
                c.execute("SELECT DISTINCT season FROM v_match_frequencies WHERE season IS NOT NULL")
                freq_seasons = {row["season"] for row in c.fetchall()}
                c.execute("SELECT DISTINCT season FROM v_goal_distribution")
                goal_seasons = {row["season"] for row in c.fetchall()}
                c.execute("SELECT DISTINCT season FROM v_data_coverage")
                coverage_seasons = {row["season"] for row in c.fetchall()}
                assert freq_seasons == goal_seasons == coverage_seasons
        finally:
            conn.close()
