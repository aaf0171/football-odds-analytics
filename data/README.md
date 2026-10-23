# Données brutes

## Avertissement

Les données proviennent de [Football-Data.co.uk](https://www.football-data.co.uk/) et **ne sont pas librement redistribuables**.
Ce dossier ne doit pas être versionné dans le dépôt Git.

## Comment obtenir les données

1. Se rendre sur https://www.football-data.co.uk/francem.php
2. Télécharger les fichiers CSV correspondant aux saisons souhaitées :
   - Ligue 1 (Division 1) : `F1.csv`
3. Placer les fichiers dans ce dossier avec le nommage suivant :
   ```
   data/F1_2024-2025.csv
   data/F1_2023-2024.csv
   data/F1_2022-2023.csv
   ```

## Inspection des données

Un script Python standard library est fourni pour inspecter un CSV :

```bash
python3 data/F1_2024-2025_inspection.py
python3 data/F1_2024-2025_inspection.py data/F1_2023-2024.csv
```

## Fichiers

| Fichier | Description |
|---|---|
| `F1_2024-2025.csv` | 306 matchs, 119 colonnes, UTF-8 avec BOM |
| `F1_2024-2025_inspection.py` | Script d'inspection standard library |
| `README.md` | Ce fichier |

## Licence

Données gratuites à usage personnel / analyse quantitative.
Voir https://www.football-data.co.uk/disclaimer.php
