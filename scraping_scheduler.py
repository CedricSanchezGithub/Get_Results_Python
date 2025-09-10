#!/usr/bin/env python3

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import logging

from run_daily_scraping import run_daily_scraping

# Application Flask (optionnelle si vous voulez un endpoint HTTP)
app = Flask(__name__)

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

def scraping_job():
    """Job appelé par APScheduler : lance le script de scraping."""
    run_daily_scraping()

@app.route('/')
def index():
    return "APScheduler est en cours d'exécution. Accès racine de l'application Flask."

@app.route('/scrape', methods=['GET'])
def trigger_scrape():
    """Endpoint pour déclencher le scraping manuellement et afficher une page de confirmation immédiatement, puis lancer le job en arrière-plan."""
    from datetime import datetime
    from threading import Thread

    launched_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Démarrer le scraping en arrière-plan pour répondre tout de suite à l'utilisateur
    Thread(target=scraping_job, daemon=True).start()

    html = f"""
    <!doctype html>
    <html lang=\"fr\">
    <head>
      <meta charset=\"utf-8\">
      <title>Scraping déclenché</title>
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 2rem; color: #222; }}
        .card {{ max-width: 640px; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.25rem; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
        h1 {{ font-size: 1.25rem; margin: 0 0 0.5rem; }}
        .ok {{ color: #16a34a; font-weight: 600; }}
        .meta {{ color: #6b7280; font-size: 0.95rem; margin-top: 0.25rem; }}
        .links {{ margin-top: 1rem; }}
        a {{ color: #2563eb; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
      </style>
    </head>
    <body>
      <div class=\"card\">
        <h1 class=\"ok\">✅ Le scraping a bien été déclenché</h1>
        <div class=\"meta\">Horodatage: {launched_at}</div>
        <p>Le processus s'exécute en arrière-plan. Vous pouvez consulter l'état de l'application via les liens ci-dessous.</p>
        <div class=\"links\">
          <ul>
            <li><a href=\"/\">Accueil</a></li>
            <li><a href=\"/health\">Vérifier l'état (health)</a></li>
          </ul>
        </div>
      </div>
    </body>
    </html>
    """
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé simple pour vérifier que l'appli répond."""
    return {"status": "ok"}, 200

if __name__ == '__main__':
    # Configuration d'APScheduler
    scheduler = BackgroundScheduler()
    # Planifie l'exécution de 'scraping_job' tous les jours à 00:00
    scheduler.add_job(scraping_job, 'cron', hour=0, minute=0, id='daily_scraping')
    scheduler.start()

    # Arrêt propre du scheduler quand l'appli s'arrête
    atexit.register(lambda: scheduler.shutdown())

    # Lancement de l'appli Flask (sur port 5000 par défaut)
    app.run(host='0.0.0.0', port=5000, debug=True)
