import csv
import logging

from src.utils.purge.tables_drop.db_drop_option import connection


def db_writer_ranking(category):
    """Insère les données de classement dans la base de données MySQL."""
    csv_file = "data/ranking.csv"
    table_name = f"pool_{category}"
    sql = f"""
    INSERT INTO {table_name} (position, club_name, points)
    VALUES (%s, %s, %s)
    """

    try:
        with connection.cursor() as cursor:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    cursor.execute(sql, (row['position'], row['club_name'], row['points']))

            connection.commit()
            print(f"Données insérées avec succès depuis {csv_file}")

    except Exception as e:
        print(f"Erreur lors de l'insertion dans 'ranking' : {e}")




def db_writer_results(category):
    """Insère les données des résultats de match dans la table 'pool' de la base de données MySQL."""

    pool_csv = f"data/pool_{category}.csv"
    table_name = f"`pool_{category}`"
    error_log_file = f"errors_{category}.log"

    # Requête SQL simplifiée
    insert_sql = f"""
    INSERT INTO {table_name} (date_string, team_1_name, team_1_score, team_2_name, team_2_score, match_link, competition, day)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        with connection.cursor() as cursor:

            with open(pool_csv, newline='', encoding='utf-8') as results_file:
                reader = csv.DictReader(results_file)

                for row in reader:
                    try:
                        # Préparation des champs avec conversions sûres
                        def to_int_or_none(v):
                            try:
                                return int(v) if v not in (None, "", "-") else None
                            except Exception:
                                return None
                        def to_str_or_none(v):
                            return v if v not in (None, "") else None

                        date_ms = to_int_or_none(row.get('date_string'))
                        team_1_score = to_int_or_none(row.get('team_1_score'))
                        team_2_score = to_int_or_none(row.get('team_2_score'))

                        cursor.execute(insert_sql, (
                            date_ms,
                            to_str_or_none(row.get('team_1_name')),
                            team_1_score,
                            to_str_or_none(row.get('team_2_name')),
                            team_2_score,
                            to_str_or_none(row.get('match_link')),
                            to_str_or_none(row.get('competition')),
                            to_str_or_none(row.get('journee'))
                        ))
                    except Exception as e:
                        error_message = f"Erreur lors de l'insertion pour la ligne {row}: {e}"
                        print(error_message)
                        logging.error(error_message)

            connection.commit()
            print(f"Données insérées avec succès depuis {pool_csv}")

    except Exception as e:
        error_message = f"Erreur lors de l'insertion dans 'results': {e}"
        logging.error(error_message)
        print(error_message)
