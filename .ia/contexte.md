# AI CONTEXT & ARCHITECTURE BEACON (SCRAPER)

## 1. PROJECT IDENTITY
- **Name:** Get Results Scraper
- **Role:** ETL Engine (Extract, Transform, Load).
- **Mission:** Scraper les données sportives (résultats, classements, calendriers) et les insérer directement en base de données.

## 2. TECHNICAL STACK (STRICT)
- **Language:** Python 3.x.
- **Core Libs:** `requests` (HTTP), `beautifulsoup4` (Parsing HTML), `mysql-connector-python` (Database).
- **Scheduling:** Script `scraping_scheduler.py` (Boucle infinie avec `schedule` ou simple sleep).
- **Database Interaction:** Écriture directe via SQL brut (pas d'ORM type SQLAlchemy).

## 3. ARCHITECTURE & PATTERNS
- **Pattern:** "Shared Database Integration". Le Scraper ne parle PAS au Backend, il parle à la même DB (MySQL/MariaDB).
- **Flow:**
  1. `scraping_scheduler.py` déclenche les jobs.
  2. `api_fetcher.py` / `get_*.py` récupèrent le HTML/JSON.
  3. `db_writer.py` nettoie et insère/met à jour les données (Upsert logic).
- **Error Handling:** Logs stockés en base via `db_logger.py` (Table `scraping_logs`).

## 4. CRITICAL FILES
- `src/database/db_connector.py`: Gestion de la connexion MySQL (Single Point of Failure).
- `src/saving/db_writer.py`: Contient les requêtes SQL d'insertion. C'est ici que le schéma doit s'aligner avec le Backend Kotlin.
- `schema.sql`: Définition de la structure de la base (Doit être sync avec le Backend).
- `run_daily_scraping.py`: Script d'exécution manuelle/journalière.

## 5. ENVIRONMENT VARIABLES
- `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`: Essentiels pour la connexion.
- `ENV`: `production` vs `dev`.