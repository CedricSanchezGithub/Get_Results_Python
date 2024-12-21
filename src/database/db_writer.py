import csv

from src.database.db_drop_option import connection


def db_writer_ranking():
    """Insère les données de classement dans la base de données MySQL."""
    csv_file = "../../data/ranking.csv"

    sql = """
    INSERT INTO ranking (position, club_name, points)
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

    finally:
        connection.close()



def db_writer_results():
    """Insère les données des résultats de match dans la table 'results' de la base de données MySQL."""
    csv_file = "data/results.csv"

    truncate_sql = "TRUNCATE TABLE results;"
    sql = """
    INSERT INTO results (date, team_a, team_b, score_a, score_b, competition)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    try:
        with connection.cursor() as cursor:
            # Vider la table avant d'insérer de nouvelles données
            cursor.execute(truncate_sql)
            print("Table 'results' vidée avec succès.")

            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Insertion directe de la date en tant que string
                    cursor.execute(sql, (
                        row['date_time'],         # Directement inséré sans conversion
                        row['team_1_name'],       # Correspond à 'team_a'
                        row['team_2_name'],       # Correspond à 'team_b'
                        int(row['team_1_score']), # Correspond à 'score_a'
                        int(row['team_2_score']), # Correspond à 'score_b'
                        None                      # Placeholder pour 'competition' si non défini
                    ))

            # Valider les changements
            connection.commit()
            print(f"Données insérées avec succès depuis {csv_file}")

    except Exception as e:
        print(f"Erreur lors de l'insertion dans 'results' : {e}")

    finally:
        connection.close()
