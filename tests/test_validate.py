"""Tests de validation des données (pipeline/validate.py)."""

from pipeline.validate import (
    ValidationReport,
    validate_all,
    validate_matches,
    validate_odds,
)


class TestValidateMatches:
    def test_valid_match(self):
        """Un match valide ne génère aucune anomalie."""
        matches = [{
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "match_date": "2024-08-16",
            "home_team_name": "PSG",
            "away_team_name": "Lens",
            "home_goals": 3,
            "away_goals": 1,
            "result_1n2": "H",
        }]
        report = validate_matches(matches, "2024-2025")
        report.finalize(matches, [])
        assert report.total_matches == 1
        assert report.matches_with_issues == 0
        assert report.matches_passed == 1

    def test_same_team_home_away(self):
        """Même équipe à domicile et extérieur = erreur."""
        matches = [{
            "source_match_key": "F1|2024-08-16|PSG|PSG",
            "match_date": "2024-08-16",
            "home_team_name": "PSG",
            "away_team_name": "PSG",
            "home_goals": 2,
            "away_goals": 1,
            "result_1n2": "H",
        }]
        report = validate_matches(matches, "2024-2025")
        assert "teams_same" in report.issue_counts
        assert report.issue_counts["teams_same"] == 1

    def test_negative_score(self):
        """Score négatif détecté."""
        matches = [{
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "match_date": "2024-08-16",
            "home_team_name": "PSG",
            "away_team_name": "Lens",
            "home_goals": -1,
            "away_goals": 1,
            "result_1n2": "A",
        }]
        report = validate_matches(matches, "2024-2025")
        assert "score_negative" in report.issue_counts
        assert report.issue_counts["score_negative"] == 1

    def test_too_large_score(self):
        """Score > 30 buts = warning."""
        matches = [{
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "match_date": "2024-08-16",
            "home_team_name": "PSG",
            "away_team_name": "Lens",
            "home_goals": 35,
            "away_goals": 2,
            "result_1n2": "H",
        }]
        report = validate_matches(matches, "2024-2025")
        assert "score_too_large" in report.issue_counts
        assert report.issue_counts["score_too_large"] == 1

    def test_missing_result(self):
        """FTR manquant ou invalide = warning."""
        matches = [{
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "match_date": "2024-08-16",
            "home_team_name": "PSG",
            "away_team_name": "Lens",
            "home_goals": 2,
            "away_goals": 2,
            "result_1n2": "X",
        }]
        report = validate_matches(matches, "2024-2025")
        assert "missing_1n2" in report.issue_counts
        assert report.issue_counts["missing_1n2"] == 1

    def test_missing_score(self):
        """Score manquant = warning."""
        matches = [{
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "match_date": "2024-08-16",
            "home_team_name": "PSG",
            "away_team_name": "Lens",
            "home_goals": None,
            "away_goals": 1,
            "result_1n2": "A",
        }]
        report = validate_matches(matches, "2024-2025")
        assert "missing_score" in report.issue_counts
        assert report.issue_counts["missing_score"] == 1

    def test_null_score_not_negative(self):
        """Score NULL n'est pas traité comme négatif."""
        matches = [{
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "match_date": "2024-08-16",
            "home_team_name": "PSG",
            "away_team_name": "Lens",
            "home_goals": None,
            "away_goals": None,
            "result_1n2": None,
        }]
        report = validate_matches(matches, "2024-2025")
        assert "score_negative" not in report.issue_counts

    def test_multiple_issues_same_match(self):
        """Plusieurs anomalies sur le même match."""
        matches = [{
            "source_match_key": "F1|bad-date|PSG|PSG",
            "match_date": "",
            "home_team_name": "PSG",
            "away_team_name": "PSG",
            "home_goals": -1,
            "away_goals": 1,
            "result_1n2": "X",
        }]
        report = validate_matches(matches, "2024-2025")
        report.finalize(matches, [])
        assert report.matches_with_issues == 1  # un seul match avec problème
        assert report.matches_passed == 0


class TestValidateOdds:
    def test_valid_odds(self):
        """Cotes valides = pas d'anomalie."""
        odds = [{
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "bookmaker": "bet365",
            "odds_type": "closing",
            "home_odds": 1.85,
            "draw_odds": 3.60,
            "away_odds": 4.20,
        }]
        report = validate_odds(odds, "2024-2025")
        assert report.total_odds == 1
        assert report.odds_with_issues == 0

    def test_negative_odds(self):
        """Cote négative détectée."""
        odds = [{
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "bookmaker": "bet365",
            "odds_type": "closing",
            "home_odds": -1.0,
            "draw_odds": 3.60,
            "away_odds": 4.20,
        }]
        report = validate_odds(odds, "2024-2025")
        assert "odds_h" in report.issue_counts

    def test_zero_odds_not_detected(self):
        """Les cotes 0.0 ont été converties en NULL en amont;
        elles ne devraient pas apparaître dans les données validées."""
        odds = [{
            "source_match_key": "F1|2024-08-16|PSG|Lens",
            "bookmaker": "bet365",
            "odds_type": "closing",
            "home_odds": None,
            "draw_odds": 3.60,
            "away_odds": 4.20,
        }]
        report = validate_odds(odds, "2024-2025")
        assert report.odds_with_issues == 0


class TestValidateAll:
    def test_combined_report(self):
        """validate_all fusionne les rapports matches + odds."""
        matches = [{
            "source_match_key": "F1|2024-08-16|PSG|PSG",
            "match_date": "2024-08-16",
            "home_team_name": "PSG",
            "away_team_name": "PSG",
            "home_goals": 2,
            "away_goals": 1,
            "result_1n2": "H",
        }]
        odds = [{
            "source_match_key": "F1|2024-08-16|PSG|PSG",
            "bookmaker": "bet365",
            "odds_type": "closing",
            "home_odds": 1.85,
            "draw_odds": 3.60,
            "away_odds": 4.20,
        }]
        report = validate_all(matches, odds, "2024-2025")
        assert report.total_matches == 1
        assert report.total_odds == 1
        assert "teams_same" in report.issue_counts
        assert report.matches_with_issues == 1
        assert report.odds_with_issues == 0

    def test_summary_text(self):
        """Le résumé contient les compteurs."""
        matches = []
        odds = []
        report = validate_all(matches, odds, "2024-2025")
        summary = report.summary_text
        assert "2024-2025" in summary
        assert "Matchs" in summary or "matchs" in summary


class TestValidationReport:
    def test_empty_report(self):
        """Un rapport vide n'a pas d'anomalies."""
        report = ValidationReport(season="2024-2025")
        report.finalize([], [])
        assert report.total_matches == 0
        assert report.matches_passed == 0
        assert len(report.issues) == 0

    def test_add_issue(self):
        """add_issue enregistre et compte."""
        report = ValidationReport(season="2024-2025")
        report.total_matches = 5
        report.add_issue("test_rule", "warning", "Test", "key1", "detail")
        assert len(report.issues) == 1
        assert report.issue_counts["test_rule"] == 1

    def test_summary_format(self):
        """Le résumé contient les informations essentielles."""
        report = ValidationReport(season="2024-2025")
        report.total_matches = 10
        report.total_odds = 50
        report.finalize([], [])
        text = str(report)
        assert "10" in text
        assert "50" in text
