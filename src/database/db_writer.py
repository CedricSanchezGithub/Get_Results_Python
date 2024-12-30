import csv

from src.database.db_drop_option import connection


def db_writer_ranking():
    """Insère les données de classement dans la base de données MySQL."""
    csv_file = "data/ranking.csv"

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



def db_writer_results():
    """Insère les données des résultats de match dans la table 'results' de la base de données MySQL."""
    results_csv = "data/results.csv"
    day_and_competition_csv = "data/day_and_competition.csv"

    insert_sql = """
    INSERT INTO results (date, team_1_name,team_1_score, team_2_name, team_2_score, match_link, competition, day)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        with connection.cursor() as cursor:
            # Lire les deux fichiers CSV
            with open(day_and_competition_csv, newline='', encoding='utf-8') as day_comp_file, \
                 open(results_csv, newline='', encoding='utf-8') as results_file:
                day_comp_reader = list(csv.DictReader(day_comp_file))
                results_reader = csv.DictReader(results_file)

                for idx, row in enumerate(results_reader):
                    # Récupérer les données competition et journee
                    if idx < len(day_comp_reader):
                        day_comp_row = day_comp_reader[idx]
                        competition = day_comp_row.get('competition', None)
                        day = day_comp_row.get('journee', None)
                    else:
                        competition = None
                        day = None

                    # Valider les données avant insertion
                    if not all([row.get('date'), row.get('team_1_name'), row.get('team_1_score'), row.get('team_2_name'), row.get('team_2_score'), row.get('match_link')]):
                        print(f"Ligne invalide ignorée : {row}")
                        continue

                    # Insérer les données dans la base
                    try:
                        cursor.execute(insert_sql, (
                            row['date'],
                            row['team_1_name'],
                            int(row['team_1_score']),
                            row['team_2_name'],
                            int(row['team_2_score']),
                            row['match_link'],
                            competition,
                            day
                        ))
                    except Exception as e:
                        print(f"Erreur lors de l'insertion pour la ligne {row} : {e}")
                        continue

            connection.commit()
            print(f"Données insérées avec succès depuis {results_csv} et {day_and_competition_csv}")

    except Exception as e:
        print(f"Erreur lors de l'insertion dans 'results' : {e}")
