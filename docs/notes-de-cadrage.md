# Note de cadrage — Ticket T1

## Récapitulatif des décisions

| Décision | Valeur retenue |
|---|---|
| Source de données | Football-Data.co.uk |
| Compétition | Ligue 1 française (code `F1`) |
| Saisons | 2024-2025 (priorité), 2023-2024, 2022-2023 |
| Marché | 1N2 (victoire domicile, nul, victoire extérieur) |
| Bookmakers cibles | Bet365, Betfair Exchange, Pinnacle, Bet&Win, William Hill, 1XBet |
| Cotes d'intérêt | Ouverture (H/D/A), moyennes/max du marché, Betfair Exchange, clôture |
| Questions analytiques | Voir `docs/methodology.md` |
| Conditions d'utilisation | Usage personnel/analyse uniquement, pas de redistribution |

## Critères d'acceptation T1

- [x] Source et conditions d'utilisation documentées (`docs/data-source.md`)
- [x] Colonnes nécessaires identifiées et confrontées au dictionnaire officiel (`docs/data-dictionary.md`)
- [x] Limites et valeurs manquantes connues
- [x] CSV de la saison 2024-2025 téléchargé et inspecté (`data/F1_2024-2025.csv`, 306 matchs, 119 colonnes)
- [x] Questions analytiques définies (`docs/methodology.md`)

## Prochaines étapes (T2 — Étudier le CSV source)

- Inventorier les colonnes, types, formats de date et valeurs manquantes pour chaque saison.
- Identifier les variations de schéma entre saisons (noms de bookmakers, colonnes absentes).
- Confronter les en-têtes réels du CSV avec le dictionnaire officiel `notes.txt`.
- Documenter les anomalies connues dans `docs/data-dictionary.md`.
