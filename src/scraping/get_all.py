import logging
import re
from src.saving.db_writer import db_writer_results
from src.scraping.get_match_results import get_matches_from_url


def get_all(url_start, category):
    """
    Logique principale : Scrape toutes les journées d'une poule donnée.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Démarrage scraping '{category}' via Requests")

    all_match_data = []

    # 1. Scraping de la page initiale (donnée en config)
    logger.info(f"Traitement URL initiale : {url_start}")
    matches, journees_meta = get_matches_from_url(url_start, category)

    if matches:
        all_match_data.extend(matches)
        logger.info(f"  -> {len(matches)} matchs trouvés sur la page initiale.")

    # 2. Gestion de la pagination intelligente
    if journees_meta:
        logger.info(f"  -> {len(journees_meta)} journées détectées dans la structure.")
        if len(journees_meta) > 0:
            first_j = journees_meta[0]
            logger.info(f"  🔍 [DEBUG STRUCT] Keys disponibles dans journees_meta[0]: {list(first_j.keys())}")

        base_url_pattern = re.sub(r"journee-\d+/?", "journee-{}/", url_start)

        if base_url_pattern == url_start:
            if not base_url_pattern.endswith("/"): base_url_pattern += "/"
            base_url_pattern += "journee-{}/"

        count_paginated = 0
        for journee in journees_meta:
            num = journee.get("journeeNumero") or journee.get("journee_numero") or journee.get("numero")

            if not num:
                logger.warning(f"  ⚠️ Impossible de trouver le numéro de journée dans : {journee}. Skip.")
                continue

            if f"journee-{num}" in url_start or f"journee-{num}/" in url_start:
                continue

            target_url = base_url_pattern.format(num)

            page_matches, _ = get_matches_from_url(target_url, category)
            if page_matches:
                all_match_data.extend(page_matches)
                count_paginated += len(page_matches)

        logger.info(f"  -> {count_paginated} matchs supplémentaires récupérés via pagination.")

    else:
        logger.warning(
            "⚠️ Impossible de détecter les autres journées automatiquement. Seule l'URL fournie a été traitée.")

    # 3. Sauvegarde Atomique
    logger.info(f"🏁 Fin du scraping pour '{category}'. Total: {len(all_match_data)} matchs. Écriture BDD...")
    db_writer_results(all_match_data, category)