"""Chargement idempotent des données dans MariaDB.

Utilise SQLAlchemy pour se connecter à la base et charger les équipes,
les matchs et les cotes via des INSERT avec ON DUPLICATE KEY UPDATE.
Chaque exécution est tracée dans la table etl_runs.
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generator

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


@dataclass
class LoadStats:
    """Statistiques de chargement."""

    teams_upserted: int = 0
    matches_upserted: int = 0
    odds_upserted: int = 0
    odds_errors: int = 0
    duration_seconds: float = 0.0

    def summary(self) -> str:
        return (
            f"Chargement ({self.duration_seconds:.1f}s) :\n"
            f"  Équipes insérées/mises à jour : {self.teams_upserted}\n"
            f"  Matchs insérés/mises à jour  : {self.matches_upserted}\n"
            f"  Cotes insérées/mises à jour  : {self.odds_upserted}\n"
            f"  Erreurs cotes                : {self.odds_errors}"
        )


def _build_engine() -> Any:
    """Créer l'engine SQLAlchemy depuis les variables d'environnement."""
    user = os.getenv("MARIADB_USER", "football")
    password = os.getenv("MARIADB_PASSWORD", "football")
    host = os.getenv("MARIADB_HOST", "127.0.0.1")
    port = os.getenv("MARIADB_PORT", "3306")
    database = os.getenv("MARIADB_DATABASE", "football_odds")

    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(url, pool_pre_ping=True, echo=False)
    return engine


def _create_etl_run(engine: Any, season: str, source: str = "football-data.co.uk") -> int:
    """Créer un enregistrement etl_runs en statut 'running'. Retourne l'ID."""
    now = datetime.now(timezone.utc).replace(microsecond=0)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO etl_runs (started_at, status, source, season, "
                "lines_read, lines_loaded, lines_rejected) "
                "VALUES (:started_at, 'running', :source, :season, 0, 0, 0)"
            ),
            {
                "started_at": now,
                "source": source,
                "season": season,
            },
        )
        etl_run_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
    logger.info("ETL run créé : id=%d", etl_run_id)
    return int(etl_run_id)


def _complete_etl_run(
    engine: Any,
    etl_run_id: int,
    status: str,
    lines_read: int = 0,
    lines_loaded: int = 0,
    lines_rejected: int = 0,
    error_message: str | None = None,
) -> None:
    """Mettre à jour l'enregistrement etl_runs avec le statut final."""
    now = datetime.now(timezone.utc).replace(microsecond=0)
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE etl_runs SET finished_at = :finished_at, status = :status, "
                "lines_read = :lines_read, lines_loaded = :lines_loaded, "
                "lines_rejected = :lines_rejected, error_message = :error_message "
                "WHERE id = :etl_run_id"
            ),
            {
                "finished_at": now,
                "status": status,
                "lines_read": lines_read,
                "lines_loaded": lines_loaded,
                "lines_rejected": lines_rejected,
                "error_message": error_message,
                "etl_run_id": etl_run_id,
            },
        )


def load_teams(
    engine: Any,
    matches_data: list[dict[str, Any]],
) -> dict[str, int]:
    """Charger les équipes dans la table teams.

    Returns un mapping nom -> id pour les utiliser dans matches.
    """
    # Collecter les équipes uniques préservant l'ordre d'apparition
    seen: set[str] = set()
    ordered_teams: list[str] = []
    for m in matches_data:
        for name in (m.get("home_team_name"), m.get("away_team_name")):
            if name and name not in seen:
                seen.add(name)
                ordered_teams.append(name)

    if not ordered_teams:
        return {}

    # Charger les équipes existantes
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, source_team_name FROM teams WHERE source_team_name IN :names"),
            {"names": tuple(ordered_teams)},
        )
        existing = {row[1]: row[0] for row in result}

    new_teams = [t for t in ordered_teams if t not in existing]
    upserted = 0

    if new_teams:
        with engine.begin() as conn:
            for team_name in new_teams:
                conn.execute(
                    text(
                        "INSERT INTO teams (source_team_name, name) "
                        "VALUES (:name, :name) "
                        "ON DUPLICATE KEY UPDATE name = VALUES(name)"
                    ),
                    {"name": team_name},
                )
                upserted += 1

        # Recharger pour avoir les IDs
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, source_team_name FROM teams WHERE source_team_name IN :names"),
                {"names": tuple(ordered_teams)},
            )
            existing = {row[1]: row[0] for row in result}

    logger.info("Équipes chargées : %d existantes, %d nouvelles", len(existing) - upserted, upserted)
    return existing


def load_matches(
    engine: Any,
    matches_data: list[dict[str, Any]],
    team_map: dict[str, int],
) -> tuple[list[dict[str, Any]], int]:
    """Charger les matchs dans la table matches.

    Retourne les matchs chargés avec leur ID ajouté, et le nombre upserté.
    """
    if not matches_data:
        return [], 0

    # Récupérer les match keys existants
    existing_keys: set[str] = set()
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT source_match_key FROM matches WHERE source_match_key IN :keys"),
            {"keys": tuple(m["source_match_key"] for m in matches_data)},
        )
        existing_keys = {row[0] for row in result}

    new_matches = [m for m in matches_data if m["source_match_key"] not in existing_keys]
    upserted = 0

    if new_matches:
        with engine.begin() as conn:
            for m in new_matches:
                home_id = team_map.get(m["home_team_name"])
                away_id = team_map.get(m["away_team_name"])

                if home_id is None or away_id is None:
                    logger.warning(
                        "Match %s : équipe introuvable (home=%s, away=%s)",
                        m["source_match_key"],
                        m["home_team_name"],
                        m["away_team_name"],
                    )
                    continue

                if home_id == away_id:
                    logger.warning(
                        "Match %s : même équipe domicile et extérieur, ignoré",
                        m["source_match_key"],
                    )
                    continue

                conn.execute(
                    text(
                        "INSERT INTO matches ("
                        "  source_match_key, competition, season, match_date, "
                        "  home_team_id, away_team_id, home_goals, away_goals, "
                        "  home_goals_ht, away_goals_ht"
                        ") VALUES ("
                        "  :source_match_key, :competition, :season, :match_date, "
                        "  :home_team_id, :away_team_id, :home_goals, :away_goals, "
                        "  :home_goals_ht, :away_goals_ht"
                        ") ON DUPLICATE KEY UPDATE "
                        "  competition = VALUES(competition), "
                        "  season = VALUES(season), "
                        "  match_date = VALUES(match_date), "
                        "  home_team_id = VALUES(home_team_id), "
                        "  away_team_id = VALUES(away_team_id), "
                        "  home_goals = VALUES(home_goals), "
                        "  away_goals = VALUES(away_goals), "
                        "  home_goals_ht = VALUES(home_goals_ht), "
                        "  away_goals_ht = VALUES(away_goals_ht)"
                    ),
                    {
                        "source_match_key": m["source_match_key"],
                        "competition": m["competition"],
                        "season": m["season"],
                        "match_date": m["match_date"],
                        "home_team_id": home_id,
                        "away_team_id": away_id,
                        "home_goals": m.get("home_goals"),
                        "away_goals": m.get("away_goals"),
                        "home_goals_ht": None,
                        "away_goals_ht": None,
                    },
                )
                upserted += 1

    logger.info("Matchs chargés : %d upsertés, %d déjà existants", upserted, len(matches_data) - len(new_matches))
    return matches_data, upserted


def load_odds(
    engine: Any,
    odds_data: list[dict[str, Any]],
    match_key_to_id: dict[str, int],
) -> tuple[int, int]:
    """Charger les cotes dans la table match_odds.

    Returns (upserted, errors).
    """
    if not odds_data:
        return 0, 0

    upserted = 0
    errors = 0

    with engine.begin() as conn:
        for odd in odds_data:
            match_id = match_key_to_id.get(odd["source_match_key"])
            if match_id is None:
                errors += 1
                continue

            try:
                conn.execute(
                    text(
                        "INSERT INTO match_odds "
                        "(match_id, bookmaker, odds_type, home_odds, draw_odds, away_odds) "
                        "VALUES (:match_id, :bookmaker, :odds_type, :home_odds, :draw_odds, :away_odds) "
                        "ON DUPLICATE KEY UPDATE "
                        "  home_odds = VALUES(home_odds), "
                        "  draw_odds = VALUES(draw_odds), "
                        "  away_odds = VALUES(away_odds)"
                    ),
                    {
                        "match_id": match_id,
                        "bookmaker": odd["bookmaker"],
                        "odds_type": odd["odds_type"],
                        "home_odds": odd.get("home_odds"),
                        "draw_odds": odd.get("draw_odds"),
                        "away_odds": odd.get("away_odds"),
                    },
                )
                upserted += 1
            except Exception as e:
                errors += 1
                logger.warning("Erreur cote pour %s (%s %s) : %s",
                               odd["source_match_key"], odd["bookmaker"], odd["odds_type"], e)

    return upserted, errors


def load_season(
    season: str,
    matches_data: list[dict[str, Any]],
    odds_data: list[dict[str, Any]],
    lines_read: int = 0,
    lines_rejected: int = 0,
) -> LoadStats:
    """Charger une saison complète en base.

    Ordre d'insertion :
    1. Équipes (teams)
    2. Matchs (matches) — nécessite les IDs d'équipes
    3. Cotes (match_odds) — nécessite les IDs de matchs

    Trace l'exécution dans etl_runs.
    """
    engine = _build_engine()
    load_stats = LoadStats()
    start_time = time.time()

    etl_run_id = _create_etl_run(engine, season)

    try:
        # 1. Équipes
        team_map = load_teams(engine, matches_data)
        load_stats.teams_upserted = len(team_map)

        if not team_map:
            raise RuntimeError("Aucune équipe chargée — arrêt du chargement")

        # 2. Matchs
        _, matches_upserted = load_matches(engine, matches_data, team_map)
        load_stats.matches_upserted = matches_upserted

        # Construire le mapping match_key -> match_id pour les cotes
        match_key_to_id: dict[str, int] = {}
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT source_match_key, id FROM matches "
                    "WHERE source_match_key IN :keys"
                ),
                {"keys": tuple(m["source_match_key"] for m in matches_data)},
            )
            match_key_to_id = {row[0]: row[1] for row in result}

        # 3. Cotes
        odds_upserted, odds_errors = load_odds(engine, odds_data, match_key_to_id)
        load_stats.odds_upserted = odds_upserted
        load_stats.odds_errors = odds_errors

        load_stats.duration_seconds = time.time() - start_time

        _complete_etl_run(
            engine,
            etl_run_id,
            status="success",
            lines_read=lines_read,
            lines_loaded=matches_upserted,
            lines_rejected=lines_rejected,
        )

        logger.info("Chargement terminé avec succès : %s", load_stats.summary())
        return load_stats

    except Exception as e:
        load_stats.duration_seconds = time.time() - start_time
        error_msg = str(e)[:1000]
        _complete_etl_run(
            engine,
            etl_run_id,
            status="failed",
            lines_read=lines_read,
            error_message=error_msg,
        )
        logger.error("Chargement échoué : %s", error_msg)
        raise
