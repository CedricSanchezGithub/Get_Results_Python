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

## Construire et pousser l'image Docker du scraper

Nom de l'image: cedsanc/getresultscraper

Prérequis:
- Avoir un compte Docker Hub et être connecté via la CLI: `docker login`
- Être à la racine du projet (là où se trouve le Dockerfile).

Commandes de base:
- Build (tag latest):
  docker build -t cedsanc/getresultscraper:latest .
- (Optionnel) Ajoutez un tag versionné:
  export VERSION=1.0.0
  docker tag cedsanc/getresultscraper:latest cedsanc/getresultscraper:${VERSION}
- Push vers Docker Hub:
  docker push cedsanc/getresultscraper:latest
  # et si vous avez créé un tag versionné:
  docker push cedsanc/getresultscraper:${VERSION}

Vérifier localement:
- Démarrer uniquement le service scraper en utilisant l'image locale:
  docker run --rm -p 5000:5000 --env-file .env --network host cedsanc/getresultscraper:latest
  # ou via docker compose (le service "scraper" utilise déjà cedsanc/getresultscraper):
  docker compose up -d scraper

Notes:
- Le Dockerfile installe Chromium et chromedriver et expose le port 5000. La commande par défaut lance `scraping_scheduler.py`.
- Si vous devez construire pour plusieurs architectures (ex: AMD64 et ARM64/Raspberry Pi), utilisez Buildx:
  docker buildx create --use --name multi
  docker buildx build --platform linux/amd64,linux/arm64 -t cedsanc/getresultscraper:latest --push .
  # Remplacez/ajoutez les tags nécessaires.
- Après le push, vos environnements distants peuvent récupérer la dernière image avec:
  docker compose pull scraper && docker compose up -d scraper
