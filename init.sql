-- Création de la base de données si elle n'existe pas
CREATE DATABASE IF NOT EXISTS get_results;
USE get_results;

-- ========================================================
-- 1. Table MATCHES
-- Correspond au fichier src/saving/db_writer.py
-- ========================================================
DROP TABLE IF EXISTS matches;

CREATE TABLE matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pool_id VARCHAR(50) NOT NULL,        -- Ex: 'SF', '-18F' (correspond à 'category')
    competition VARCHAR(255) NULL,       -- Nom de la compétition
    round VARCHAR(50) NULL,              -- Ex: 'Journée 1' (correspond à 'journee')
    match_date DATETIME NULL,            -- La colonne qui manquait !
    team_1_name VARCHAR(255) NULL,
    team_1_score INT NULL,
    team_2_name VARCHAR(255) NULL,
    team_2_score INT NULL,
    match_link TEXT NULL,                -- URL du match (TEXT pour éviter les limites)

    -- Index pour optimiser les purges (DELETE WHERE pool_id = ...)
    INDEX idx_pool_id (pool_id),
    -- Index pour des recherches temporelles futures
    INDEX idx_match_date (match_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ========================================================
-- 2. Table SCRAPING_LOG
-- Correspond au fichier src/saving/db_logger.py
-- ========================================================
DROP TABLE IF EXISTS scraping_log;

CREATE TABLE scraping_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    started_at DATETIME NOT NULL,
    finished_at DATETIME NULL,
    status VARCHAR(50) NOT NULL,         -- Ex: 'RUNNING', 'SUCCESS', 'FAILURE'
    duration_seconds FLOAT NULL,         -- Durée en secondes
    message TEXT NULL,                   -- Stockage des messages d'erreur

    -- Index pour trier facilement par date
    INDEX idx_started_at (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Utilisation de la base
USE get_results;

-- ========================================================
-- 3. Table SOURCING_URLS (Anciennement "url_équipes")
-- Remplace le fichier src/utils/sources/urls.py
-- ========================================================
DROP TABLE IF EXISTS sourcing_urls;

CREATE TABLE sourcing_urls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,       -- Ex: 'SF', '-18F'
    phase VARCHAR(100) NULL,             -- Ex: 'Championnat', 'Coupe de France'
    url TEXT NOT NULL,                   -- L'URL cible
    active TINYINT(1) DEFAULT 1,         -- 1 = Actif, 0 = Inactif (pour désactiver sans supprimer)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================================
-- MIGRATION DES DONNÉES (Basé sur ton fichier urls.py actuel)
-- ========================================================
INSERT INTO sourcing_urls (category, phase, url) VALUES
('SF', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-f-prenationale-28365/poule-169120/journee-1/'),
('SF', 'Coupe de France', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/coupe-de-france/coupe-de-france-regionale-feminine-2025-26-29113/poule-173664/'),
('-18F', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-f-2e-division-28369/poule-172464/'),
('-15F1', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-f-1ere-division-28372/poule-169159/'),
('-15F2', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-f-2e-division-28373/poule-172423/'),
('-13F1', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-13-feminins-28964/'),
('-13F1', 'Coupe de l\'Hérault', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/coupe-de-l-herault-13-f-29043/'),
('-11F', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-11-feminins-28963/'),
('SG', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-m-preregionale-1ere-division-28343/poule-169284/'),
('-18M2', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-m-3e-division-28350/poule-172487/'),
('-18M1', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-m-2e-division-28349/poule-169141/'),
('-15M1', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-m-2e-division-28355/poule-169153/'),
('-15M2', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-m-3e-division-28356/poule-172527/'),
('-13M1', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-13-masculins-28913/poule-172095/'),
('-13M2', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-13-masculins-28913/poule-175328/'),
('-11M', 'Championnat', 'https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-11-masculins-28912/poule-175315/');