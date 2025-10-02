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


import csv
import logging
from src.database.db_connector import get_connection


def _to_int_or_none(value):
    """Tente de convertir une valeur en entier, sinon retourne None."""
    if value in (None, "", "-"):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _to_str_or_none(value):
    """Retourne la chaîne de caractères si elle n'est pas vide, sinon None."""
    return value if value else None


def db_writer_results(category):
    """
    Lit les résultats d'un match depuis un fichier CSV et les insère dans la table 'matches'.
    """
    pool_csv = f"data/pool_{category}.csv"
    table_name = "matches"

    # La requête est définie une seule fois pour plus de clarté.
    # Note: La colonne 'round' correspond à 'journee' dans le CSV.
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

    inserted_count = 0
    read_count = 0

    try:
        with connection.cursor() as cursor:
            try:
                with open(pool_csv, mode='r', newline='', encoding='utf-8') as csv_file:
                    reader = csv.DictReader(csv_file)
                    for row in reader:
                        read_count += 1

                        # 1. Préparation des données pour l'insertion.
                        #    Cette étape isole la logique de nettoyage des données.
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

                        # 2. Log des données avant l'insertion (essentiel pour le débogage).
                        #    Utiliser .debug pour éviter de surcharger les logs en production.
                        logging.debug(f"Préparation de l'insertion : {data_tuple}")

                        try:
                            # 3. Exécution de la requête pour la ligne actuelle.
                            cursor.execute(insert_sql, data_tuple)
                            inserted_count += 1
                        except Exception as e:
                            logging.error(f"Échec de l'insertion pour la ligne : {row}", exc_info=True)

            except FileNotFoundError:
                logging.error(f"Le fichier CSV '{pool_csv}' n'a pas été trouvé.")
                return  # Arrête la fonction si le fichier n'existe pas.

        # 4. Valide la transaction si tout s'est bien passé.
        connection.commit()
        logging.info(
            f"Insertion terminée pour la poule '{category}' : "
            f"{inserted_count}/{read_count} lignes insérées dans '{table_name}'."
        )

    except Exception as e:
        # En cas de problème majeur (connexion perdue, etc.), annule la transaction.
        logging.exception(f"Erreur majeure lors de l'écriture dans '{table_name}', annulation de la transaction.")
        if connection:
            connection.rollback()
    finally:
        # Assure que la connexion est toujours fermée.
        if connection:
            connection.close()