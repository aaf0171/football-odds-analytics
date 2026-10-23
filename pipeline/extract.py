"""Extraction des données CSV Football-Data.co.uk.

Lecture des fichiers CSV, normalisation des colonnes et des types.
Chaque match est identifié par une clé composite :
    source_match_key = Div + "|" + Date + "|" + HomeTeam + "|" + AwayTeam
"""

from __future__ import annotations

import csv
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mapping bookmakers
# ---------------------------------------------------------------------------

BOOKMAKER_PREFIXES = {
    # 2024-25 uniquement
    "BFE": "betfair_exchange",
    "BF": "betfair",
    # Toutes les saisons
    "B365": "bet365",
    "BW": "betandwin",
    "PS": "pinnacle",
    "WH": "william_hill",
    # 2024-25 uniquement
    "1XB": "1xbet",
    # 2022-23, 2023-24 uniquement
    "IW": "interwetten",
    "VC": "vc_bet",
}

MATCH_COLUMNS = [
    "Div",
    "Date",
    "Time",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR",
    "HTHG",
    "HTAG",
    "HTR",
]

ODDS_PREFIXES_OPENING = [
    "B365", "BWH", "BF", "PS", "WH", "1XB", "BFE",
]

ODDS_PREFIXES_CLOSING = [
    "B365C", "BWHCH", "BWCH", "PSCH", "WHCH", "1XBCH", "BFCH",
]


@dataclass
class ExtractionStats:
    """Statistiques d'extraction."""

    season: str = ""
    file: str = ""
    lines_read: int = 0
    lines_loaded: int = 0
    lines_skipped: int = 0
    teams_collected: int = 0
    matches_extracted: int = 0
    odds_records: int = 0
    extracted_at: str = ""
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Extraction [{self.season}] depuis {self.file}:\n"
            f"  Lignes lues:          {self.lines_read}\n"
            f"  Matchs extraits:      {self.matches_extracted}\n"
            f"  Équipes collectées:   {self.teams_collected}\n"
            f"  Enregistrements cotes: {self.odds_records}\n"
            f"  Lignes ignorées:      {self.lines_skipped}\n"
            f"  Erreurs:              {len(self.errors)}"
        )


def _parse_date(date_str: str) -> str | None:
    """Convertir dd/mm/yyyy en yyyy-mm-dd.

    Retourne None si la date est invalide.
    """
    try:
        dt = datetime.strptime(date_str.strip(), "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return None


def _parse_float(value: str) -> float | None:
    """Convertir une chaîne en float, retourne None si vide ou invalide."""
    if not value or not value.strip():
        return None
    try:
        return float(value.strip())
    except ValueError:
        return None


def _parse_int(value: str) -> int | None:
    """Convertir une chaîne en int, retourne None si vide ou invalide."""
    if not value or not value.strip():
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def _make_match_key(div: str, date: str, home: str, away: str) -> str:
    """Clé composite unique pour un match."""
    return f"{div}|{date}|{home}|{away}"


def _extract_odds_prefixes(season: str) -> tuple[list[str], list[str]]:
    """Retourne les préfixes de bookmakers ouverts/fermés selon la saison."""
    if season == "2024-2025":
        opening = ["B365", "BWH", "BF", "PS", "WH", "1XB", "BFE"]
        closing = ["B365C", "BWCH", "PSCH", "WHCH", "1XBCH", "BFCH"]
    else:
        opening = ["B365", "BWH", "PS", "WH", "IW", "VC"]
        closing = ["B365C", "BWCH", "PSCH", "WHCH", "IWCH", "VCCH"]
    return opening, closing


def extract_season(
    season: str,
    base_dir: str | Path = "data",
    csv_filename: str | None = None,
) -> tuple[list[dict[str, Any]], ExtractionStats]:
    """Extraire toutes les données d'une saison depuis un fichier CSV.

    Parameters
    ----------
    season : str
        Saison, ex: ``"2024-2025"``.
    base_dir : str | Path
        Dossier contenant les fichiers CSV.
    csv_filename : str | None
        Nom du fichier CSV. Si None, déduit de ``season``.

    Returns
    -------
    tuple[list[dict[str, Any]], ExtractionStats]
        Liste de dictionnaires (un par match) et statistiques d'extraction.
    """
    stats = ExtractionStats(season=season, extracted_at=datetime.now(timezone.utc).isoformat())

    if csv_filename is None:
        csv_filename = f"F1_{season}.csv"

    filepath = Path(base_dir) / csv_filename

    if not filepath.exists():
        msg = f"Fichier CSV introuvable : {filepath}"
        logger.error(msg)
        stats.errors.append(msg)
        return [], [], stats

    stats.file = str(filepath)
    logger.info("Extraction de %s (saison %s)", filepath, season)

    opening_prefixes, closing_prefixes = _extract_odds_prefixes(season)

    # Collecte des équipes uniques
    teams_set: set[str] = set()
    matches: list[dict[str, Any]] = []
    odds_records: list[dict[str, Any]] = []

    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row_num, row in enumerate(reader, start=2):
            stats.lines_read += 1

            # --- Vérifications minimales ---
            div = row.get("Div", "").strip()
            date_raw = row.get("Date", "").strip()
            home = row.get("HomeTeam", "").strip()
            away = row.get("AwayTeam", "").strip()

            if not div or not date_raw or not home or not away:
                stats.lines_skipped += 1
                stats.errors.append(f"Ligne {row_num} : colonnes obligatoires vides")
                continue

            match_date = _parse_date(date_raw)
            if match_date is None:
                stats.lines_skipped += 1
                stats.errors.append(f"Ligne {row_num} : date invalide '{date_raw}'")
                continue

            match_key = _make_match_key(div, match_date, home, away)
            fthg = _parse_int(row.get("FTHG", ""))
            ftag = _parse_int(row.get("FTAG", ""))
            ftr = row.get("FTR", "").strip()

            if ftr not in ("H", "D", "A"):
                ftr = None

            # --- Match ---
            match_record = {
                "source_match_key": match_key,
                "competition": div,
                "match_date": match_date,
                "home_team_name": home,
                "away_team_name": away,
                "home_goals": fthg,
                "away_goals": ftag,
                "result_1n2": ftr,
                "season": season,
            }
            matches.append(match_record)
            stats.matches_extracted += 1

            # --- Équipes ---
            if home:
                teams_set.add(home)
            if away:
                teams_set.add(away)

            # --- Cotes ---
            _extract_match_odds(
                row,
                match_key,
                season,
                opening_prefixes,
                closing_prefixes,
                odds_records,
            )

    stats.teams_collected = len(teams_set)
    stats.odds_records = len(odds_records)

    logger.info(
        "Extraction terminée : %d matchs, %d équipes, %d cotes",
        stats.matches_extracted,
        stats.teams_collected,
        stats.odds_records,
    )

    return matches, odds_records, stats


def _extract_match_odds(
    row: dict[str, str],
    match_key: str,
    season: str,
    opening_prefixes: list[str],
    closing_prefixes: list[str],
    out: list[dict[str, Any]],
) -> None:
    """Extraire les cotes d'une ligne CSV vers des records match_odds."""

    def _clean_odds(h: float | None, d: float | None, a: float | None) -> tuple[float | None, float | None, float | None]:
        """Convertir 0.0 en None pour les cotes invalides."""
        if h == 0.0:
            h = None
        if d == 0.0:
            d = None
        if a == 0.0:
            a = None
        return h, d, a

    def _emit_odds(bookmaker: str | None, h: float | None, d: float | None, a: float | None,
                   odds_type: str) -> None:
        """Émettre un record de cote si le bookmaker est connu et les cotes valides."""
        if bookmaker is None:
            return
        # Ignorer si toutes les cotes sont None/0
        if h is None and d is None and a is None:
            return
        h, d, a = _clean_odds(h, d, a)
        if h is None and d is None and a is None:
            return
        out.append({
            "source_match_key": match_key,
            "bookmaker": bookmaker,
            "odds_type": odds_type,
            "home_odds": h,
            "draw_odds": d,
            "away_odds": a,
        })

    def _resolve_prefix(prefix: str) -> str | None:
        """Retourner le préfixe net (ex: B365C -> B365, BWCH -> BWH)."""
        if prefix.startswith("BWCH"):
            return "BWH"
        if prefix.startswith("1XBCH"):
            return "1XB"
        if prefix.startswith("BFCH"):
            return "BF"
        if prefix.startswith("BFECH"):
            return "BFE"
        if prefix.startswith("IWCH"):
            return "IW"
        if prefix.startswith("VCCH"):
            return "VC"
        if "C" in prefix:
            return prefix.rstrip("C")
        return prefix

    # --- Cotes d'ouverture ---
    for prefix in opening_prefixes:
        h_val = _parse_float(row.get(f"{prefix}H", ""))
        d_val = _parse_float(row.get(f"{prefix}D", ""))
        a_val = _parse_float(row.get(f"{prefix}A", ""))
        bookmaker = BOOKMAKER_PREFIXES.get(prefix)
        _emit_odds(bookmaker, h_val, d_val, a_val, "opening")

    # --- Cotes de clôture ---
    for prefix in closing_prefixes:
        clean_prefix = _resolve_prefix(prefix)
        net_prefix = BOOKMAKER_PREFIXES.get(clean_prefix) if clean_prefix else None
        h_val = _parse_float(row.get(f"{prefix}H", ""))
        d_val = _parse_float(row.get(f"{prefix}D", ""))
        a_val = _parse_float(row.get(f"{prefix}A", ""))
        _emit_odds(net_prefix, h_val, d_val, a_val, "closing")
