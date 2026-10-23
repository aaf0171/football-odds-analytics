# Source des données — Football Odds Analytics

## Source principale

**Nom :** Football-Data.co.uk  
**URL :** https://www.football-data.co.uk/  
**Auteur :** Joseph Buchdahl  
**Licence :** Données gratuites à usage personnel / analyse quantitative. Redistribution non autorisée sans accord explicite.

Le site propose des fichiers CSV historiques de résultats de matchs et de cotes de bookmakers pour de nombreuses ligues de football à travers le monde. Les données sont mises à jour après chaque journée de championnat.

## Conditions d'utilisation

- Les données sont gratuites mais **ne sont pas librement redistribuables**.
- Elles ne doivent pas être versionnées directement dans le dépôt Git si leur redistribution est interdite.
- Le site mentionne : *"My data is free, but for those who want a subscription API service, I am now partnering with TheStatsAPI."*
- Le disclaimer du site indique : *"Any information appearing on this website, including references to winning, profit, beating odds/bookmakers etc. should not be considered professional advice or a recommendation to bet or gamble."*
- **Conséquence pour le projet :** les CSV seront conservés localement (dans `data/`), ajoutés à `.gitignore`, et leur obtention sera documentée. Le pipeline doit pouvoir fonctionner avec un échantillon fictif ou un jeu de données de test si nécessaire.

## Compétition retenue

**Ligue 1 française** (Division 1) — identifiée par le code `F1` dans les fichiers CSV.

Justification :
- Cible explicitement mentionnée dans la roadmap du projet.
- Compétition majeure européenne avec des données complètes et historisées.
- Cotes de bookmakers disponibles depuis plusieurs saisons.

## Saisons retenues

Saisons cibles de la roadmap :

| Saison | Fichier | URL | Statut |
|---|---|---|---|
| 2024-2025 | `F1.csv` (2425) | `https://www.football-data.co.uk/mmz4281/2425/F1.csv` | Téléchargé, inspecté |
| 2023-2024 | `F1.csv` (2324) | `https://www.football-data.co.uk/mmz4281/2324/F1.csv` | Disponible |
| 2022-2023 | `F1.csv` (2223) | `https://www.football-data.co.uk/mmz4281/2223/F1.csv` | Disponible |

**Priorité :** commencer par la saison **2024-2025** pour valider le pipeline, puis étendre aux autres saisons si la qualité le permet.

## Marché retenu

**1N2 (1X2) :** victoire à domicile (1), match nul (X), victoire à l'extérieur (2).  
Ce marché est disponible via :
- La colonne `FTR` (Full Time Result) : `H` = victoire domicile, `D` = nul, `A` = victoire extérieur.
- Les cotes des bookmakers : colonnes de type `B365H`, `B365D`, `B365A` (Bet365), `BWH`, `BWD`, `BWA` (Bet&Win), `BFH`, `BFD`, `BFA` (Betfair), `PSH`, `PSD`, `PSA` (Pinnacle), `WHH`, `WHD`, `WHA` (William Hill), `1XBH`, `1XBD`, `1XBA` (1XBet), etc.
- Les cotes maximales et moyennes du marché : `MaxH`, `MaxD`, `MaxA`, `AvgH`, `AvgD`, `AvgA`.
- Les cotes du Betfair Exchange : `BFEH`, `BFED`, `BFEA`.

## Autres données disponibles (hors périmètre initial)

Le CSV contient également :
- Statistiques de match (tirs, corners, fautes, cartons, etc.)
- Cotes Over/Under 2.5 buts
- Cotes Asian Handicap
- Cotes à la clôture (suffixe `C` : `B365CH`, `B365CD`, `B365CA`, etc.)
- Résultats mi-temps (HTHG, HTAG, HTR)

Ces données pourront être exploitées dans des phases ultérieures mais ne font pas partie du périmètre initial du ticket T1.

## Échantillon téléchargé

- **Fichier :** `data/F1_2024-2025.csv`
- **Lignes de données :** 306 matchs
- **Colonnes :** 119
- **Encodage :** UTF-8 avec BOM (Byte Order Mark)
- **Format de date :** `dd/mm/yyyy`
- **Séparateur :** virgule (`,`)

## Références

- Page France : https://www.football-data.co.uk/francem.php
- Dictionnaire des colonnes : https://www.football-data.co.uk/notes.txt
- Disclaimer : https://www.football-data.co.uk/disclaimer.php
