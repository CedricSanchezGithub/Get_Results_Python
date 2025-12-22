from datetime import datetime, timezone
import logging
import re
import pytz
from dateutil import parser

PARIS_TZ = pytz.timezone("Europe/Paris")
LOGGER = logging.getLogger(__name__)

MONTHS_MAP = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12
}

def format_date(date_string: str):
    """
    Parse une date robuste : supporte ISO 8601 et format texte français (avec espaces insécables).
    Retourne un datetime UTC aware.
    """
    if not date_string or "non disponible" in str(date_string).lower():
        return None

    # 1. Tentative ISO directe (Le cas standard du JSON FFHandball)
    try:
        dt = parser.parse(date_string)
        if dt.tzinfo is None:
            dt = PARIS_TZ.localize(dt)
        return dt.astimezone(timezone.utc)
    except (ValueError, TypeError):
        pass

    # 2. Parsing Manuel Français (Regex pour ignorer les espaces insécables \xa0)
    raw = date_string.lower().strip()

    regex = r"(\d{1,2})\s+([a-zéû]+)\s+(\d{4})(?:.*(\d{1,2})[h:](\d{2}))?"
    match = re.search(regex, raw)

    if not match:
        LOGGER.warning(f"format_date: Format irrécupérable pour '{date_string}'")
        return None

    day, month_str, year, hour, minute = match.groups()

    month_num = MONTHS_MAP.get(month_str)
    if not month_num:
        LOGGER.warning(f"format_date: Mois inconnu '{month_str}'")
        return None

    try:
        dt_naive = datetime(
            year=int(year), month=month_num, day=int(day),
            hour=int(hour) if hour else 0,
            minute=int(minute) if minute else 0
        )
        return PARIS_TZ.localize(dt_naive).astimezone(timezone.utc)
    except Exception as e:
        LOGGER.error(f"format_date: Erreur construction '{date_string}': {e}")
        return None