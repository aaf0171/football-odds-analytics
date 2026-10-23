#!/usr/bin/env python3
"""Script simple d'inspection du CSV Ligue 1 Football-Data.co.uk.

Utilise uniquement la standard library (csv, collections).
Aucune dépendance externe requise.

Usage :
    python3 data/F1_2024-2025_inspection.py
    python3 data/F1_2024-2025_inspection.py data/F1_2023-2024.csv
"""

import csv
import collections
import sys
import os

CSV_PATH = os.path.join("data", "F1_2024-2025.csv")

COLS_1N2 = [
    "Div", "Date", "Time", "HomeTeam", "AwayTeam",
    "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR",
    "B365H", "B365D", "B365A",
    "BWH", "BWD", "BWA",
    "BFH", "BFD", "BFA",
    "PSH", "PSD", "PSA",
    "WHH", "WHD", "WHA",
    "1XBH", "1XBD", "1XBA",
    "MaxH", "MaxD", "MaxA",
    "AvgH", "AvgD", "AvgA",
    "BFEH", "BFED", "BFEA",
]


def _detect_type(val: str) -> str:
    """Retourne le type détecté pour une valeur non vide."""
    if val.startswith("#") or val.startswith("//"):
        return "comment"
    try:
        int(val)
        return "int"
    except ValueError:
        pass
    try:
        float(val)
        return "float"
    except ValueError:
        pass
    return "str"


def inspect(csv_path: str) -> None:
    if not os.path.isfile(csv_path):
        print(f"Erreur : fichier '{csv_path}' introuvable.", file=sys.stderr)
        sys.exit(1)

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    print(f"=== {csv_path} ===")
    print(f"Lignes : {len(rows)}")
    print(f"Colonnes : {len(header)}")
    print()

    # Types et valeurs manquantes
    col_types = collections.defaultdict(set)
    col_nulls = collections.defaultdict(int)
    for row in rows:
        for i, val in enumerate(row):
            if val == "":
                col_nulls[i] += 1
            else:
                col_types[i].add(_detect_type(val))

    print("--- Colonnes, types et valeurs manquantes ---")
    for i, col in enumerate(header):
        types = ", ".join(sorted(col_types[i]))
        nulls = col_nulls[i]
        null_pct = nulls / len(rows) * 100
        null_str = f" ({null_pct:.1f}%) de nulls" if nulls > 0 else ""
        print(f"  {i:3d}. {col:20s} [{types:15s}]{null_str}")
    print()

    # Exemple 1N2
    print("--- Exemple 1N2 (3 premières lignes) ---")
    core_idx = [i for i, c in enumerate(header) if c in COLS_1N2]
    for row in rows[:3]:
        vals = [row[i] for i in core_idx]
        print(" | ".join(f"{vals[j]:>10}" for j in range(len(vals))))
    print()

    # Résumé des cotes
    odds_cols = [i for i, c in enumerate(header)
                 if c.endswith(("H", "D", "A"))
                 and not c.startswith(("FTH", "FTA", "HTH", "HTA", "HHW", "AHW"))
                 and c not in ("HS", "AS", "HC", "AC", "HF", "AF", "HO", "AO", "HY", "AY")]
    if odds_cols:
        print("--- Résumé des cotes (moyenne, min, max) ---")
        for idx in odds_cols:
            col = header[idx]
            values = []
            for row in rows:
                if row[idx] != "":
                    try:
                        values.append(float(row[idx]))
                    except ValueError:
                        pass
            if values:
                avg = sum(values) / len(values)
                mn = min(values)
                mx = max(values)
                print(f"  {col:15s} n={len(values):4d}  min={mn:6.2f}  avg={avg:6.3f}  max={mx:6.2f}")
    print()
    print("=== Inspection terminée ===")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else CSV_PATH
    inspect(path)
