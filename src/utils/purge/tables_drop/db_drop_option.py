from src.database.db_connector import get_connection

drop_sql_ranking = """
DROP TABLE IF EXISTS ranking;
"""

drop_sql_pool = """
DROP TABLE IF EXISTS pool;
"""


def drop_tables_ranking():
    """Drop la table 'ranking' en ouvrant une connexion locale et éphémère."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(drop_sql_ranking)
            print("Table 'ranking' dropped")
        conn.commit()
    finally:
        conn.close()


def drop_tables_results():
    """Drop la table 'pool' en ouvrant une connexion locale et éphémère."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(drop_sql_pool)
            print("Table 'pool' dropped")
        conn.commit()
    finally:
        conn.close()

