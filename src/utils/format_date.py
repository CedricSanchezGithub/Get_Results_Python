from datetime import datetime
import locale
import logging

from datetime import datetime
import locale
import logging

from datetime import datetime
import locale
import logging


def format_date(date_string: str):
    """
    Tente de convertir une chaîne de caractères en objet datetime.
    - Retourne un objet datetime si le parsing réussit.
    - Retourne None si la chaîne est invalide ou "Date non disponible".
    """
    logger = logging.getLogger(__name__)
    if not date_string or date_string == "Date non disponible":
        logger.debug(f"format_date: chaîne de date non fournie ou non disponible: '{date_string}'")
        return None

    logger.debug(f"format_date: brut='{date_string}'")

    # Logique pour définir la locale française (essentiel pour %B)
    locale_set = False
    for loc in ("fr_FR.utf8", "fr_FR.UTF-8", "fr_FR"):
        try:
            locale.setlocale(locale.LC_TIME, loc)
            locale_set = True
            break
        except locale.Error:
            continue
    if not locale_set:
        logger.warning("format_date: impossible de définir la locale FR. Le parsing des mois peut échouer.")

    try:
        # Nettoyage et parsing
        # Exemple: "Le 29 septembre 2025 à 20H30"
        date_cleaned = date_string.lower().replace("le ", "").replace(" à ", " ").replace("h", ":")

        # Format attendu : "29 septembre 2025 20:30"
        fmt = "%d %B %Y %H:%M"

        date_obj = datetime.strptime(date_cleaned, fmt)
        logger.info(f"format_date: parsing réussi pour '{date_string}' -> {date_obj}")
        return date_obj
    except (ValueError, IndexError) as e:
        logger.warning(f"format_date: échec du parsing pour brut='{date_string}': {e}")
        return None