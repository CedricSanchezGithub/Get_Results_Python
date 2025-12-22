from datetime import datetime, timezone
import logging
import re
import pytz

PARIS_TZ = pytz.timezone("Europe/Paris")
LOGGER = logging.getLogger(__name__)

MONTHS_MAP = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12
}


def format_date(date_string: str):
    """
    Parse une date française robuste aux espaces insécables et à la casse.
    Format attendu ex: "SAMEDI 27 SEPTEMBRE 2025 À 18H30" ou "27 septembre 2025"
    Retourne un datetime UTC aware.
    """
    if not date_string or "non disponible" in date_string.lower():
        return None

    # 1. Nettoyage basique
    raw = date_string.lower().strip()

    # 2. Regex d'extraction :
    # - (\d{1,2}) : Jour (ex: 27)
    # - \s+ : N'importe quel espace (y compris \xa0 insécable)
    # - ([a-zéû]+) : Mois (ex: septembre)
    # - \s+ : Espace
    # - (\d{4}) : Année (ex: 2025)
    # - (?:.*(\d{1,2})[h:](\d{2}))? : Temps optionnel (ex: 18h30 ou 18:30), on ignore le "à"
    regex = r"(\d{1,2})\s+([a-zéû]+)\s+(\d{4})(?:.*(\d{1,2})[h:](\d{2}))?"

    match = re.search(regex, raw)

    if not match:
        LOGGER.warning(f"format_date: Format non reconnu pour '{date_string}'")
        return None

    day, month_str, year, hour, minute = match.groups()

    # 3. Validation du mois
    month_num = MONTHS_MAP.get(month_str)
    if not month_num:
        LOGGER.error(f"format_date: Mois inconnu '{month_str}' dans '{date_string}'")
        return None

    # 4. Construction de la date (Gestion du temps optionnel)
    try:
        dt_naive = datetime(
            year=int(year),
            month=month_num,
            day=int(day),
            hour=int(hour) if hour else 0,
            minute=int(minute) if minute else 0
        )

        # 5. Localisation Paris -> UTC
        paris_datetime = PARIS_TZ.localize(dt_naive)
        utc_datetime = paris_datetime.astimezone(timezone.utc)

        return utc_datetime

    except Exception as e:
        LOGGER.error(f"format_date: Erreur lors de la construction datetime pour '{date_string}': {e}")
        return None