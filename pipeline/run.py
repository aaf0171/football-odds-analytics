"""Orchestrateur du pipeline ETL.

Commande CLI :
    python -m pipeline.run --season 2024-2025
    python -m pipeline --season 2024-2025 --csv data/F1_2024-2025.csv
    python -m pipeline --season 2024-2025 --dry-run

Le pipeline effectue :
    1. Extraction CSV (extract.py)
    2. Chargement MariaDB (load.py)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from pipeline.extract import extract_season
from pipeline.load import load_season
from pipeline.validate import validate_all

logger = logging.getLogger(__name__)

# Format : [heure] [niveau] message
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def run_pipeline(season: str, csv_path: str | None = None, dry_run: bool = False) -> bool:
    """Exécuter le pipeline ETL pour une saison donnée.

    Parameters
    ----------
    season : str
        Saison, ex: ``"2024-2025"``.
    csv_path : str | None
        Chemin vers le fichier CSV. Si None, cherche dans ``data/``.
    dry_run : bool
        Si True, extraction uniquement, pas de chargement.

    Returns
    -------
    bool
        True si tout s'est bien passé.
    """
    # --- Extraction ---
    logger.info("=" * 60)
    logger.info("Pipeline ETL — saison %s", season)
    logger.info("=" * 60)

    matches, odds, extract_stats = extract_season(season, base_dir="data", csv_filename=csv_path)

    if not matches:
        logger.error("Aucun match extrait — arrêt du pipeline")
        return False

    print("\n" + extract_stats.summary())

    if dry_run:
        # Validation quand même en mode dry-run
        logger.info("Mode dry-run : validation des données...")
        validation_report = validate_all(matches, odds, season)
        print("\n" + validation_report.summary_text)
        logger.info("Validation dry-run terminée")
        return True

    # --- Validation ---
    logger.info("Validation des données...")
    validation_report = validate_all(matches, odds, season)
    print("\n" + validation_report.summary_text)

    if validation_report.matches_with_issues > 0 or validation_report.odds_with_issues > 0:
        logger.warning(
            "%d match(s) et %d cote(s) avec anomalie(s) — chargement continu",
            validation_report.matches_with_issues,
            validation_report.odds_with_issues,
        )

    # --- Chargement ---
    logger.info("Début du chargement en base...")

    try:
        load_stats = load_season(
            season=season,
            matches_data=matches,
            odds_data=odds,
            lines_read=extract_stats.lines_read,
            lines_rejected=extract_stats.lines_skipped,
        )
        print("\n" + load_stats.summary())
        return True

    except Exception as e:
        logger.error("Chargement échoué : %s", e)
        print(f"\nERREUR : {e}")
        return False


def main():
    """Point d'entrée CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Pipeline ETL Football Odds Analytics"
    )
    parser.add_argument(
        "--season",
        required=True,
        help="Saison à importer, ex: 2024-2025",
    )
    parser.add_argument(
        "--csv",
        help="Chemin vers le fichier CSV (défaut: data/F1_{season}.csv)",
        default=None,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Extraction uniquement, sans chargement",
    )
    parser.add_argument(
        "--verbosity",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Niveau de verbosité (défaut: INFO)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.verbosity),
        format=LOG_FORMAT,
        stream=sys.stdout,
    )

    success = run_pipeline(
        season=args.season,
        csv_path=args.csv,
        dry_run=args.dry_run,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
