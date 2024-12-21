import pymysql

def get_connection():
    """Crée et retourne une connexion à la base de données."""
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='getresults'
    )
    return connection
