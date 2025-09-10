# Get Results

## Résumé des endpoints & logique métier (concise)

- Services (après `docker compose up`):
  - phpMyAdmin: http://localhost:8080 — interface web pour MySQL.
  - Backend API: http://localhost:8081 — API principale (image `cedsanc/getresultsbackend`). Endpoints de découverte communs: `/`, `/health`, `/docs`, `/openapi.json`.
  - Scheduler Flask: http://localhost:5000 — déclencheur/monitoring du scraping de ce dépôt.
    - GET /            → statut APScheduler
    - GET /health      → {"status":"ok"}
    - GET /scrape      → déclenche immédiatement le scraping en arrière‑plan et répond tout de suite par une page de confirmation.

- Logique métier (vue d’ensemble):
  1) L’endpoint GET /scrape démarre un job en arrière‑plan.
  2) Le job exécute `run_daily_scraping()` qui:
     - ouvre les URLs cibles (src/utils/sources/urls.py) avec Selenium (headless),
     - accepte la bannière cookies si présente, navigue journée par journée,
     - extrait résultats/classements (src/scraping/*), sauvegarde CSV (data/pool_*.csv),
     - écrit en base MySQL (src/saving/db_writer.py) via `src/database/db_connector.py`.
  3) APScheduler planifie aussi ce job quotidiennement (cron 00:00).

- Accès base de données:
  - MySQL: host `localhost`, port `3306`, base `get_results` (ou `${MYSQL_DATABASE}`), user/pass depuis `.env`.
  - Depuis les conteneurs, l’hôte est `mysql_getresults`.

## Installation rapide

```bash
python -m venv venv
source venv/bin/activate   
pip install -r requirements.txt
```

```bash
chmod +x scraping_scheduler.py
```

```bash
./scraping_scheduler.py
```