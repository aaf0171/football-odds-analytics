# Méthodologie et questions analytiques — Football Odds Analytics

## Questions analytiques principales

### Question centrale
> Les probabilités implicites des cotes de bookmakers reflètent-elles correctement les résultats observés en Ligue 1 ? Peut-on produire des probabilités mieux calibrées avec un modèle statistique simple ?

### Questions dérivées

1. **Calibration des cotes :**
   - Dans quelle mesure les probabilités implicites (`1/cote`) des bookmakers correspondent-elles aux fréquences observées des issues 1N2 ?
   - Les bookmakers sur-estiment-ils systématiquement la probabilité de victoire à domicile ?
   - Existe-t-il un écart systématique entre les cotes d'ouverture et les cotes de clôture ?

2. **Effet domicile :**
   - Quelle est la fréquence observée des victoires à domicile en Ligue 1 ?
   - Cette fréquence évolue-t-elle selon le niveau de cote accordée au favori ?

3. **Comparaison des bookmakers :**
   - Les probabilités déduites des cotes de différents bookmakers (Bet365, Betfair, Pinnacle, William Hill, 1XBet) convergent-elles vers les mêmes distributions ?
   - Un bookmaker est-il systématiquement plus proche de la réalité observée qu'un autre ?

4. **Distribution des buts :**
   - Quelle est la distribution moyenne des buts marqués à domicile et à l'extérieur ?
   - Existe-t-il une corrélation entre l'écart de cotes et l'écart de buts ?

5. **Valeur prédictive des cotes moyennes/max :**
   - Les cotes moyennes du marché (`AvgH`, `AvgD`, `AvgA`) sont-elles plus prédictives que les cotes d'un bookmaker unique ?
   - Les cotes maximales (`MaxH`, `MaxD`, `MaxA`) apportent-elles une information complémentaire ?

## Approche méthodologique

### Phase 1 — Analyse descriptive
- Calculer les fréquences empiriques de chaque issue 1N2 par saison.
- Visualiser les distributions de cotes par bookmaker.
- Calculer les probabilités implicites brutes et normalisées.

### Phase 2 — Analyse comparative
- Comparer les fréquences observées aux probabilités implicites.
- Mesurer les écarts (résidus) entre probabilités implicites et fréquences réelles.
- Explorer les différences entre bookmakers.

### Phase 3 — Modélisation (Phase 7 de la roadmap)
- Entraîner un modèle de régression logistique multinomiale.
- Évaluer la qualité prédictive via log loss, score de Brier et courbes de calibration.
- Comparer aux probabilités implicites des cotes comme ligne de base.

## Précautions méthodologiques

- **Pas de fuite de données :** les caractéristiques utilisées pour prédire un match ne peuvent pas inclure d'informations postérieures au coup d'envoi.
- **Séparation temporelle :** entraînement et test sont séparés chronologiquement (pas de split aléatoire).
- **Interprétation prudente :** une corrélation ne signifie pas causalité. Les résultats sont des constats historiques, pas des recommandations de paris.
- **Reproductibilité :** tous les calculs sont exécutés dans des notebooks JupyterLab versionnés, avec l'environnement Python isolé dans `.venv`.

## Règles de transformation (Phase 7 / T7)

### Issue 1N2
L'issue est calculée à partir des scores finaux :

| Condition | Issue |
|---|---|
| `home_goals > away_goals` | `H` (victoire domicile) |
| `home_goals = away_goals` | `D` (match nul) |
| `home_goals < away_goals` | `A` (victoire extérieur) |
| Un score est `NULL` | `NULL` (impossible de calculer) |

Les scores manquants ne sont jamais imputés.

### Probabilités implicites brutes
Pour une cote décimale `o_i > 0` :

```
p_brute_i = 1 / o_i
```

- Si la cote est `NULL`, nulle ou négative, la probabilité brute est `NULL`.
- La somme des probabilités brutes d'un marché 1N2 dépasse 1 en raison de la marge du bookmaker.

### Probabilités implicites normalisées
Pour un triplet complet de cotes valides :

```
p_norm_i = p_brute_i / (p_brute_home + p_brute_draw + p_brute_away)
```

- La normalisation n'est calculée que si les **trois** cotes existent, sont finies et strictement positives.
- Si l'une des cotes est manquante ou invalide, les trois probabilités normalisées sont `NULL`.
- La normalisation fournit une approximation sans marge, pas une vérité sur la marge réelle du bookmaker.

### Marge du bookmaker

```
marge = p_brute_home + p_brute_draw + p_brute_away - 1
```

Exprimée en pourcentage, la marge représente le pourcentage théorique perdu par un parieur sur un grand nombre de mises équilibrées.

## Livrables analytiques

- Requêtes SQL analytiques dans `sql/analytics/`
- Notebook exploratoire dans `notebooks/01_exploration.ipynb`
- Notebook d'évaluation des modèles dans `notebooks/02_evaluation_modeles.ipynb`
- Graphiques reproductibles avec Matplotlib

## Limites connues

- Les données proviennent d'une seule source (Football-Data.co.uk), dont la qualité n'est pas vérifiée de manière indépendante.
- Seules les cotes pré-fermeture (et non les cotes en live) sont disponibles pour certaines saisons.
- Les données ne couvrent pas toutes les ligues : l'analyse se limite à la Ligue 1 française pour l'instant.
- Les simulations de paris ne constituent pas une prédiction de performance future.
