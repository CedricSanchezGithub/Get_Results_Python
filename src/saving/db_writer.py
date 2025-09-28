import csv
import logging
from src.database.db_connector import get_connection


def db_writer_ranking(category):
    """Insère les données de classement dans la base de données MySQL."""
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




def db_writer_results(category):
    """Insère les données des résultats de match dans la table unique 'matches'."""

    pool_csv = f"data/pool_{category}.csv"
    table_name = "matches"
    error_log_file = f"errors_{category}.log"

    insert_sql = f"""
    INSERT INTO {table_name} (pool_id, match_date, team_1_name, team_1_score, team_2_name, team_2_score, match_link, competition, round)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    conn = get_connection()
    try:
        inserted = 0
        read_rows = 0
        with conn.cursor() as cursor:
            with open(pool_csv, newline='', encoding='utf-8') as results_file:
                reader = csv.DictReader(results_file)
                for row in reader:
                    read_rows += 1
                    try:
                        def to_int_or_none(v):
                            try:
                                return int(v) if v not in (None, "", "-") else None
                            except Exception:
                                return None
                        def to_str_or_none(v):
                            return v if v not in (None, "") else None

                        date_ms = to_int_or_none(row.get('match_date'))
                        team_1_score = to_int_or_none(row.get('team_1_score'))
                        team_2_score = to_int_or_none(row.get('team_2_score'))

                        cursor.execute(insert_sql, (
                            category,
                            date_ms,
                            to_str_or_none(row.get('team_1_name')),
                            team_1_score,
                            to_str_or_none(row.get('team_2_name')),
                            team_2_score,
                            to_str_or_none(row.get('match_link')),
                            to_str_or_none(row.get('competition')),
                            to_str_or_none(row.get('journee'))
                        ))
                        inserted += 1
                    except Exception as e:
                        logging.error(
                            f"Erreur lors de l'insertion d'un match",
                            extra={
                                'category': category,
                                'competition': row.get('competition'),
                                'journee': row.get('journee'),
                                'row': row,
                                'error': str(e),
                            }
                        )

            conn.commit()
            logging.info(f"Insertion terminée pour la poule '{category}' dans '{table_name}': {inserted}/{read_rows} lignes insérées")

    except Exception as e:
        logging.exception(f"Erreur lors de l'écriture dans '{table_name}': {e}")
    finally:
        conn.close()