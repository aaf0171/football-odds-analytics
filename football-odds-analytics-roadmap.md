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

**Objectif**

Définir un périmètre d'analyse clair et réalisable.

**Contexte**

Le projet étudie les probabilités implicites des cotes du marché 1N2 de Ligue 1 et leur adéquation aux résultats observés.

**Décisions techniques**

- Commencer par une saison complète et élargir uniquement après validation du pipeline.
- Utiliser Football-Data.co.uk comme source candidate, sous réserve de vérifier les conditions d'utilisation.
- Ne pas supposer que les données peuvent être redistribuées librement.

**Fichiers à créer/modifier**

- `docs/data-source.md`
- `docs/methodology.md`, si utile
- `README.md`, si nécessaire pour présenter le périmètre

**Étapes d'implémentation**

1. Confirmer la compétition, la saison, le marché et les questions analytiques.
2. Examiner la page source et ses conditions d'utilisation.
3. Choisir un CSV représentatif et vérifier qu'il est accessible.
4. Documenter la provenance, les limites et les conditions d'obtention des données.

**Tests et vérifications**

- Vérifier que la source et le fichier choisis sont accessibles.
- Vérifier que le périmètre retenu correspond aux questions analytiques.

**Critères d'acceptation**

- Le périmètre et les questions analytiques sont documentés.
- La source, sa provenance et les conditions d'utilisation sont décrites.
- Un CSV représentatif a été inspecté sans être nécessairement ajouté au dépôt.

### T2 — Étudier le CSV source

**Objectif**

Comprendre la structure réelle du CSV avant de développer le parseur.

**Contexte**

Les noms et la disponibilité des colonnes peuvent varier d'une saison à l'autre. Le dictionnaire publié par la source doit être confronté aux fichiers réels.

**Décisions techniques**

- Consulter `https://www.football-data.co.uk/notes.txt`.
- Ne pas inventer de colonnes ni déduire leur signification uniquement à partir de leur nom.
- Distinguer les informations disponibles avant le match de celles produites après le match.

**Fichiers à créer/modifier**

- `docs/data-dictionary.md`
- `docs/data-source.md`

**Étapes d'implémentation**

1. Inspecter les en-têtes et un échantillon de lignes.
2. Recenser les types, formats de date, valeurs manquantes et anomalies visibles.
3. Comparer les colonnes réelles au dictionnaire officiel.
4. Documenter les correspondances vérifiées, les colonnes ambiguës et les variations éventuelles entre saisons.

**Tests et vérifications**

- Vérifier que chaque colonne utilisée dans le périmètre possède une définition documentée ou une mention explicite « non documentée ».
- Vérifier que les colonnes nécessaires au marché 1N2 sont présentes dans le fichier retenu.

**Critères d'acceptation**

- Le dictionnaire initial documente les noms source, définitions, types, disponibilité temporelle et usages analytiques des colonnes utiles.
- Les anomalies et variations de schéma connues sont consignées.
- Les colonnes nécessaires à l'analyse sont identifiées sans hypothèse non vérifiée.

### T3 — Définir le modèle relationnel

**Objectif**

Concevoir un schéma SQL qui conserve les matchs, équipes, cotes et exécutions d'ingestion de façon cohérente.

**Contexte**

Le modèle initial est décrit dans la section 7 de la roadmap. Il doit permettre de dédupliquer les matchs et de conserver plusieurs types de cotes lorsque les données les proposent.

**Décisions techniques**

- Utiliser MariaDB et le schéma défini dans la roadmap comme point de départ.
- Définir une clé stable ou une stratégie de déduplication documentée.
- Ne pas ajouter de table ou de couche sans besoin démontré.
- Utiliser des clés étrangères et contraintes d'unicité adaptées à la granularité des données.

**Fichiers à créer/modifier**

- `sql/schema.sql`
- `docs/architecture.md`
- `docs/data-dictionary.md`
- Un diagramme relationnel dans `docs/`, si nécessaire

**Étapes d'implémentation**

1. Inspecter les fichiers existants et confirmer les entités nécessaires.
2. Définir les tables `teams`, `matches`, `match_odds` et `etl_runs`.
3. Ajouter les clés primaires, clés étrangères, contraintes et types.
4. Définir la contrainte d'unicité des cotes en fonction du match, du bookmaker et du type de cote.
5. Documenter la stratégie de déduplication et les choix non évidents.

**Tests et vérifications**

- Créer le schéma sur une base MariaDB vierge.
- Vérifier les clés étrangères et contraintes d'unicité.
- Vérifier qu'un match ou une cote dupliqués sont rejetés ou traités selon la stratégie documentée.

**Critères d'acceptation**

- Le schéma SQL est reproductible.
- Les relations et contraintes importantes sont testées.
- La stratégie de déduplication est documentée et cohérente avec les colonnes réelles.

### T4 — Créer l'ingestion idempotente

**Objectif**

Importer une saison sans créer de doublons et tracer chaque exécution.

**Contexte**

L'ingestion doit séparer la lecture de la source, le chargement en base et le suivi des résultats. Elle doit pouvoir être relancée après une erreur.

**Décisions techniques**

- Utiliser Python avec les dépendances installées dans `.venv`.
- Séparer les responsabilités entre extraction/lecture et chargement.
- Conserver les valeurs source sans transformation silencieuse.
- Ne pas versionner les données si leur redistribution n'est pas autorisée.

**Fichiers à créer/modifier**

- `pipeline/extract.py`
- `pipeline/load.py`
- `pipeline/`, pour les modules auxiliaires strictement nécessaires
- `tests/`, pour les tests d'ingestion
- `data/README.md`

**Étapes d'implémentation**

1. Lire le CSV à partir d'un chemin configurable.
2. Normaliser les noms de colonnes et convertir les types nécessaires sans perdre la traçabilité des valeurs source.
3. Charger les équipes, matchs et cotes en respectant le schéma.
4. Gérer les doublons et enregistrements incomplets selon des règles explicites.
5. Enregistrer dans `etl_runs` le statut, la saison et les compteurs de lignes lues, insérées, mises à jour et rejetées.
6. Documenter la commande permettant de lancer l'import.

**Tests et vérifications**

- Tester le chargement d'un petit fichier représentatif.
- Lancer deux fois le même import et comparer les nombres de lignes.
- Tester le comportement face à une ligne invalide et à une erreur de chargement.
- Vérifier que le bilan d'exécution correspond aux lignes traitées.

**Critères d'acceptation**

- Une saison peut être importée.
- Une seconde exécution identique ne crée pas de doublons.
- Les compteurs de lignes lues, insérées, mises à jour et rejetées sont disponibles.
- Les erreurs sont explicites et exploitables.

### T5 — Valider les données

**Objectif**

Détecter et quantifier les anomalies avant les analyses statistiques.

**Contexte**

Des données invalides ou mal interprétées peuvent fausser les résultats. Les valeurs manquantes ne doivent pas être transformées arbitrairement en zéro.

**Décisions techniques**

- Distinguer les erreurs bloquantes des anomalies qui peuvent être conservées et signalées.
- Conserver les valeurs manquantes comme valeurs manquantes/`NULL`.
- Calculer l'issue historique 1N2 à partir des scores finaux uniquement pour l'analyse après-match.
- Ne pas utiliser de données postérieures au match comme variables prédictives pré-match.

**Fichiers à créer/modifier**

- `pipeline/validate.py`
- `tests/`, pour les règles de validation
- `docs/data-dictionary.md`, si les contrôles révèlent une ambiguïté
- Un rapport de qualité dans `reports/` ou un emplacement équivalent déjà utilisé

**Étapes d'implémentation**

1. Valider les dates, équipes, scores et cotes.
2. Vérifier que les équipes à domicile et à l'extérieur sont différentes.
3. Vérifier que les cotes renseignées sont strictement positives.
4. Contrôler les doublons, clés orphelines et valeurs manquantes.
5. Quantifier les anomalies et documenter les règles d'exclusion.
6. Produire un rapport de qualité lisible.

**Tests et vérifications**

- Tester des exemples valides et invalides pour chaque règle.
- Vérifier que les valeurs manquantes ne sont pas remplacées par zéro.
- Vérifier que les anomalies détectées sont comptabilisées de manière reproductible.

**Critères d'acceptation**

- Les anomalies sont identifiées, quantifiées et documentées.
- Les règles métier principales sont couvertes par des tests.
- Les exclusions sont explicites et ne masquent pas silencieusement des données.

### T6 — Finaliser l'environnement reproductible

**Objectif**

Permettre de recréer et d'exécuter l'environnement du projet sans installer de dépendances Python dans le système hôte.

**Contexte**

La roadmap impose un environnement virtuel local `.venv`, MariaDB via Docker Compose et une configuration sans secrets dans le dépôt. Ce ticket complète les éléments qui ne seraient pas déjà réalisés pendant T1 à T5.

**Décisions techniques**

- Utiliser `.venv` pour toutes les dépendances Python.
- Utiliser Docker Compose au minimum pour MariaDB.
- Déclarer les dépendances dans `pyproject.toml` ou dans un fichier de dépendances choisi et documenté.
- Lire les paramètres de connexion depuis des variables d'environnement ; ne pas committer de secrets.
- Ne pas ajouter de service ou d'outil d'orchestration supplémentaire.

**Fichiers à créer/modifier**

- `compose.yaml`
- `.gitignore`
- `pyproject.toml` ou fichier de dépendances retenu
- `.env.example`, avec uniquement des valeurs fictives/non sensibles
- `README.md` ou `docs/architecture.md`

**Étapes d'implémentation**

1. Inspecter l'environnement et les fichiers existants ; ne pas écraser une configuration fonctionnelle sans raison.
2. Vérifier que `.venv/` est ignoré par Git.
3. Déclarer les dépendances réellement utilisées par le projet.
4. Configurer MariaDB dans Docker Compose et rendre les paramètres configurables.
5. Documenter la création/activation de `.venv`, l'installation des dépendances et le démarrage des services.
6. Vérifier que les commandes Python documentées utilisent l'interpréteur de `.venv`.

**Tests et vérifications**

- Recréer `.venv` à partir des instructions documentées.
- Démarrer MariaDB avec Docker Compose et vérifier que le service est disponible.
- Vérifier que la configuration fonctionne sans fichier contenant de vrais secrets.
- Vérifier que `.venv/` et les fichiers secrets ne sont pas suivis par Git.

**Critères d'acceptation**

- L'environnement Python peut être recréé à partir du dépôt.
- MariaDB démarre avec Docker Compose.
- Les dépendances du projet ne sont pas installées dans le Python système.
- Aucun secret ni dossier `.venv/` n'est versionné.
- Les commandes nécessaires sont documentées.

### T7 — Transformer les données et calculer les probabilités implicites

**Objectif**

Produire un jeu de données analytique cohérent à partir des données validées et calculer les probabilités issues des cotes.

**Contexte**

La roadmap prévoit de calculer l'issue 1N2 à partir des scores finaux et les probabilités implicites à partir des cotes décimales. Les calculs doivent respecter les valeurs manquantes et la disponibilité temporelle des données.

**Décisions techniques**

- Calculer la probabilité implicite brute par `p = 1 / cote`.
- Calculer la probabilité normalisée par `p_normalisee = p / somme(p_i)` seulement lorsque les trois cotes sont présentes, finies et strictement positives.
- Considérer la normalisation comme une approximation indicative sans marge, pas comme une vérité exacte sur la marge du bookmaker.
- Ne pas imputer les cotes manquantes.
- Réutiliser les tables et modules existants plutôt que créer un second pipeline de transformations.

**Fichiers à créer/modifier**

- `pipeline/transform.py`
- `sql/analytics/`, pour les vues ou requêtes analytiques nécessaires
- `tests/`, pour les tests de transformation
- `docs/methodology.md`
- `docs/data-dictionary.md`, si de nouveaux champs calculés y sont décrits

**Étapes d'implémentation**

1. Inspecter le schéma et les modules d'ingestion/validation existants.
2. Définir et documenter les règles de calcul de l'issue 1N2.
3. Calculer les probabilités brutes pour chaque cote valide.
4. Calculer les probabilités normalisées uniquement pour les triplets complets et valides.
5. Définir le traitement des cotes absentes ou invalides sans les remplacer arbitrairement.
6. Exposer les champs nécessaires aux analyses SQL et Python.

**Tests et vérifications**

- Tester les trois issues possibles : victoire domicile, nul et victoire extérieur.
- Tester une cote connue, par exemple une cote de 2,00 donnant une probabilité brute de 0,5.
- Vérifier que les probabilités normalisées d'un triplet valide somment à environ 1.
- Tester les valeurs manquantes, nulles, négatives et non finies.
- Vérifier que les résultats calculés sont reproductibles.

**Critères d'acceptation**

- Les transformations et hypothèses sont documentées.
- Les calculs sont couverts par des tests automatisés.
- Les données manquantes ou invalides ne produisent pas de probabilités artificielles.
- Les champs calculés peuvent être utilisés dans les analyses.

### T8 — Réaliser l'analyse exploratoire SQL

**Objectif**

Répondre aux premières questions descriptives avec des requêtes SQL reproductibles.

**Contexte**

Cette phase doit fournir une base de résultats vérifiables avant de construire les notebooks et les modèles. Les constats décrivent des associations et des distributions ; ils ne démontrent pas de causalité.

**Décisions techniques**

- Utiliser MariaDB et les tables/vues déjà définies.
- Conserver les requêtes dans le dépôt.
- Afficher le périmètre, la période et le nombre d'observations derrière chaque indicateur.
- Ne comparer les bookmakers ou types de cotes que si les colonnes correspondantes existent et sont suffisamment renseignées.

**Fichiers à créer/modifier**

- `sql/analytics/`, avec des fichiers SQL nommés de façon explicite
- `docs/methodology.md`
- Éventuellement `reports/`, pour un résumé exporté des résultats

**Étapes d'implémentation**

1. Calculer la fréquence des victoires à domicile, des nuls et des victoires à l'extérieur.
2. Comparer ces fréquences entre les saisons disponibles.
3. Examiner les résultats selon les tranches de cotes.
4. Décrire la distribution des buts.
5. Comparer les bookmakers ou types de cotes si les données le permettent.
6. Mesurer la couverture des données et les exclusions qui affectent chaque analyse.
7. Documenter les résultats intéressants et les limites d'interprétation.

**Tests et vérifications**

- Exécuter les requêtes sur une base initialisée avec le pipeline.
- Vérifier que les catégories 1N2 couvrent tous les matchs admissibles, hors exclusions documentées.
- Contrôler les dénominateurs et les valeurs manquantes.
- Vérifier manuellement quelques agrégats sur un petit échantillon.

**Critères d'acceptation**

- Les requêtes principales sont versionnées et réexécutables.
- Les indicateurs sont accompagnés de leurs périodes, populations et dénominateurs.
- Les limites dues aux données manquantes et à la couverture sont documentées.
- Les résultats ne sont pas présentés comme des relations causales.

### T9 — Construire le notebook d'analyse exploratoire

**Objectif**

Présenter et interpréter les principaux résultats descriptifs dans un notebook JupyterLab reproductible.

**Contexte**

L'analyse est le cœur du portfolio. Le notebook doit privilégier l'interprétation statistique plutôt que la construction d'un dashboard. Les résultats doivent pouvoir être rapprochés des agrégats SQL.

**Décisions techniques**

- Utiliser JupyterLab, Pandas et Matplotlib dans `.venv`.
- Utiliser les requêtes SQL de T8 comme points de contrôle.
- Éviter les visualisations décoratives qui n'apportent pas de réponse à une question.
- Expliquer pour chaque graphique ce qu'il montre, ce qu'il ne permet pas de conclure et les limites de l'échantillon.

**Fichiers à créer/modifier**

- `notebooks/01_exploration.ipynb`
- `analysis/exploratory_analysis.py`, uniquement si du code réutilisable hors notebook est nécessaire
- `docs/methodology.md`
- `README.md`, si un résumé des résultats doit y figurer

**Étapes d'implémentation**

1. Charger les données analytiques avec une méthode documentée.
2. Présenter la période, le périmètre et les contrôles de qualité.
3. Visualiser les fréquences 1N2, les distributions de buts et les résultats selon les tranches de cotes.
4. Comparer les probabilités implicites aux fréquences observées en expliquant les limites de cette comparaison.
5. Vérifier les agrégats principaux par rapport à SQL.
6. Rédiger une interprétation et une limite pour chaque résultat important.

**Tests et vérifications**

- Exécuter le notebook de haut en bas dans `.venv`.
- Vérifier qu'il ne dépend pas d'un chemin absolu propre à la machine.
- Comparer les agrégats clés avec ceux de T8.
- Vérifier que les graphiques ont titres, axes, unités et périodes explicites.

**Critères d'acceptation**

- Le notebook s'exécute de bout en bout avec les instructions du projet.
- Les indicateurs concordent avec les contrôles SQL.
- Les graphiques sont lisibles et interprétables.
- Les conclusions distinguent description, association et causalité.
- Aucun dashboard interactif n'est créé à ce stade.

### T10 — Établir le modèle de référence des bookmakers

**Objectif**

Évaluer la qualité des probabilités issues des cotes avant de développer un modèle prédictif propre.

**Contexte**

Une comparaison pertinente exige de comparer des probabilités et des résultats sur les mêmes matchs. Les probabilités brutes et normalisées n'ont pas la même interprétation, notamment en raison de la marge du bookmaker.

**Décisions techniques**

- Utiliser les probabilités normalisées comme baseline principale lorsque les trois cotes sont disponibles et valides.
- Conserver les probabilités brutes à des fins descriptives, notamment pour examiner la somme des probabilités et la marge implicite.
- N'utiliser que des cotes correspondant à un moment de disponibilité défini et documenté.
- Évaluer sur les mêmes observations que les modèles ultérieurs.
- Ne pas interpréter la baseline comme une garantie de rentabilité.

**Fichiers à créer/modifier**

- `notebooks/02_evaluation_modeles.ipynb` ou un notebook de baseline distinct si cela rend le travail plus lisible
- `analysis/`, pour le code d'évaluation réutilisable si nécessaire
- `docs/methodology.md`
- `tests/`, pour les calculs de métriques

**Étapes d'implémentation**

1. Définir les observations admissibles et la période d'évaluation.
2. Construire le vecteur des probabilités 1N2 pour chaque match retenu.
3. Calculer la log loss et le score de Brier multiclasses.
4. Examiner la calibration des probabilités, en explicitant la méthode retenue.
5. Calculer et commenter la somme des probabilités brutes comme indicateur de marge implicite.
6. Enregistrer les résultats de référence avec le périmètre exact utilisé.

**Tests et vérifications**

- Vérifier les métriques sur de petits exemples dont le résultat attendu est connu.
- Vérifier que chaque ligne évaluée possède une issue réelle valide et un vecteur de probabilités valide.
- Vérifier que les probabilités sont comprises entre 0 et 1 et que leur somme vaut environ 1 pour la baseline normalisée.
- Vérifier que les observations retenues sont identiques à celles qui seront utilisées pour comparer les modèles.

**Critères d'acceptation**

- Une baseline bookmaker est calculée et documentée.
- Les métriques et leurs limites sont expliquées.
- Le périmètre de comparaison est enregistré et reproductible.
- Les résultats de la baseline pourront être comparés aux modèles ultérieurs sur le même test.

### T11 — Entraîner un modèle de classification pré-match

**Objectif**

Construire un premier modèle de classification multinomiale et le comparer à la baseline bookmaker.

**Contexte**

Le modèle doit prédire les probabilités de victoire à domicile, de match nul et de victoire à l'extérieur. Il ne doit utiliser que des informations disponibles avant le match prédit.

**Décisions techniques**

- Utiliser scikit-learn et commencer par une régression logistique multinomiale.
- Définir les ensembles d'entraînement, de validation et de test chronologiquement.
- Commencer par un jeu de caractéristiques simple et justifié ; n'ajouter les caractéristiques de forme ou un classement Elo que si leur calcul utilise exclusivement l'historique disponible avant chaque match.
- Exclure les scores et statistiques produits pendant ou après le match à prédire.
- Éviter les caractéristiques qui dupliquent directement l'issue cible.
- Ne pas ajouter de modèle complexe avant d'avoir évalué cette première baseline.

**Fichiers à créer/modifier**

- `analysis/train_model.py`
- `notebooks/02_evaluation_modeles.ipynb`
- `docs/methodology.md`
- `tests/`, pour la construction des caractéristiques et la séparation temporelle

**Étapes d'implémentation**

1. Définir la cible 1N2 et les caractéristiques pré-match disponibles.
2. Construire une séparation temporelle et documenter les dates utilisées.
3. Préparer les données et traiter les valeurs manquantes avec une méthode explicite.
4. Entraîner une régression logistique multinomiale avec scikit-learn.
5. Produire les probabilités prédites sur les ensembles de validation et de test.
6. Enregistrer la configuration du modèle et les versions pertinentes.
7. Comparer les premiers résultats à la baseline sans modifier le périmètre de test.

**Tests et vérifications**

- Vérifier qu'aucune caractéristique ne contient d'information postérieure au coup d'envoi.
- Vérifier que les données d'entraînement sont chronologiquement antérieures au test.
- Vérifier que le modèle produit trois probabilités valides par match et que leur somme est proche de 1.
- Tester le pipeline de préparation sur un petit échantillon connu.

**Critères d'acceptation**

- Le modèle s'entraîne et produit des probabilités reproductibles.
- La séparation temporelle est documentée et testée.
- Les caractéristiques et leur disponibilité temporelle sont documentées.
- Aucune fuite de données connue n'est identifiée.
- Les résultats sont comparables à la baseline bookmaker.

### T12 — Évaluer et comparer les modèles

**Objectif**

Déterminer si le modèle apporte une amélioration mesurable par rapport aux probabilités des bookmakers sur une période de test postérieure à l'entraînement.

**Contexte**

Une bonne classification des issues les plus fréquentes ne suffit pas à démontrer la qualité des probabilités. Il faut examiner les métriques probabilistes et leur calibration sur un test chronologique commun.

**Décisions techniques**

- Utiliser la log loss, le score de Brier multiclasses et des graphiques de calibration adaptés au problème 1N2.
- Comparer la baseline bookmaker et le modèle sur exactement les mêmes matchs.
- Conserver une période de test non utilisée pour le choix des caractéristiques ou des hyperparamètres.
- Décrire les résultats sans conclure à une rentabilité future.
- Documenter les limites liées à la taille de l'échantillon, aux saisons et aux données manquantes.

**Fichiers à créer/modifier**

- `notebooks/02_evaluation_modeles.ipynb`
- `analysis/`, pour les fonctions de métriques si nécessaire
- `docs/methodology.md`
- `README.md`, pour la synthèse finale si les résultats sont stabilisés

**Étapes d'implémentation**

1. Vérifier et figer le périmètre du test.
2. Calculer les métriques de la baseline et du modèle sur les mêmes observations.
3. Produire des graphiques de calibration pour les issues 1N2 selon une méthode documentée.
4. Examiner les écarts entre modèles et leur stabilité selon les périodes, si l'échantillon le permet.
5. Interpréter les différences sans surinterpréter de petits écarts.
6. Consigner les limites, résultats négatifs et pistes d'amélioration.

**Tests et vérifications**

- Vérifier que les deux méthodes sont évaluées sur les mêmes matchs et les mêmes issues.
- Vérifier les calculs de métriques sur des exemples contrôlés.
- Vérifier que les probabilités invalides et les observations exclues sont détectées.
- Réexécuter le notebook et comparer les résultats à ceux documentés.

**Critères d'acceptation**

- Les métriques sont calculées, documentées et reproductibles.
- Les modèles sont comparés sur un test temporel commun.
- Les graphiques de calibration sont lisibles et correctement interprétés.
- La conclusion indique clairement si le modèle améliore, égale ou dégrade la baseline sur le test observé.
- Aucune promesse de rentabilité n'est formulée.

### T13 — Fiabiliser le pipeline et vérifier la reproductibilité

**Objectif**

Vérifier que le projet fonctionne depuis un environnement propre et que ses étapes critiques sont couvertes par des tests.

**Contexte**

Les tests doivent protéger les transformations, l'ingestion et les calculs statistiques contre les régressions. Ils ne doivent pas rendre l'architecture inutilement complexe.

**Décisions techniques**

- Utiliser l'outil de test Python déjà retenu ou, si aucun n'est configuré, choisir une solution simple et la documenter.
- Séparer les tests unitaires des tests nécessitant MariaDB.
- Utiliser de petites données synthétiques pour les tests unitaires ; ne pas dépendre du téléchargement d'une source externe pendant les tests.
- Garder les tests déterministes et indépendants de chemins propres à la machine.

**Fichiers à créer/modifier**

- `tests/`
- `pyproject.toml` ou fichier de dépendances
- `README.md`
- `docs/architecture.md`
- Les modules du pipeline uniquement si les tests révèlent un défaut

**Étapes d'implémentation**

1. Recenser les règles critiques et les tests déjà présents.
2. Ajouter ou compléter les tests unitaires de validation, transformation et calcul des probabilités.
3. Ajouter des tests d'intégration de l'ingestion et du schéma MariaDB.
4. Tester l'idempotence et la gestion des erreurs.
5. Exécuter les tests depuis l'environnement `.venv`.
6. Vérifier les instructions de démarrage depuis un dépôt propre et documenter les éventuels prérequis.

**Tests et vérifications**

- Exécuter toute la suite de tests documentée.
- Vérifier que les tests unitaires ne nécessitent pas Internet.
- Vérifier que les tests d'intégration échouent clairement si MariaDB n'est pas disponible.
- Vérifier que les données ou secrets locaux ne sont pas requis implicitement.

**Critères d'acceptation**

- Les tests critiques passent dans un environnement documenté.
- Les règles de validation, transformations et calculs de probabilités sont couvertes.
- L'ingestion idempotente est vérifiée par un test.
- Le projet peut être démarré en suivant les instructions sans configuration cachée.

### T14 — Finaliser le portfolio et communiquer les résultats

**Objectif**

Présenter le projet, sa démarche analytique, ses résultats et ses limites à un recruteur ou à un autre analyste.

**Contexte**

Le portfolio doit mettre en avant le raisonnement data et la capacité à interpréter les résultats. Il ne doit pas se limiter à une démonstration technique du pipeline.

**Décisions techniques**

- Utiliser JupyterLab et des graphiques reproductibles comme supports principaux.
- Ne créer une interface Streamlit que si un besoin concret est démontré ; elle n'est pas requise pour terminer le projet.
- Ne publier que des données et éléments visuels dont le partage est autorisé.
- Distinguer les faits observés, les hypothèses, les limites et les pistes d'amélioration.
- Ne pas présenter les simulations historiques comme une promesse de gains futurs.

**Fichiers à créer/modifier**

- `README.md`
- `docs/architecture.md`
- `docs/data-source.md`
- `docs/data-dictionary.md`
- `docs/methodology.md`
- `notebooks/01_exploration.ipynb`
- `notebooks/02_evaluation_modeles.ipynb`
- Un diagramme d'architecture dans `docs/`, si nécessaire

**Étapes d'implémentation**

1. Présenter la question analytique, le périmètre et la source des données.
2. Documenter les étapes du pipeline et les commandes de reproduction.
3. Résumer les résultats exploratoires et la comparaison des probabilités.
4. Présenter les métriques des modèles, y compris les résultats négatifs ou non concluants.
5. Expliquer les limites statistiques, les biais possibles et les restrictions de redistribution.
6. Vérifier que les notebooks sont lisibles et s'exécutent de bout en bout.
7. Rédiger un résumé synthétique destiné à un recruteur.

**Tests et vérifications**

- Suivre les instructions du README depuis un environnement propre.
- Réexécuter les notebooks dans l'ordre requis.
- Vérifier que les résultats présentés correspondent aux sorties du projet.
- Vérifier l'absence de secrets et de données non autorisées dans le dépôt.
- Vérifier les liens internes et les chemins des fichiers documentés.

**Critères d'acceptation**

- Un tiers peut comprendre l'objectif, la démarche et les conclusions.
- L'installation et l'exécution sont documentées et reproductibles, avec un accès autorisé aux données.
- Les notebooks et tests critiques fonctionnent.
- Les limites, hypothèses et conditions de partage sont clairement indiquées.
- Le portfolio met en avant l'analyse et l'interprétation, pas uniquement l'infrastructure.
- Streamlit reste facultatif et n'est ajouté que s'il apporte une valeur démontrable.
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
