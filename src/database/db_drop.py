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
