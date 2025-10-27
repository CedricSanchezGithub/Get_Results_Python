import csv
import logging
from src.database.db_connector import get_connection


def db_writer_ranking(category):
    csv_file = "data/ranking.csv"
    table_name = f"pool_{category}"
    sql = f"""
    INSERT INTO {table_name} (position, club_name, points)
    VALUES (%s, %s, %s)
    """

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    cursor.execute(sql, (row['position'], row['club_name'], row['points']))

            conn.commit()
            logging.info(f"Classement inséré avec succès depuis {csv_file} dans {table_name}")

    except Exception as e:
        logging.error(f"Erreur lors de l'insertion du ranking dans '{table_name}' : {e}")
    finally:
        conn.close()


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
    insert_sql = f"""
        INSERT INTO {table_name} 
            (pool_id, match_date, team_1_name, team_1_score, team_2_name, team_2_score, 
             match_link, competition, round)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            f"Insertion transactionnelle terminée pour la poule '{category}' : "
            f"{inserted_count}/{len(data_to_insert)} lignes insérées dans '{table_name}'."
        )

    except Exception as e:
        logging.exception(f"Erreur majeure lors de l'écriture transactionnelle dans '{table_name}', annulation.")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()