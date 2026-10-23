# Football Odds Analytics — Roadmap du projet

## 1. Présentation

**Objectif :** construire un projet de portfolio orienté Data Analyst à partir de données historiques de football et de cotes de bookmakers.

**Question d'analyse :** les probabilités implicites des cotes reflètent-elles correctement les résultats observés ? Peut-on produire des probabilités mieux calibrées avec un modèle statistique simple ?

**Périmètre initial :**
- Sport : football.
- Compétition : Ligue 1.
- Marché : 1N2 (victoire à domicile, match nul, victoire à l'extérieur).
- Données : plusieurs saisons terminées, en commençant par une seule saison pour valider le pipeline.
- Pas de paris réels : les stratégies éventuellement étudiées seront des simulations historiques, sans garantie de rentabilité future.

## 2. Objectifs pédagogiques et portfolio

Le projet doit démontrer la capacité à :
- collecter et documenter des données externes ;
- contrôler et nettoyer un jeu de données ;
- concevoir un modèle relationnel SQL ;
- développer un pipeline réexécutable et idempotent ;
- réaliser une analyse exploratoire avec SQL et Python ;
- expliquer et comparer des probabilités ;
- entraîner et évaluer un modèle de classification sans fuite de données ;
- présenter les résultats avec des outils libres et open source, en privilégiant les notebooks JupyterLab ;
- éventuellement publier une petite interface interactive avec Streamlit si elle apporte une réelle valeur ;
- documenter les décisions, les limites et les résultats pour un recruteur.

## 3. Stack technique cible

- **Python** : ingestion, validation, transformations et analyses.
- **Pandas** : manipulation des données tabulaires.
- **scikit-learn** : modèles de classification et métriques, dans une phase ultérieure.
- **MariaDB** : stockage relationnel et requêtes analytiques.
- **SQL** : modèle, contrôles, jointures, agrégations et vues.
- **Docker Compose** : environnement reproductible, au minimum pour MariaDB.
- **JupyterLab** : environnement principal d’analyse exploratoire, de statistiques et de visualisation, libre et open source.
- **Matplotlib** (et éventuellement Seaborn) : graphiques reproductibles dans les notebooks.
- **Streamlit** : option libre et open source pour une petite interface interactive, uniquement si utile ; ce n’est pas une priorité.
- **Environnement Python** : toutes les dépendances Python doivent être installées dans un environnement virtuel local `.venv`, jamais dans l’environnement Python système.
- **GitLab ou GitHub** : dépôt, tickets, historique et documentation.

Ne pas ajouter immédiatement Spring Boot, Vue.js, Airflow, dbt ou Snowflake. Ces outils ne seront envisagés que si un besoin concret apparaît. L'objectif est de démontrer les compétences data, pas de construire une application complète.

## 4. Source et gestion des données

Source candidate de départ : Football-Data.co.uk, qui propose des CSV historiques de football et de cotes.

- Page France : https://www.football-data.co.uk/francem.php
- Dictionnaire / notes des colonnes : https://www.football-data.co.uk/notes.txt
- Le dictionnaire doit être consulté pendant l’étude de la source et utilisé pour documenter les colonnes du CSV dans `docs/data-dictionary.md`. Il faut confronter les définitions publiées aux en-têtes et aux valeurs réellement présents dans chaque fichier : la disponibilité et le nom des colonnes peuvent varier selon les saisons.
- Vérifier les conditions d'utilisation et de redistribution avant de publier des données ou des fichiers dérivés.
- Ne pas supposer que les données peuvent être redistribuées librement.
- Pour commencer, utiliser un échantillon local réduit et documenter la provenance.
- Ne pas versionner dans le dépôt les données dont la redistribution n'est pas autorisée.
- Documenter comment obtenir les données autorisées et reproduire le pipeline.

Saisons envisagées pour l'analyse : 2022-2023, 2023-2024 et 2024-2025, sous réserve de disponibilité, de qualité et de compatibilité des colonnes. Commencer par une seule saison complète avant d'élargir.

### Principes de qualité

- Une ligne du référentiel de matchs représente un match.
- Identifier les colonnes source et leurs changements éventuels selon les saisons.
- Distinguer les données connues avant le match des informations produites après le match.
- Conserver les valeurs manquantes comme NULL/valeurs manquantes, sans les remplacer arbitrairement par zéro.
- Contrôler les dates, équipes, scores, cotes et doublons.
- Documenter les exclusions et transformations.
- Conserver la provenance des données et la date d'ingestion.

## 5. Environnement Python isolé

Toutes les dépendances Python du projet doivent être installées dans un environnement virtuel local nommé `.venv`. Il ne faut jamais installer les packages du projet dans le Python système de la machine hôte. Docker reste utilisé pour les services comme MariaDB ; il ne remplace pas l’environnement virtuel Python local.

Depuis la racine du dépôt, sur Linux :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
# Installer ensuite les dépendances du projet dans .venv
python -m pip install pandas matplotlib jupyterlab scikit-learn sqlalchemy pymysql
```

Quand l’environnement est activé, lancer JupyterLab avec :

```bash
jupyter lab
```

Pour quitter l’environnement : `deactivate`. Ajouter `.venv/` à `.gitignore` et ne jamais committer le dossier. Documenter les dépendances dans `pyproject.toml` ou dans un fichier de verrouillage adapté afin de pouvoir recréer l’environnement. Utiliser `python -m pip` plutôt que `pip` seul aide à installer les paquets dans l’interpréteur Python actif.

## 6. Architecture logique

1. **Extract** — Python : lecture/téléchargement des CSV, métadonnées de source et date de collecte.
2. **Raw** — MariaDB : conservation des données importées, sans modifier silencieusement les valeurs source.
3. **Validate** — Python : validation des colonnes, types, valeurs, doublons et règles métier.
4. **Transform** — Python + SQL : normalisation, calcul des probabilités implicites et préparation des tables analytiques.
5. **Analyze** — SQL + Pandas : analyse exploratoire et métriques.
6. **Model** — scikit-learn : modèles de probabilités et évaluation temporelle.
7. **Communicate** — JupyterLab : graphiques et synthèse des résultats dans un notebook reproductible. Streamlit peut être ajouté ultérieurement si une interface interactive est réellement nécessaire.

Le pipeline doit être relançable sans créer de doublons. Les étapes doivent signaler clairement les erreurs et les données rejetées. Pour la première version, une commande CLI simple suffit, par exemple :

```bash
docker compose up -d
python -m pipeline.run --season 2024-2025
```

Cette commande est une cible de conception ; son implémentation viendra avec les modules du pipeline. Les commandes Python doivent être exécutées avec `.venv` activé (voir la section Environnement Python ci-dessous).

## 7. Modèle de données initial

### `teams`
Référentiel des équipes :
- `id`
- `name`
- éventuellement `source_team_name` ou table de correspondance si les noms source varient.

### `matches`
Un enregistrement par match :
- `id`
- `source_match_id` ou clé de déduplication définie et documentée
- `competition`
- `season`
- `match_date`
- `home_team_id`
- `away_team_id`
- `home_goals`
- `away_goals`
- métadonnées d'ingestion si utiles

### `match_odds`
Cotes d'un match pour un bookmaker et un type de cote :
- `id`
- `match_id`
- `bookmaker`
- `odds_type` (par exemple ouverture/clôture si disponible)
- `home_odds`
- `draw_odds`
- `away_odds`
- source ou référence source, si nécessaire

Prévoir une contrainte d'unicité adaptée à la granularité retenue, par exemple match + bookmaker + type de cote.

### `etl_runs`
Historique des exécutions :
- `id`
- `started_at`
- `finished_at`
- `status`
- `source`
- `season`
- compteurs de lignes lues, chargées, rejetées
- message d'erreur éventuel

### `match_predictions`
Prédictions historisées :
- `id`
- `match_id`
- `model_name`
- `model_version`
- `prediction_created_at`
- `prob_home`
- `prob_draw`
- `prob_away`
- jeu de caractéristiques/version de données si nécessaire

Les scores définitifs ne doivent jamais servir de variables explicatives pour prédire le même match avant le coup d'envoi.

## 8. Roadmap par phases

### Phase 1 — Cadrage et étude de la source

**Tâches**
- Confirmer la compétition, le marché 1N2 et les saisons.
- Vérifier les conditions d'utilisation et la provenance des données.
- Télécharger un CSV représentatif.
- Consulter le dictionnaire de données Football-Data : https://www.football-data.co.uk/notes.txt.
- Inventorier les colonnes, types, formats de dates et valeurs manquantes.
- Faire correspondre les noms de colonnes réels aux définitions du dictionnaire et noter les colonnes non documentées ou ambiguës.
- Repérer les variations de schéma entre saisons.
- Définir les questions analytiques principales.

**Livrables**
- `docs/data-source.md`
- `docs/data-dictionary.md` initial, avec nom source, définition, type, disponibilité temporelle et usage analytique de chaque colonne utile
- échantillon local autorisé ou procédure d'obtention
- note de cadrage

**Critères d'acceptation**
- Source et conditions d'utilisation documentées.
- Colonnes nécessaires au périmètre 1N2 identifiées et confrontées au dictionnaire officiel.
- Limites et valeurs manquantes connues.
- Une saison peut être lue avec un script Python simple.

### Phase 2 — Environnement Python, Docker et modèle SQL

**Tâches**
- Créer le dépôt et sa structure initiale.
- Créer un environnement virtuel local `.venv` et y installer les dépendances Python.
- Ajouter `.venv/` à `.gitignore` et ne jamais installer les dépendances du projet dans le Python système.
- Documenter l’activation de l’environnement et l’installation reproductible des dépendances.
- Configurer MariaDB via Docker Compose.
- Définir les tables, clés primaires, clés étrangères et contraintes.
- Définir une clé stable ou une stratégie de déduplication des matchs.
- Ajouter un mécanisme de configuration via variables d'environnement.
- Ne jamais committer les secrets.

**Livrables**
- `compose.yaml`
- `.gitignore` incluant `.venv/`
- `pyproject.toml` (ou fichier de dépendances choisi et documenté)
- `sql/schema.sql`
- `docs/architecture.md`
- `docs/data-dictionary.md`

**Critères d'acceptation**
- L'environnement démarre avec Docker Compose.
- Le schéma peut être créé de manière reproductible.
- Les relations et contraintes importantes sont testées.

### Phase 3 — Ingestion idempotente

**Tâches**
- Écrire le module d'extraction/lecture CSV.
- Normaliser les noms de colonnes et les types.
- Charger les équipes, matchs et cotes.
- Gérer les doublons et les enregistrements incomplets.
- Tracer chaque exécution dans `etl_runs`.
- Faire en sorte qu'une seconde exécution du même import ne duplique pas les lignes.

**Livrables**
- modules `pipeline/extract.py` et `pipeline/load.py`
- tests d'ingestion
- exemples de logs et bilan de chargement

**Critères d'acceptation**
- Import d'une saison réussi.
- Réexécution sans doublons.
- Compteurs de lignes lues, insérées, mises à jour et rejetées disponibles.
- Les erreurs sont explicites et exploitables.

### Phase 4 — Validation et transformations

**Tâches**
- Valider les dates, scores, identifiants d'équipes et cotes.
- Vérifier que les équipes à domicile et à l'extérieur sont différentes.
- Vérifier les cotes strictement positives lorsqu'elles sont renseignées.
- Calculer l'issue 1N2 à partir des scores finaux pour l'analyse historique.
- Calculer les probabilités implicites brutes : `p_i = 1 / cote_i`.
- Calculer une normalisation indicative : `p_i_normalisee = p_i / somme(p_j)` lorsque les trois cotes existent et sont valides.
- Documenter les hypothèses et les lignes exclues.

**Livrables**
- `pipeline/validate.py`
- `pipeline/transform.py`
- tests de règles métier
- rapport de qualité des données

**Critères d'acceptation**
- Les anomalies sont identifiées et quantifiées.
- Les valeurs manquantes ne sont pas converties arbitrairement en zéro.
- Les calculs de probabilités sont testés sur des exemples connus.
- Les exclusions sont documentées.

### Phase 5 — Analyse exploratoire (SQL + Pandas)

**Questions**
- Quelle est la fréquence des victoires à domicile, matchs nuls et victoires à l'extérieur ?
- Ces fréquences évoluent-elles entre saisons ?
- Comment les résultats observés varient-ils selon les tranches de cotes ?
- Quelle est la distribution des buts ?
- Les données diffèrent-elles selon les bookmakers ou les types de cotes, si ces informations sont disponibles ?
- Quelles limites sont dues aux données manquantes ou à la couverture de la source ?

**Livrables**
- requêtes dans `sql/analytics/`
- script ou notebook exploratoire
- graphiques reproductibles
- résumé des constats, sans prétendre à une causalité

**Critères d'acceptation**
- Les principaux indicateurs peuvent être reproduits.
- Les résultats SQL et Python concordent sur des agrégats de contrôle.
- Les conclusions précisent le périmètre et les limites.

### Phase 6 — Analyse et visualisation avec JupyterLab

Cette phase privilégie l’analyse, qui est le cœur du projet, plutôt que la construction d’un dashboard. JupyterLab est libre, open source et fonctionne sous Linux.

**Travaux**
- Créer un notebook reproductible dans `analysis/` ou `notebooks/`.
- Présenter les distributions, tendances et comparaisons avec Pandas et Matplotlib.
- Comparer les probabilités implicites des cotes aux fréquences observées, en précisant les limites de cette comparaison.
- Vérifier les agrégats du notebook avec les requêtes SQL.
- Expliquer chaque graphique avec une interprétation et une limite éventuelle.
- Ne pas construire de dashboard interactif à ce stade. Si un besoin concret apparaît plus tard, évaluer Streamlit, libre et open source.

**Livrables**
- notebook exploratoire reproductible
- graphiques et synthèse des constats
- documentation des indicateurs et limites

**Critères d’acceptation**
- Le notebook s’exécute de bout en bout dans `.venv`.
- Les indicateurs correspondent aux résultats SQL de contrôle.
- Les graphiques indiquent clairement les périodes, unités et populations étudiées.
- Les conclusions distinguent corrélation, description et causalité.

### Phase 7 — Modèles de probabilités

**Approche progressive**
1. Modèle de référence basé sur les probabilités implicites des cotes.
2. Régression logistique multinomiale.
3. Éventuellement, modèle enrichi avec des caractéristiques pré-match, par exemple forme récente ou classement Elo calculé uniquement avec l'historique disponible avant chaque rencontre.

**Tâches**
- Définir une séparation temporelle entre entraînement, validation et test.
- Éviter le mélange aléatoire de matchs de saisons futures dans l'entraînement.
- Calculer les caractéristiques pré-match sans utiliser d'informations postérieures au match.
- Évaluer avec log loss, score de Brier et courbes de calibration.
- Comparer les modèles sur exactement la même période de test.
- Enregistrer le nom/version du modèle et les probabilités prédites.

**Livrables**
- `analysis/train_model.py`
- métriques reproductibles
- graphiques de calibration
- notebook d’évaluation des modèles et graphiques de calibration

**Critères d'acceptation**
- Aucune fuite de données identifiée dans le protocole.
- Une période de test chronologiquement postérieure à l'entraînement est utilisée.
- Les métriques sont documentées et comparables.
- Les conclusions ne confondent pas qualité prédictive et rentabilité garantie.

### Phase 8 — Fiabilisation et portfolio

**Tâches**
- Ajouter tests unitaires sur les transformations et règles métier.
- Ajouter tests d'intégration sur l'ingestion et la base.
- Vérifier le lancement depuis un environnement propre.
- Documenter la configuration et les commandes.
- Ajouter un diagramme d'architecture.
- Écrire les conclusions et les limites.
- Vérifier les conditions de partage des données et des captures.
- Préparer un résumé de projet compréhensible par un recruteur.

**Livrables**
- README principal
- documentation d'installation et d'exécution
- tests automatisés
- diagramme d'architecture
- notebooks d’analyse et d’évaluation reproductibles
- interface Streamlit facultative, uniquement si elle est justifiée
- synthèse des résultats et limites

**Critères d'acceptation**
- Un autre développeur peut comprendre et lancer le projet en suivant le README, avec un accès autorisé aux données.
- Le pipeline est reproductible.
- Les tests critiques passent.
- Le portfolio ne contient ni secrets ni données redistribuées sans autorisation.

## 9. Mesures et précautions statistiques

### Probabilités implicites
Pour une cote décimale `o_i`, la probabilité implicite brute est `p_i = 1 / o_i`. La somme des probabilités brutes d'un marché 1N2 dépasse souvent 1 en raison de la marge du bookmaker. Une normalisation par la somme peut fournir une approximation sans marge, mais elle repose sur une hypothèse simplificatrice.

### Évaluation
- **Log loss** : pénalise fortement les probabilités très confiantes mais erronées.
- **Score de Brier** : mesure l'écart quadratique entre probabilités prédites et résultats observés.
- **Calibration** : parmi les événements auxquels le modèle attribue environ 60 %, environ 60 % devraient se réaliser sur un grand échantillon comparable.

### Prévention des erreurs
- Pas de variables issues du match à prédire.
- Pas de statistiques de forme calculées avec des matchs futurs.
- Les cotes utilisées doivent correspondre au moment auquel elles sont supposées disponibles.
- Validation temporelle plutôt qu'une séparation aléatoire naïve.
- Ne pas conclure à une stratégie rentable à partir d'un petit échantillon.
- Une simulation historique ne garantit pas de résultats futurs.

## 10. Planning indicatif

Estimation initiale : environ 25 à 40 heures de travail, hors difficultés imprévues et apprentissage approfondi.

| Période | Priorité | Estimation |
|---|---|---:|
| Semaine 1 | Cadrage, source, exploration du CSV | 2–4 h |
| Semaine 2 | Docker, schéma SQL | 3–5 h |
| Semaine 3 | Ingestion et contrôles qualité | 3–5 h |
| Semaine 4 | Analyse exploratoire et visualisations JupyterLab | 3–5 h |
| Semaines 5–6 | Modèles et évaluation temporelle | 6–10 h |
| Semaines 7–8 | Tests, documentation et finition | 6–10 h |

Le calendrier est indicatif. Il vaut mieux livrer chaque phase avec des critères d'acceptation que respecter des dates artificielles.

## 11. Structure de dépôt suggérée

```text
football-odds-analytics/
├── data/
│   └── README.md
├── docs/
│   ├── architecture.md
│   ├── data-dictionary.md
│   ├── data-source.md
│   └── methodology.md
├── sql/
│   ├── schema.sql
│   └── analytics/
├── pipeline/
│   ├── extract.py
│   ├── validate.py
│   ├── load.py
│   └── transform.py
├── analysis/
│   ├── exploratory_analysis.py
│   └── train_model.py
├── notebooks/
│   ├── 01_exploration.ipynb
│   └── 02_evaluation_modeles.ipynb
├── tests/
├── compose.yaml
├── .gitignore
├── pyproject.toml
└── README.md
```

Cette structure est une proposition de départ, pas une obligation. Éviter de créer des modules ou des couches sans responsabilité claire.

## 12. Backlog initial

### T1 — Cadrer le jeu de données
- Choisir la source, les saisons, la compétition et le marché.
- Vérifier les conditions d'utilisation.
- Définir les questions analytiques.
- **Acceptation :** périmètre et source documentés, CSV représentatif inspecté.

### T2 — Étudier le CSV source
- Inventorier colonnes, types, formats de date et valeurs manquantes.
- Identifier les variations de schéma selon les saisons.
- **Acceptation :** dictionnaire de données initial et anomalies connues.

### T3 — Définir le modèle relationnel
- Définir tables, clés, contraintes et stratégie de déduplication.
- **Acceptation :** schéma SQL et diagramme relationnel validés.

### T4 — Créer l'ingestion idempotente
- Importer une saison sans doublons.
- Tracer les exécutions et compteurs.
- **Acceptation :** réexécuter le même import ne duplique pas les matchs.

### T5 — Valider les données
- Tester scores, issues 1N2, cotes, dates et clés.
- **Acceptation :** anomalies détectées, quantifiées et documentées.

## 13. Instructions à l'IA qui aidera à développer le projet

- Agir comme un mentor technique data et avancer phase par phase.
- Commencer par T1 ; ne pas générer tout le projet d'un coup.
- Poser une question seulement lorsqu'une décision bloquante est nécessaire ; sinon expliciter les hypothèses raisonnables.
- Pour chaque ticket, fournir : objectif, contexte, décisions techniques, fichiers à créer/modifier, étapes d'implémentation, tests et critères d'acceptation.
- Toute commande Python doit utiliser l’environnement virtuel local `.venv` ; ne jamais installer de packages Python dans l’environnement système de l’hôte.
- Consulter https://www.football-data.co.uk/notes.txt pour interpréter les colonnes source et consigner les correspondances vérifiées dans `docs/data-dictionary.md`.
- Privilégier JupyterLab, libre et open source, pour l’analyse et les graphiques ; ne proposer Streamlit que si une interface interactive répond à un besoin concret.
- Privilégier du code Python et SQL simple, explicite et maintenable.
- Expliquer les notions data et statistiques nouvelles avec des exemples concrets.
- Ne pas introduire d'outils supplémentaires sans bénéfice démontré.
- Ne jamais inventer la structure d'un CSV : inspecter les en-têtes et quelques lignes avant d'écrire le parseur.
- Séparer les données brutes, les transformations et les résultats analytiques.
- Préserver la reproductibilité, la traçabilité, la qualité et les contraintes de licence des données.
- Éviter toute fuite de données dans les modèles.
- Ne pas présenter les simulations de paris comme une promesse de rentabilité.
- Ne passer à la phase suivante qu'après validation des critères d'acceptation de la phase courante.
