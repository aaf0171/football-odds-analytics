-- =============================================================================
-- Football Odds Analytics — Schéma MariaDB
-- =============================================================================

SET NAMES utf8mb4;
SET time_zone = "+00:00";

-- ---------------------------------------------------------------------------
-- 1. équipes
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `teams` (
    `id`          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `source_team_name` VARCHAR(100) NOT NULL COMMENT 'Nom exact tel qu''il apparaît dans le CSV',
    `name`        VARCHAR(100) NOT NULL COMMENT 'Nom normalisé (optionnel)',
    UNIQUE KEY `uq_source_team_name` (`source_team_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Référentiel des équipes de football';

-- ---------------------------------------------------------------------------
-- 2. matchs
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `matches` (
    `id`              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `source_match_key` VARCHAR(255) NOT NULL COMMENT 'Clé unique source : Div+Date+HomeTeam+AwayTeam',
    `competition`     VARCHAR(10) NOT NULL COMMENT 'Code compétition (ex. F1)',
    `season`          VARCHAR(10) NOT NULL COMMENT 'Saison (ex. 2024-2025)',
    `match_date`      DATE NOT NULL,
    `home_team_id`    INT UNSIGNED NOT NULL,
    `away_team_id`    INT UNSIGNED NOT NULL,
    `home_goals`      INT DEFAULT NULL,
    `away_goals`      INT DEFAULT NULL,
    `home_goals_ht`   INT DEFAULT NULL COMMENT 'Buts mi-temps domicile',
    `away_goals_ht`   INT DEFAULT NULL COMMENT 'Buts mi-temps extérieur',
    `created_at`      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at`      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_source_match_key` (`source_match_key`),
    KEY `idx_season` (`season`),
    KEY `idx_match_date` (`match_date`),
    KEY `idx_home_team` (`home_team_id`),
    KEY `idx_away_team` (`away_team_id`),
    CONSTRAINT `fk_matches_home_team` FOREIGN KEY (`home_team_id`)
        REFERENCES `teams`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_matches_away_team` FOREIGN KEY (`away_team_id`)
        REFERENCES `teams`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `chk_goals_non_negative` CHECK (`home_goals` IS NULL OR `home_goals` >= 0),
    CONSTRAINT `chk_goals_ht_non_negative` CHECK (`home_goals_ht` IS NULL OR `home_goals_ht` >= 0),
    CONSTRAINT `chk_home_away_different` CHECK (`home_team_id` <> `away_team_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Un enregistrement par match';

-- ---------------------------------------------------------------------------
-- 3. cotes de match (match_odds)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `match_odds` (
    `id`              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `match_id`        INT UNSIGNED NOT NULL,
    `bookmaker`       VARCHAR(50) NOT NULL COMMENT 'Nom du bookmaker (ex. bet365, pinnacle)',
    `odds_type`       ENUM('opening', 'closing') NOT NULL COMMENT 'Type de cote',
    `home_odds`       DECIMAL(10,4) DEFAULT NULL,
    `draw_odds`       DECIMAL(10,4) DEFAULT NULL,
    `away_odds`       DECIMAL(10,4) DEFAULT NULL,
    `created_at`      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_match_bookmaker_type` (`match_id`, `bookmaker`, `odds_type`),
    KEY `idx_bookmaker` (`bookmaker`),
    KEY `idx_odds_type` (`odds_type`),
    CONSTRAINT `fk_match_odds_match` FOREIGN KEY (`match_id`)
        REFERENCES `matches`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `chk_odds_positive` CHECK (
        `home_odds` IS NULL OR `home_odds` > 0
    ),
    CONSTRAINT `chk_draw_odds_positive` CHECK (
        `draw_odds` IS NULL OR `draw_odds` > 0
    ),
    CONSTRAINT `chk_away_odds_positive` CHECK (
        `away_odds` IS NULL OR `away_odds` > 0
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Cotes 1N2 par bookmaker et type (ouverture/clôture)';

-- ---------------------------------------------------------------------------
-- 4. exécutions ETL
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `etl_runs` (
    `id`              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `started_at`      DATETIME NOT NULL,
    `finished_at`     DATETIME DEFAULT NULL,
    `status`          ENUM('running', 'success', 'failed') NOT NULL DEFAULT 'running',
    `source`          VARCHAR(100) NOT NULL COMMENT 'Source des données (ex. football-data.co.uk)',
    `season`          VARCHAR(10) NOT NULL COMMENT 'Saison traitée',
    `lines_read`      INT DEFAULT 0 COMMENT 'Lignes lues dans le CSV',
    `lines_loaded`    INT DEFAULT 0 COMMENT 'Lignes chargées en base',
    `lines_rejected`  INT DEFAULT 0 COMMENT 'Lignes rejetées',
    `error_message`   TEXT DEFAULT NULL COMMENT 'Message d''erreur le cas échéant',
    `created_at`      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Historique des exécutions ETL';
