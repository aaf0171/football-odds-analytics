"""Validation et rapport de qualité des données ingérées.

Parcourir les données extraites (matches + odds), appliquer des règles
métier et retourner un rapport de qualité avec les anomalies détectées.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Règles de validation
# ---------------------------------------------------------------------------

RULE_DESCRIPTIONS = {
    "date_invalid": "Date invalide ou non parseable",
    "score_negative": "Score négatif (impossible)",
    "score_too_large": "Score anormalement élevé (> 30 buts)",
    "teams_same": "Même équipe à domicile et à l'extérieur",
    "odds_zero": "Cote nulle (0.0) au lieu d'une valeur positive",
    "odds_negative": "Cote négative (impossible)",
    "missing_1n2": "Issue 1N2 manquante ou invalide",
    "missing_score": "Score (FTHG/FTAG) manquant",
}


@dataclass
class ValidationRule:
    """Description d'une règle de validation."""

    id: str
    description: str
    severity: str = "warning"  # "error" | "warning" | "info"


@dataclass
class ValidationReport:
    """Rapport de validation pour une saison complète."""

    season: str = ""
    total_matches: int = 0
    total_odds: int = 0
    matches_passed: int = 0
    matches_with_issues: int = 0
    odds_passed: int = 0
    odds_with_issues: int = 0
    issues: list[dict[str, Any]] = field(default_factory=list)
    issue_counts: dict[str, int] = field(default_factory=dict)
    validated_at: str = ""
    summary_text: str = ""

    def add_issue(self, rule_id: str, severity: str, description: str,
                  match_key: str | None, details: str) -> None:
        """Enregistrer une anomalie détectée."""
        issue = {
            "rule_id": rule_id,
            "rule_description": description,
            "severity": severity,
            "match_key": match_key,
            "details": details,
        }
        self.issues.append(issue)
        self.issue_counts[rule_id] = self.issue_counts.get(rule_id, 0) + 1

    def finalize(self, matches_data: list[dict[str, Any]], odds_data: list[dict[str, Any]]) -> None:
        """Calculer les compteurs finaux."""
        # Compter les matchs avec au moins une issue
        match_keys_with_issues = set()
        for issue in self.issues:
            if issue.get("match_key"):
                match_keys_with_issues.add(issue["match_key"])

        self.matches_with_issues = len(match_keys_with_issues)
        self.matches_passed = self.total_matches - self.matches_with_issues

        # Compter les cotes avec au moins une issue
        odds_keys_with_issues = set()
        for issue in self.issues:
            if issue.get("match_key") and issue["rule_id"].startswith("odds_"):
                odds_keys_with_issues.add(issue["match_key"])

        self.odds_with_issues = len(odds_keys_with_issues)
        self.odds_passed = self.total_odds - self.odds_with_issues

        self.validated_at = datetime.now(timezone.utc).isoformat()
        self.summary_text = self._build_summary()

    def _build_summary(self) -> str:
        """Construire un résumé textuel du rapport."""
        lines = [
            f"Rapport de validation — saison {self.season}",
            "=" * 50,
            f"Matchs analysés :           {self.total_matches}",
            f"Matchs sans anomalie :      {self.matches_passed}",
            f"Matchs avec anomalie(s) :   {self.matches_with_issues}",
            f"Cotes analysées :           {self.total_odds}",
            f"Cotes sans anomalie :       {self.odds_passed}",
            f"Cotes avec anomalie(s) :    {self.odds_with_issues}",
            "",
        ]
        if self.issue_counts:
            lines.append("Anomalies par catégorie :")
            for rule_id, count in sorted(self.issue_counts.items(),
                                         key=lambda x: -x[1]):
                desc = RULE_DESCRIPTIONS.get(rule_id, rule_id)
                lines.append(f"  {rule_id}: {count} ({desc})")
        else:
            lines.append("Aucune anomalie détectée.")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.summary_text


# ---------------------------------------------------------------------------
# Fonctions de validation
# ---------------------------------------------------------------------------

def validate_matches(
    matches_data: list[dict[str, Any]],
    season: str,
) -> ValidationReport:
    """Valider les matchs extraits.

    Règles appliquées :
    1. Date invalide
    2. Score négatif
    3. Score anormalement élevé (> 30)
    4. Même équipe à domicile et extérieur
    5. Issue 1N2 manquante ou invalide
    6. Score manquant
    """
    report = ValidationReport(season=season)
    report.total_matches = len(matches_data)

    for match in matches_data:
        key = match.get("source_match_key", "inconnu")
        match_has_issue = False

        # 1. Date invalide
        date_str = match.get("match_date", "")
        if not date_str:
            report.add_issue(
                "date_invalid", "error",
                RULE_DESCRIPTIONS["date_invalid"],
                key, f"Date vide pour {key}",
            )
            match_has_issue = True

        # 2. Score négatif
        h_goals = match.get("home_goals")
        a_goals = match.get("away_goals")
        if h_goals is not None and h_goals < 0:
            report.add_issue(
                "score_negative", "error",
                RULE_DESCRIPTIONS["score_negative"],
                key, f"home_goals = {h_goals}",
            )
            match_has_issue = True
        if a_goals is not None and a_goals < 0:
            report.add_issue(
                "score_negative", "error",
                RULE_DESCRIPTIONS["score_negative"],
                key, f"away_goals = {a_goals}",
            )
            match_has_issue = True

        # 3. Score anormalement élevé
        for score_name, score_val in [("home_goals", h_goals), ("away_goals", a_goals)]:
            if score_val is not None and score_val > 30:
                report.add_issue(
                    "score_too_large", "warning",
                    RULE_DESCRIPTIONS["score_too_large"],
                    key, f"{score_name} = {score_val}",
                )
                match_has_issue = True

        # 4. Même équipe à domicile et extérieur
        home = match.get("home_team_name", "")
        away = match.get("away_team_name", "")
        if home and away and home == away:
            report.add_issue(
                "teams_same", "error",
                RULE_DESCRIPTIONS["teams_same"],
                key, f"domicile='{home}', extérieur='{away}'",
            )
            match_has_issue = True

        # 5. Issue 1N2 manquante ou invalide
        result = match.get("result_1n2")
        if result not in ("H", "D", "A", None):
            report.add_issue(
                "missing_1n2", "warning",
                RULE_DESCRIPTIONS["missing_1n2"],
                key, f"FTR = '{result}'",
            )
            match_has_issue = True

        # 6. Score manquant
        if h_goals is None or a_goals is None:
            report.add_issue(
                "missing_score", "warning",
                RULE_DESCRIPTIONS["missing_score"],
                key, f"FTHG={h_goals}, FTAG={a_goals}",
            )
            match_has_issue = True

        if match_has_issue:
            pass  # compté dans finalize

    return report


def validate_odds(
    odds_data: list[dict[str, Any]],
    season: str,
) -> ValidationReport:
    """Valider les cotes extraites.

    Règles appliquées :
    1. Cote nulle (0.0) au lieu d'une valeur positive
    2. Cote négative (impossible)
    """
    report = ValidationReport(season=season)
    report.total_odds = len(odds_data)

    for odd in odds_data:
        key = odd.get("source_match_key", "inconnu")
        bookmaker = odd.get("bookmaker", "?")
        odd_type = odd.get("odds_type", "?")

        # Vérifier les trois cotes
        for odd_col, odd_name in [("home_odds", "H"), ("draw_odds", "D"),
                                    ("away_odds", "A")]:
            val = odd.get(odd_col)
            if val is not None:
                if val <= 0:
                    report.add_issue(
                        f"odds_{odd_name.lower()}", "error",
                        f"Cote {odd_name} invalide ({val})",
                        key,
                        f"{bookmaker} {odd_type}: {odd_name} = {val}",
                    )

    report.odds_passed = report.total_odds
    for issue in report.issues:
        if issue["rule_id"].startswith("odds_"):
            report.odds_passed -= 1
            report.odds_with_issues += 1
            break  # un match_key ne peut être compté qu'une fois par odds issue

    # Recalculer odds_with_issues correctement
    odds_keys_with_issues = set()
    for issue in report.issues:
        if issue["rule_id"].startswith("odds_"):
            odds_keys_with_issues.add(issue["match_key"])
    report.odds_with_issues = len(odds_keys_with_issues)
    report.odds_passed = max(0, report.total_odds - report.odds_with_issues)

    return report


def validate_all(
    matches_data: list[dict[str, Any]],
    odds_data: list[dict[str, Any]],
    season: str,
) -> ValidationReport:
    """Valider l'ensemble des données d'une saison et fusionner les rapports.

    Retourne un rapport unique avec toutes les anomalies de matches et odds.
    """
    matches_report = validate_matches(matches_data, season)
    odds_report = validate_odds(odds_data, season)

    # Fusionner dans un seul rapport
    report = ValidationReport(
        season=season,
        total_matches=matches_report.total_matches,
        total_odds=odds_report.total_odds,
        matches_passed=matches_report.matches_passed,
        matches_with_issues=matches_report.matches_with_issues,
        odds_passed=odds_report.odds_passed,
        odds_with_issues=odds_report.odds_with_issues,
        issues=matches_report.issues + odds_report.issues,
        issue_counts={**matches_report.issue_counts, **odds_report.issue_counts},
    )
    report.finalize(matches_data, odds_data)

    logger.info("Validation terminée : %s", report.summary_text)
    return report
