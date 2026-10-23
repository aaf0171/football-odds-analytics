#!/usr/bin/env python3
"""Comparer les schémas CSV entre saisons — T2.

Utilise uniquement la standard library (csv, collections).
Compare les en-têtes, types et valeurs manquantes entre fichiers.

Usage :
    python3 data/compare_seasons.py
    python3 data/compare_seasons.py data/F1_2024-2025.csv data/F1_2023-2024.csv
"""

import csv
import collections
import sys
import os


def _detect_type(val: str) -> str:
    if val == "":
        return ""
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


def read_csv_meta(csv_path: str) -> dict:
    """Lire un CSV et retourner ses métadonnées."""
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    col_types = collections.defaultdict(set)
    col_nulls = collections.defaultdict(int)
    for row in rows:
        for i, val in enumerate(row):
            if val == "":
                col_nulls[i] += 1
            else:
                col_types[i].add(_detect_type(val))

    return {
        "path": csv_path,
        "rows": len(rows),
        "cols": len(header),
        "header": header,
        "types": dict(col_types),
        "nulls": dict(col_nulls),
    }


def compare(seasons: list[str]) -> None:
    metas = []
    for path in seasons:
        print(f"Lecture de {path}...")
        metas.append(read_csv_meta(path))

    # En-têtes communs et différents
    all_headers = [set(m["header"]) for m in metas]
    common = set.intersection(*all_headers) if all_headers else set()
    not_in_all = []
    for i, h in enumerate(all_headers):
        diff = h - common
        if diff:
            not_in_all.append((metas[i]["path"], diff))

    print(f"\n=== Comparaison de {len(metas)} fichiers ===")
    for m in metas:
        print(f"  {m['path']}: {m['cols']} colonnes, {m['rows']} lignes")

    print(f"\n=== Colonnes communes à toutes les saisons ({len(common)}) ===")
    print(", ".join(sorted(common)))

    print(f"\n=== Colonnes absentes dans certaines saisons ===")
    all_unique = set()
    for h in [m["header"] for m in metas]:
        all_unique.update(h)
    extra_cols = all_unique - common
    if extra_cols:
        for col in sorted(extra_cols):
            present_in = []
            for i, m in enumerate(metas):
                if col in m["header"]:
                    present_in.append(metas[i]["path"])
            absent_from = [metas[i]["path"] for i in range(len(metas)) if col not in m["header"]]
            print(f"  {col}: présent dans {', '.join(present_in)}")
            if absent_from:
                print(f"       absent de {', '.join(absent_from)}")
    else:
        print("  Aucun écart.")

    # Colonnes avec noms différents mais positions similaires
    print(f"\n=== Positions des colonnes par saison ===")
    for i in range(max(m["cols"] for m in metas)):
        cols_at_pos = [(m["path"], m["header"][i] if i < m["cols"] else "(manquante)") for m in metas]
        unique_cols = set(c[1] for c in cols_at_pos)
        if len(unique_cols) > 1:
            print(f"  Pos {i:3d}:", end=" ")
            for path, col in cols_at_pos:
                print(f"{path.split('/')[-1]:25s} = {col}", end="  ")
            print()

    # Noms d'équipes
    print(f"\n=== Noms d'équipes par saison ===")
    team_idx = None
    for i, col in enumerate(metas[0]["header"]):
        if col == "HomeTeam":
            team_idx = i
            break
    if team_idx is not None:
        all_teams = collections.defaultdict(set)
        for m in metas:
            if team_idx < m["cols"]:
                for row in m:
                    if team_idx < len(row):
                        all_teams[m["path"]].add(row[team_idx])
        for path, teams in all_teams.items():
            print(f"  {path}: {len(teams)} équipes uniques")

    # Types par colonne
    print(f"\n=== Types par colonne (écart entre saisons) ===")
    shortest_header = min(metas, key=lambda m: m["cols"])["header"]
    for i, col in enumerate(shortest_header):
        types_by_season = []
        for m in metas:
            if i < m["cols"]:
                t = m["types"].get(i, set())
                types_by_season.append((m["path"].split("/")[-1], t))
        unique_types = set()
        for _, t in types_by_season:
            unique_types.update(t)
        if len(unique_types) > 1:
            print(f"  {col}:")
            for label, t in types_by_season:
                print(f"    {label:25s}: {', '.join(sorted(t)) if t else '(empty)'}")

    # Valeurs manquantes par bookmaker 1N2
    print(f"\n=== Disponibilité bookmakers 1N2 (ouverture) ===")
    bk_map = {
        "B365": "Bet365",
        "BWH": "Bet&Win",
        "BF": "Betfair",
        "PS": "Pinnacle",
        "WH": "William Hill",
        "1XB": "1XBet",
    }
    for bk_prefix, bk_name in bk_map.items():
        # Trouver les colonnes H/D/A avec ce préfixe
        for season in metas:
            h_cols = [i for i, c in enumerate(season["header"]) if c.startswith(bk_prefix) and c.endswith("H")]
            d_cols = [i for i, c in enumerate(season["header"]) if c.startswith(bk_prefix) and c.endswith("D")]
            a_cols = [i for i, c in enumerate(season["header"]) if c.startswith(bk_prefix) and c.endswith("A")]
            if h_cols:
                idx = h_cols[0]
                total = season["rows"]
                nulls = season["nulls"].get(idx, 0)
                print(f"  {season['path'].split('/')[-1]:20s} {bk_name:15s}: {total - nulls}/{total} ({(total - nulls)/total*100:.1f}%)")
                break  # Un bookmaker par saison

    print()


if __name__ == "__main__":
    default_paths = [
        os.path.join("data", "F1_2024-2025.csv"),
        os.path.join("data", "F1_2023-2024.csv"),
        os.path.join("data", "F1_2022-2023.csv"),
    ]
    paths = sys.argv[1:] if len(sys.argv) > 1 else default_paths
    compare(paths)
