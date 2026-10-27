# Football Odds Analytics

Analyse des probabilités implicites des cotes de bookmakers et comparaison avec les résultats observés en Ligue 1 française (F1).

## Objectif

**Question d'analyse :** les probabilités implicites des cotes reflètent-elles correctement les résultats observés ? Peut-on produire des probabilités mieux calibrées avec un modèle statistique simple ?

Ce projet est un portfolio orienté Data Analyst. Il démontre la capacité à :
- collecter et documenter des données externes
- contrôler et nettoyer un jeu de données
- concevoir un modèle relationnel SQL
- développer un pipeline réexécutable et idempotent
- réaliser une analyse exploratoire avec SQL et Python
- entraîner et évaluer un modèle de classification sans fuite de données
- présenter les résultats avec JupyterLab

## Avertissement

**Pas de paris réels.** Les stratégies éventuellement étudiées sont des simulations historiques, sans garantie de rentabilité future. Les résultats ne constituent pas un conseil d'investissement.

## Stack technique

| Élément | Technologie |
|---|---|
| Langage | Python 3.11+ |
| Base de données | MariaDB 11.4 (Docker Compose) |
| Manipulation données | Pandas |
| Modélisation | scikit-learn |
| Visualisation | Matplotlib, JupyterLab |
| Environnement | `.venv` (environnement virtuel local) |

## Prérequis

- Python 3.11 ou supérieur
- Docker et Docker Compose
- Git

## Installation

### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd football-odds-analytics
```

### 2. Configurer l'environnement Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

Les dépendances sont déclarées dans `pyproject.toml`. L'environnement virtuel `.venv/` est ignoré par Git (voir `.gitignore`).

### 3. Installer les dépendances de développement (optionnel)

```bash
pip install -e ".[dev]"
```

Cela installe `pytest`, `pytest-cov` et `ruff`.

### 4. Configurer MariaDB

```bash
# Copier le fichier d'exemple et adapter les valeurs si nécessaire
cp .env.example .env

# Démarrer MariaDB via Docker Compose
docker compose up -d
```

MariaDB démarre avec :
- Database : `football_odds` (configurable via `MARIADB_DATABASE`)
- Utilisateur : `football` / `football` (configurable via `MARIADB_USER` et `MARIADB_PASSWORD`)
- Le schéma SQL (`sql/schema.sql`) est appliqué automatiquement au premier démarrage.

### 5. Récupérer les données

Les fichiers CSV de Football-Data.co.uk ne sont pas versionnés (licence de redistribution non autorisée).

1. Se rendre sur https://www.football-data.co.uk/francem.php
2. Télécharger les fichiers CSV pour les saisons souhaitées (ex: `F1_2024-2025.csv`)
3. Placer les fichiers dans le dossier `data/`

Le dictionnaire complet des colonnes est disponible dans `docs/data-dictionary.md`.

## Utilisation

### Pipeline ETL

Importer une saison complète (équipes, matchs, cotes) dans MariaDB :

```bash
source .venv/bin/activate
python -m pipeline.run --season 2024-2025
```

Options :
| Argument | Description |
|---|---|
| `--season` | Saison à importer (ex: `2024-2025`) — **requis** |
| `--csv` | Chemin personnalisé vers le fichier CSV |
| `--dry-run` | Extraction et validation uniquement, sans chargement en base |
| `--verbosity` | Niveau de log : `DEBUG`, `INFO` (défaut), `WARNING`, `ERROR` |

Le pipeline effectue :
1. **Extraction** : lecture du CSV, normalisation des colonnes et types
2. **Validation** : vérification des règles métier (scores, dates, cotes, doublons)
3. **Transformation** : calcul de l'issue 1N2 et des probabilités implicites
4. **Chargement** : insertion idempotente dans MariaDB (`ON DUPLICATE KEY UPDATE`)
5. **Traçabilité** : chaque exécution est enregistrée dans `etl_runs`

### Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

Pour inclure la couverture :
```bash
python -m pytest tests/ -v --cov=pipeline --cov-report=term-missing
```

### Analyse exploratoire

```bash
source .venv/bin/activate
jupyter lab
```

Les notebooks d'analyse sont dans `notebooks/`. Les requêtes SQL analytiques sont dans `sql/analytics/`.

## Structure du projet

```
football-odds-analytics/
├── data/                       # Fichiers CSV (non versionnés)
│   └── README.md
├── docs/                       # Documentation
│   ├── architecture.md
│   ├── data-dictionary.md
│   ├── data-source.md
│   └── methodology.md
├── notebooks/                  # Notebooks JupyterLab
├── pipeline/                   # Pipeline ETL
│   ├── extract.py
│   ├── validate.py
│   ├── transform.py
│   ├── load.py
│   └── run.py
├── sql/
│   ├── schema.sql              # Schéma MariaDB
│   └── analytics/              # Requêtes analytiques
├── tests/                      # Tests unitaires
├── .env.example                # Variables d'environnement (exemples)
├── compose.yaml                # Docker Compose pour MariaDB
├── pyproject.toml              # Dépendances Python
├── .gitignore
└── README.md
```

## Configuration

Les paramètres de connexion à la base sont lus depuis les variables d'environnement ou le fichier `.env` :

| Variable | Défaut | Description |
|---|---|---|
| `MARIADB_HOST` | `127.0.0.1` | Hôte de MariaDB |
| `MARIADB_PORT` | `3306` | Port de MariaDB |
| `MARIADB_DATABASE` | `football_odds` | Nom de la base |
| `MARIADB_USER` | `football` | Utilisateur |
| `MARIADB_PASSWORD` | `football` | Mot de passe |
| `MARIADB_ROOT_PASSWORD` | `root` | Mot de passe root (Docker) |

**Ne jamais commit de fichier `.env` contenant de vrais secrets.**

## Données

| Source | URL | Conditions |
|---|---|---|
| Football-Data.co.uk | https://www.football-data.co.uk/ | Usage personnel uniquement |

Les données sont utilisées pour l'analyse historique uniquement. Leur redistribution n'est pas autorisée.

### Saisons disponibles

| Saison | Matchs | Bookmakers |
|---|---|---|
| 2024-2025 | 306 | bet365, betfair, pinnacle, 1xbet, william_hill, betandwin |
| 2023-2024 | 306 | bet365, pinnacle, william_hill, betandwin, interwetten, vc_bet |
| 2022-2023 | 380 | bet365, pinnacle, william_hill, betandwin, interwetten, vc_bet |

## Méthodologie

### Issue 1N2 (Phase 7)

Calculée à partir des scores finaux :
- `H` si `home_goals > away_goals`
- `D` si `home_goals = away_goals`
- `A` si `home_goals < away_goals`
- `NULL` si un score est manquant (jamais imputé)

### Probabilités implicites brutes (Phase 7)

Pour une cote décimale `o_i > 0` :
```
p_brute_i = 1 / o_i
```

Si la cote est `NULL`, nulle ou négative, la probabilité brute est `NULL`.

### Probabilités implicites normalisées (Phase 7)

Pour un triplet complet de cotes valides :
```
p_norm_i = p_brute_i / (p_home_brute + p_draw_brute + p_away_brute)
```

Calculée uniquement si les trois cotes sont valides. Sinon, toutes les normalisées sont `NULL`.

### Marge du bookmaker

```
marge = p_home_brute + p_draw_brute + p_away_brute - 1
```

### Évaluation des modèles

### Évaluation des modèles

- **Log loss** : pénalise les probabilités très confiantes mais erronées
- **Score de Brier** : mesure l'écart quadratique entre probabilités prédites et résultats observés
- **Calibration** : parmi les événements auxquels le modèle attribue environ 60 %, environ 60 % devraient se réaliser

### Prévention des fuites de données

- Aucune variable issue du match à prédire n'est utilisée comme caractéristique
- Pas de statistiques de forme calculées avec des matchs futurs
- Les cotes utilisées correspondent au moment de disponibilité documenté
- Séparation temporelle entre entraînement et test (pas de mélange aléatoire)

## Phases du projet

| Phase | Description | Statut |
|---|---|---|
| 1 | Cadrage et étude de la source | ✅ Terminé |
| 2 | Environnement Python, Docker, modèle SQL | ✅ Terminé |
| 3 | Ingestion idempotente | ✅ Terminé |
| 4 | Validation et transformations | ✅ Terminé |
| 5 | Analyse exploratoire (SQL) | ✅ Terminé |
| 6 | Analyse et visualisation JupyterLab | 🚧 À venir |
| 7 | Modèles de probabilités | 🚧 À venir |
| 8 | Fiabilisation et portfolio | 🚧 À venir |

Voir le fichier `football-odds-analytics-roadmap.md` pour la roadmap complète.

## Licence

Ce projet est un portfolio personnel. Les données Football-Data.co.uk sont sous licence d'usage personnel uniquement.

Les codes, tests et documentation de ce projet peuvent être réutilisés sous licence MIT.
