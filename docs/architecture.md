# Architecture — Football Odds Analytics

## Vue d'ensemble

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Data source │────>│  Extract     │────>│     Raw      │
│  CSV         │     │  Python      │     │  MariaDB     │
│  football-   │     │              │     │              │
│  data.co.uk  │     └──────────────┘     └──────────────┘
└──────────────┘            │                      │
                            │  Validate            │
                            ▼                      │
                    ┌──────────────┐               │
                    │  Transform   │               │
                    │  Python      │               │
                    └──────────────┘               │
                            │                      │
                            ▼                      │
                    ┌──────────────┐               │
                    │  Analyze     │<───────────────┘
                    │  SQL + Pandas│
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  Model       │
                    │  scikit-learn│
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  Communicate │
                    │  JupyterLab  │
                    └──────────────┘
```

## Composants

### 1. Données sources

| Élément | Détail |
|---|---|
| Source | Football-Data.co.uk |
| Format | CSV (UTF-8, virgule, BOM) |
| URL | `https://www.football-data.co.uk/mmz4281/{YYMM}/F1.csv` |
| Saisons | 2024-2025, 2023-2024, 2022-2023 |
| Licence | Usage personnel uniquement |

Les fichiers CSV sont **non versionnés** et placés dans `data/`.

### 2. Pipeline ETL

Le pipeline est écrit en Python standard library pour l'extraction et transformation, avec SQLAlchemy + PyMySQL pour le chargement en MariaDB.

| Module | Responsable |
|---|---|
| `pipeline/extract.py` | Lecture CSV, métadonnées source |
| `pipeline/validate.py` | Vérification colonnes, types, règles métier |
| `pipeline/transform.py` | Normalisation, calculs probabilités, mapping bookmakers |
| `pipeline/load.py` | Chargement MariaDB (équipes, matchs, cotes) |
| `pipeline/run.py` | Orchestrator CLI (`python -m pipeline.run --season 2024-2025`) |

### 3. Base de données

**Moteur :** MariaDB 11.4 via Docker Compose.

**Tables :**

| Table | Rôle | Clé primaire | Clés étrangères |
|---|---|---|---|
| `teams` | Référentiel équipes | `id` (auto-incrément) | — |
| `matches` | Un match par ligne | `id` (auto-incrément) | `home_team_id` → `teams.id`, `away_team_id` → `teams.id` |
| `match_odds` | Cotes par bookmaker | `id` (auto-incrément) | `match_id` → `matches.id` |
| `etl_runs` | Historique exécutions | `id` (auto-incrément) | — |

**Stratégie de déduplication :**

- `matches.source_match_key` = concaténation `Div + Date + HomeTeam + AwayTeam` (clé unique)
- `match_odds` : `UNIQUE(match_id, bookmaker, odds_type)` — un bookmaker ne peut avoir qu'une seule cote par type (ouverture/clôture) par match
- INSERT avec `ON DUPLICATE KEY UPDATE` pour l'idempotence

### 4. Environnement

| Élément | Détail |
|---|---|
| Python | 3.11+, dans `.venv` (environnement virtuel) |
| Docker Compose | MariaDB 11.4 |
| Dépendances | Définies dans `pyproject.toml` |
| Configuration | Variables d'environnement via `.env` (non versionné) |

### 5. Analyse

| Élément | Détail |
|---|---|
| JupyterLab | `analysis/` et `notebooks/` |
| Requêtes SQL | `sql/analytics/` |
| Modèles | `analysis/train_model.py` (scikit-learn) |
| Visualisation | Matplotlib (Seaborn en option) |

## Contraintes

1. **Idempotence** : chaque exécution ETL est réexécutable sans doublons.
2. **Pas de fuite de données** : les modèles ne peuvent pas utiliser de résultats futurs.
3. **Valeurs manquantes** : préservées comme NULL, jamais converties en zéro.
4. **Séparation temporelle** : entraînement/validation/test séparés chronologiquement.
5. **Pas de redistribution** : les données CSV ne sont ni versionnées ni partagées.

## Commandes principales

```bash
# Démarrer MariaDB
docker compose up -d

# Créer l'environnement Python
python3 -m venv .venv && source .venv/bin/activate && pip install -e .

# Exécuter le pipeline (Phase 3)
python -m pipeline.run --season 2024-2025

# Lancer JupyterLab (Phase 6)
jupyter lab
```
