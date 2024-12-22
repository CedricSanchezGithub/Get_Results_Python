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
    results_csv = "data/results.csv"
    day_and_competition_csv = "data/day_and_competition.csv"

    insert_sql = """
    INSERT INTO results (date, team_a, team_b, score_a, score_b, competition, day)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    try:
        with connection.cursor() as cursor:

            # Lire les données du fichier day_and_competition.csv
            with open(day_and_competition_csv, newline='', encoding='utf-8') as day_comp_file:
                day_comp_reader = csv.DictReader(day_comp_file)
                day_comp_data = list(day_comp_reader)  # Charger toutes les lignes en mémoire

            # Lire et insérer les données du fichier results.csv
            with open(results_csv, newline='', encoding='utf-8') as results_file:
                results_reader = csv.DictReader(results_file)

                for idx, row in enumerate(results_reader):
                    # Obtenir les données de competition et day pour chaque ligne
                    day_comp_row = day_comp_data[min(idx, len(day_comp_data) - 1)]
                    competition = day_comp_row['competition']
                    day = day_comp_row['journee']

                    # Insérer les données dans la table
                    cursor.execute(insert_sql, (
                        row['date_time'],         # Correspond à 'date'
                        row['team_1_name'],       # Correspond à 'team_a'
                        row['team_2_name'],       # Correspond à 'team_b'
                        int(row['team_1_score']), # Correspond à 'score_a'
                        int(row['team_2_score']), # Correspond à 'score_b'
                        competition,              # Correspond à 'competition'
                        day                       # Correspond à 'day'
                    ))

            # Valider les changements
            connection.commit()
            print(f"Données insérées avec succès depuis {results_csv} et {day_and_competition_csv}")

    except Exception as e:
        print(f"Erreur lors de l'insertion dans 'results' : {e}")