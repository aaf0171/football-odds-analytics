"""Tests de l'extraction CSV (pipeline/extract.py).

Ces tests vérifient la lecture, la normalisation des colonnes,
le parsing des types et l'extraction des cotes.
"""

from pipeline.extract import (
    ExtractionStats,
    _make_match_key,
    _parse_date,
    _parse_float,
    _parse_int,
    extract_season,
)


class TestParseDate:
    def test_valid_date(self):
        assert _parse_date("16/08/2024") == "2024-08-16"

    def test_invalid_date(self):
        assert _parse_date("32/13/2024") is None

    def test_empty_string(self):
        assert _parse_date("") is None

    def test_whitespace(self):
        assert _parse_date(" 16/08/2024 ") == "2024-08-16"


class TestParseFloat:
    def test_valid_float(self):
        assert _parse_float("4.75") == 4.75

    def test_integer_string(self):
        assert _parse_float("7") == 7.0

    def test_empty_string(self):
        assert _parse_float("") is None

    def test_none_value(self):
        assert _parse_float(None) is None

    def test_whitespace(self):
        assert _parse_float(" 1.42 ") == 1.42


class TestParseInt:
    def test_valid_int(self):
        assert _parse_int("3") == 3

    def test_empty_string(self):
        assert _parse_int("") is None

    def test_non_numeric(self):
        assert _parse_int("abc") is None


class TestMatchKey:
    def test_key_composition(self):
        key = _make_match_key("F1", "2024-08-16", "Le Havre", "Paris SG")
        assert key == "F1|2024-08-16|Le Havre|Paris SG"

    def test_key_uniqueness(self):
        key1 = _make_match_key("F1", "2024-08-16", "Le Havre", "Paris SG")
        key2 = _make_match_key("F1", "2024-08-16", "Paris SG", "Le Havre")
        assert key1 != key2


class TestExtractSeason:
    def test_extract_2024_2025(self):
        matches, odds, stats = extract_season("2024-2025")
        assert len(matches) == 306
        assert stats.lines_read == 306
        assert stats.matches_extracted == 306
        assert stats.teams_collected == 18
        assert stats.lines_skipped == 0
        assert stats.odds_records == 2060
        assert len(stats.errors) == 0

    def test_match_structure(self):
        matches, _, _ = extract_season("2024-2025")
        first = matches[0]
        assert "source_match_key" in first
        assert "competition" in first
        assert "match_date" in first
        assert "home_team_name" in first
        assert "away_team_name" in first
        assert "home_goals" in first
        assert "away_goals" in first
        assert "result_1n2" in first
        assert "season" in first
        assert first["competition"] == "F1"
        assert first["season"] == "2024-2025"

    def test_match_key_format(self):
        matches, _, _ = extract_season("2024-2025")
        for m in matches:
            key = m["source_match_key"]
            parts = key.split("|")
            assert len(parts) == 4
            assert parts[0] == "F1"
            # Date should be in YYYY-MM-DD format
            assert len(parts[1]) == 10

    def test_odds_structure(self):
        _, odds, _ = extract_season("2024-2025")
        first_odd = odds[0]
        assert "source_match_key" in first_odd
        assert "bookmaker" in first_odd
        assert "odds_type" in first_odd
        assert "home_odds" in first_odd
        assert "draw_odds" in first_odd
        assert "away_odds" in first_odd
        assert first_odd["odds_type"] in ("opening", "closing")

    def test_no_duplicate_match_keys(self):
        matches, _, _ = extract_season("2024-2025")
        keys = [m["source_match_key"] for m in matches]
        assert len(keys) == len(set(keys))

    def test_1n2_values(self):
        matches, _, _ = extract_season("2024-2025")
        valid_results = {"H", "D", "A", None}
        for m in matches:
            assert m["result_1n2"] in valid_results

    def test_goals_non_negative(self):
        matches, _, _ = extract_season("2024-2025")
        for m in matches:
            if m["home_goals"] is not None:
                assert m["home_goals"] >= 0
            if m["away_goals"] is not None:
                assert m["away_goals"] >= 0

    def test_stats_summary(self):
        _, _, stats = extract_season("2024-2025")
        summary = stats.summary()
        assert "Extraction" in summary
        assert "306" in summary
        assert "18" in summary
        assert "2060" in summary

    def test_nonexistent_file(self):
        matches, odds, stats = extract_season("2099-2099")
        assert len(matches) == 0
        assert len(stats.errors) > 0


class TestExtract2023Season:
    def test_extract_2023_2024(self):
        matches, odds, stats = extract_season("2023-2024")
        assert len(matches) == 306
        assert stats.teams_collected == 18
        assert stats.lines_skipped == 0

    def test_extract_2022_2023(self):
        matches, odds, stats = extract_season("2022-2023")
        assert len(matches) == 380
        assert stats.teams_collected == 20
        assert stats.lines_skipped == 0
