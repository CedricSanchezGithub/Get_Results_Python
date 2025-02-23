from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import logging

from main import run_daily_scraping

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
    """Endpoint pour déclencher le scraping manuellement."""
    scraping_job()
    return "Scraping déclenché manuellement."

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
