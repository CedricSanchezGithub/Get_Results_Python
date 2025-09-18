from datetime import datetime
import locale
import logging


def format_date(date_string):
    locale.setlocale(locale.LC_TIME, 'fr_FR.utf8')

    date_cleaned = date_string.split(" ", 1)[1].replace(" à ", " ").replace("H", ":")

    format_string = "%d %B %Y %H:%M"

    date_obj = datetime.strptime(date_cleaned, format_string)

    date_iso = date_obj.isoformat()

    print("Date ISO 8601 :", date_iso)
