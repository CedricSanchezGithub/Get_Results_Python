from datetime import datetime
import locale
import logging


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

    # Essayer de définir la locale française
    try:
        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    except locale.Error:
        logger.warning("format_date: impossible de définir la locale fr_FR.UTF-8. Le parsing peut échouer.")

    try:
        parts = date_string.split()

        # Ignorer le premier mot si c'est un jour de la semaine ou "Le"
        if parts[0].lower() in ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche", "le"]:
            parts = parts[1:]

        # Reconstruire la chaîne et nettoyer
        date_cleaned = " ".join(parts)
        date_cleaned = date_cleaned.replace(" à ", " ").replace("H", ":")

        fmt = "%d %B %Y %H:%M"
        date_obj = datetime.strptime(date_cleaned, fmt)

        logger.info(f"format_date: parsing réussi pour '{date_string}' -> {date_obj}")
        return date_obj

    except (ValueError, IndexError) as e:
        logger.warning(f"format_date: échec du parsing pour la chaîne nettoyée '{date_cleaned}': {e}")
        return None