from sqlite3 import ProgrammingError

from src.database.db_connector import get_connection


def list_tables():
    """Liste les tables disponibles dans la base de données."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            return [table[0] for table in cursor.fetchall()]
    finally:
        print("voici la liste des tables")


def truncate_table(table_name):
    """Vide une table spécifique dans la base de données."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE TABLE {table_name};")
            print(f"Table '{table_name}' vidée avec succès.")
    finally:
        print("terminé")


from src.database.db_connector import get_connection


def table_exists(table_name):
    """
    Vérifie si une table existe dans la base de données
    """
    connection = get_connection()
    check_table_sql = f"""
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_schema = DATABASE() AND table_name = %s;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(check_table_sql, (table_name,))
            return cursor.fetchone()[0] > 0
    finally:
        connection.close()


def create_table(table_name):
    """
    Crée une table si elle n'existe pas et informe si elle existait déjà.
    """

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date_string VARCHAR(255) NULL,
        team_1_name VARCHAR(255) NOT NULL,
        team_1_score VARCHAR(255) NULL,
        team_2_name VARCHAR(255) NOT NULL,
        team_2_score VARCHAR(255) NULL,
        match_link VARCHAR(255) NULL,
        competition VARCHAR(255) NOT NULL,
        day VARCHAR(255) NULL
    );
    """

    connection = get_connection()
    try:
        table_already_exists = table_exists(table_name)

        with connection.cursor() as cursor:
            cursor.execute(create_table_sql)
            connection.commit()

        if table_already_exists:
            print(f"Table '{table_name}' existait déjà.")
        else:
            print(f"Table '{table_name}' créée avec succès.")

    except Exception as e:
        print(f"Erreur lors de la création de la table '{table_name}': {e}")

    finally:
        connection.close()

if __name__ == "__main__":
    tables = list_tables()
    if tables:
        print("Tables disponibles :")
        for i, table in enumerate(tables, start=1):
            print(f"{i}. {table}")

        try:
            choice = int(input("Entrez le numéro de la table à vider : "))
            if 1 <= choice <= len(tables):
                table_to_truncate = tables[choice - 1]
                truncate_table(table_to_truncate)
            else:
                print("Choix invalide.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un numéro valide.")
    else:
        print("Aucune table disponible.")
