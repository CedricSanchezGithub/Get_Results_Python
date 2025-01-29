from src.database.db_connector import get_connection

drop_sql_ranking = """
DROP TABLE IF EXISTS ranking;
"""

drop_sql_pool = """
DROP TABLE IF EXISTS pool;
"""

connection = get_connection()

def drop_tables_ranking():
    with connection.cursor() as cursor:
        cursor.execute(drop_sql_ranking)
        print("Table 'ranking' dropped")

def drop_tables_results():
    with connection.cursor() as cursor:
        cursor.execute(drop_sql_pool)
        print("Table 'pool' dropped")

