import logging
from src.database.db_connector import get_connection


def _to_int_or_none(value):
    if value in (None, "", "-"):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _to_str_or_none(value):
    return value if value else None


def db_writer_results(match_data_list: list, category: str):
    if not match_data_list:
        logging.getLogger(__name__).info(f"Aucune donnée à insérer pour la catégorie '{category}'.")
        return

    table_name = "matches"

    # Si le match existe (Date + Team1 + Team2 identiques), on met à jour les scores et infos
    insert_sql = f"""
        INSERT INTO {table_name} 
            (pool_id, match_date, team_1_name, team_1_score, team_2_name, team_2_score, 
             match_link, competition, round)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            team_1_score = VALUES(team_1_score),
            team_2_score = VALUES(team_2_score),
            match_link = VALUES(match_link),
            round = VALUES(round),
            pool_id = VALUES(pool_id)
    """

    connection = get_connection()
    if not connection:
        logging.error("Impossible d'obtenir une connexion à la base de données.")
        return

    data_to_insert = []
    for row in match_data_list:
        try:

            data_tuple = (
                category,
                _to_str_or_none(row.get('match_date')),
                _to_str_or_none(row.get('team_1_name')),
                _to_int_or_none(row.get('team_1_score')),
                _to_str_or_none(row.get('team_2_name')),
                _to_int_or_none(row.get('team_2_score')),
                _to_str_or_none(row.get('match_link')),
                _to_str_or_none(row.get('competition')),
                _to_str_or_none(row.get('journee'))
            )
            data_to_insert.append(data_tuple)
        except Exception as e:
            logging.error(f"Échec de la préparation des données pour la ligne : {row}", exc_info=True)
            continue

    if not data_to_insert:
        logging.getLogger(__name__).warning(f"Aucune donnée valide à insérer après préparation pour '{category}'.")
        connection.close()
        return

    inserted_count = 0

    try:
        with connection.cursor() as cursor:
            affected_rows = cursor.executemany(insert_sql, data_to_insert)
            inserted_count = affected_rows if affected_rows is not None else 0

        connection.commit()
        logging.info(
            f"Traitement terminé pour la poule '{category}' : "
            f"{inserted_count} opérations (Insertions ou Mises à jour) sur {len(data_to_insert)} items."
        )

    except Exception as e:
        logging.exception(f"Erreur majeure lors de l'écriture transactionnelle dans '{table_name}', annulation.")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()