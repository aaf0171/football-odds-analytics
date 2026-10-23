"""Point d'entrée pour exécuter le pipeline avec `python -m pipeline`."""

import argparse
import sys

from pipeline.run import run_pipeline


def main():
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
        help="Chemin vers le fichier CSV (défaut: data/)",
        default=None,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Extraction uniquement, sans chargement",
    )

    args = parser.parse_args()

    success = run_pipeline(
        season=args.season,
        csv_path=args.csv,
        dry_run=args.dry_run,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
