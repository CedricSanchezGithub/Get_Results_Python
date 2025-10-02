from datetime import datetime, timezone
import logging
import pytz

PARIS_TZ = pytz.timezone("Europe/Paris")

# Dictionnaire de traduction pour les mois
FRENCH_MONTHS = {
    "janvier": "January", "février": "February", "mars": "March", "avril": "April",
    "mai": "May", "juin": "June", "juillet": "July", "août": "August",
    "septembre": "September", "octobre": "October", "novembre": "November", "décembre": "December"
}


def format_date(date_string: str):
    """
    Tente de convertir une chaîne de caractères en objet datetime conscient
    du fuseau horaire et normalisé en UTC, en gérant explicitement les mois en français.
    """
    logger = logging.getLogger(__name__)
    if not date_string or date_string == "Date non disponible":
        return None

    try:
        parts = date_string.lower().split()  # Mettre en minuscule pour la traduction
        if parts[0] in ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche", "le"]:
            parts = parts[1:]

        # Traduire le nom du mois
        month_fr = parts[1]
        if month_fr in FRENCH_MONTHS:
            parts[1] = FRENCH_MONTHS[month_fr]
        else:
            # Si le mois n'est pas dans notre dictionnaire, on logue une erreur et on arrête
            raise ValueError(f"Mois inconnu: {month_fr}")

        date_cleaned = " ".join(parts).replace(" à ", " ").replace("h", ":")  # 'H' peut être en minuscule

        # Le format attend maintenant un mois en anglais
        fmt = "%d %B %Y %H:%M"

        # Le reste de la logique est identique
        naive_datetime = datetime.strptime(date_cleaned, fmt)
        paris_datetime = PARIS_TZ.localize(naive_datetime)
        utc_datetime = paris_datetime.astimezone(timezone.utc)

        logger.info(f"format_date: parsing réussi pour '{date_string}' -> {utc_datetime}")
        return utc_datetime

    except (ValueError, IndexError) as e:
        logger.warning(f"format_date: échec du parsing pour la chaîne '{date_string}': {e}")
        return None