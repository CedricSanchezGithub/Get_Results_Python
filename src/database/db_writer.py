import csv
from db_connector import get_connection

csv_file = "../../data/results.csv"

sql = """
INSERT INTO ranking (position, club_name, points)
VALUES (%s, %s, %s)
"""

connection = get_connection()

with connection.cursor() as cursor:
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row)
            cursor.execute(sql, (row['position'], row['club_name'], row['points']))

connection.commit()
print("Données insérées avec succès")
connection.close()
