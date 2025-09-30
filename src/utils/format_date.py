from datetime import datetime
import locale
import logging


def format_date(date_string):
    """
    Tente de formater une date française telle que récupérée depuis le site.
    - Ne modifie pas la logique d'appelant: cette fonction est utilitaire.
    - Retourne une chaîne ISO 8601 si le parsing réussit, sinon None.
    - Ajoute des logs pour faciliter le diagnostic du format source.
    """
    logger = logging.getLogger(__name__)
    if date_string is None:
        logger.warning("format_date: chaîne de date None reçue")
        return None

    logger.debug(f"format_date: brut='{date_string}'")

    # Certaines plateformes n'ont pas fr_FR.utf8 disponible; essayons plusieurs options.
    locale_set = False
    for loc in ("fr_FR.utf8", "fr_FR.UTF-8", "fr_FR", "fr_FR.iso88591"):
        try:
            locale.setlocale(locale.LC_TIME, loc)
            locale_set = True
            break
        except Exception:
            continue
    if not locale_set:
        logger.debug("format_date: impossible de définir la locale FR; tentative de parsing tout de même")

    try:
        # Exemple source: "Le 29 septembre 2025 à 20H30" => on retire le préfixe et remplace les séparateurs
        parts = date_string.split(" ", 1)
        date_cleaned = parts[1] if len(parts) > 1 else date_string
        date_cleaned = date_cleaned.replace(" à ", " ").replace("H", ":")

        fmt = "%d %B %Y %H:%M"
        date_obj = datetime.strptime(date_cleaned, fmt)
        date_iso = date_obj.isoformat()
        logger.info(f"format_date: ISO='{date_iso}' à partir de brut='{date_string}' (fmt='{fmt}')")
        return date_iso
    except Exception as e:
        logger.warning(f"format_date: échec du parsing pour brut='{date_string}': {e}")
        return None
