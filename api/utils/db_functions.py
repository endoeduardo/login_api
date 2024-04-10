"""Funções de gerenciamento de db"""
import psycopg2
from psycopg2 import OperationalError

def create_connection(db_name, db_user, db_password, db_host, db_port):
    """Cria uma conexão com um banco de dados postgres"""
    connection = None
    try:
        connection = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        print("Connection to PostgreSQL successful")

    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection
