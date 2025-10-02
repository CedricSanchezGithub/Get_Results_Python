from datetime import datetime, timezone
import locale
import logging

import pytz

PARIS_TZ = pytz.timezone("Europe/Paris")

def format_date(date_string: str):
    """
    Tente de convertir une chaîne de caractères en objet datetime.
    - Gère les préfixes comme "Le" ou les jours de la semaine.
    - Retourne un objet datetime si le parsing réussit.
    - Retourne None si la chaîne est invalide ou "Date non disponible".
    """
    logger = logging.getLogger(__name__)
    if not date_string or date_string == "Date non disponible":
        logger.debug(f"format_date: chaîne de date non fournie ou non disponible: '{date_string}'")
        return None

    logger.debug(f"format_date: brut='{date_string}'")

    try:
        parts = date_string.split()
        if parts[0].lower() in ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche", "le"]:
            parts = parts[1:]
        date_cleaned = " ".join(parts).replace(" à ", " ").replace("H", ":")
        fmt = "%d %B %Y %H:%M"

        # 1. On obtient un datetime naïf
        naive_datetime = datetime.strptime(date_cleaned, fmt)

        # 2. On le rend conscient en le localisant à Paris
        # pytz gère l'heure d'été/hiver tout seul !
        paris_datetime = PARIS_TZ.localize(naive_datetime)

        # 3. On le convertit en UTC pour le stockage
        utc_datetime = paris_datetime.astimezone(timezone.utc)

        logger.info(f"format_date: parsing réussi pour '{date_string}' -> {utc_datetime}")
        return utc_datetime

    except (ValueError, IndexError) as e:
        logger.warning(f"format_date: échec du parsing pour la chaîne nettoyée '{date_cleaned}': {e}")
        return None