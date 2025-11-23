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
    # Si on a trouvé la métadonnée des journées, on génère les autres URLs
    if journees_meta:
        logger.info(f"  -> {len(journees_meta)} journées détectées dans la structure.")

        # On détecte le pattern de l'URL actuelle pour le remplacer
        # Ex: .../poule-1234/journee-1/  -> on veut remplacer "journee-1" par "journee-X"
        base_url_pattern = re.sub(r"journee-\d+/?", "journee-{}/", url_start)

        # Si l'URL n'avait pas de /journee-N/, on l'ajoute à la fin
        if base_url_pattern == url_start:
            if not base_url_pattern.endswith("/"): base_url_pattern += "/"
            base_url_pattern += "journee-{}/"

        # On boucle sur toutes les journées trouvées
        for journee in journees_meta:
            num = journee.get("journee_numero")

            # On évite de re-scraper la journée 1 si on vient de la faire
            if str(num) in url_start:
                continue

            target_url = base_url_pattern.format(num)

            # Petit log pour suivre
            # logger.debug(f"Scraping journée {num}...")

            page_matches, _ = get_matches_from_url(target_url, category)
            if page_matches:
                all_match_data.extend(page_matches)
    else:
        logger.warning(
            "⚠️ Impossible de détecter les autres journées automatiquement. Seule l'URL fournie a été traitée.")

    # 3. Sauvegarde Atomique
    logger.info(f"🏁 Fin du scraping pour '{category}'. Total: {len(all_match_data)} matchs. Écriture BDD...")
    db_writer_results(all_match_data, category)