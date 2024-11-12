import contextlib
import os
import psycopg2
from dotenv import load_dotenv

# Carica le variabili di ambiente dal file .env
load_dotenv("../../config/.env")

# Assegna le variabili di ambiente
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def get_database_url():
    """
    Costruisce e restituisce la stringa di connessione al database.

    Returns:
        dict: Dizionario con i parametri di connessione al database.

    Raises:
        ValueError: Se una delle variabili di ambiente richieste è assente.
    """
    # Verifica che tutte le variabili di ambiente siano caricate correttamente
    missing_vars = [
        var
        for var, value in {
            "DB_NAME": DB_NAME,
            "DB_USER": DB_USER,
            "DB_PASSWORD": DB_PASSWORD,
            "DB_HOST": DB_HOST,
            "DB_PORT": DB_PORT,
        }.items()
        if not value
    ]

    if missing_vars:
        raise ValueError(f"Variabili di ambiente mancanti: {', '.join(missing_vars)}")

    return {
        "dbname": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "host": DB_HOST,
        "port": DB_PORT
    }


# Parametri di connessione
db_params = get_database_url()

@contextlib.contextmanager
def get_db():
    """
    Genera una connessione al database utilizzando `psycopg2`, compatibile con il costrutto 'with'.

    Yields:
        conn: Una connessione al database PostgreSQL.
    """
    conn = psycopg2.connect(**db_params)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO fanta_ai")
        yield conn
    finally:
        conn.close()

# Esempio di utilizzo
if __name__ == "__main__":
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"Versione del database: {db_version}")
