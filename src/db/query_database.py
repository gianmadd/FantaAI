import os
import sys
from contextlib import contextmanager

import pandas as pd
import psycopg2
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(".."))
from db.database import get_db

# Carica le variabili di ambiente


def fetch_static_data(table_name):
    """
    Recupera i dati da una tabella statica specificata.

    Args:
        table_name (str): Nome della tabella da cui recuperare i dati (es. "countries", "timezones", "leagues").

    Returns:
        pd.DataFrame: Dati della tabella in formato DataFrame.
    """
    query = f"SELECT * FROM {table_name};"
    with get_db() as conn:
        df = execute_static_query(query)
    return df


def execute_static_query(query):
    """
    Esegue una query sul database e restituisce i risultati come DataFrame.

    Args:
        query (str): La query SQL da eseguire.
        params (tuple, opzionale): Parametri per la query.

    Returns:
        pd.DataFrame: Risultati della query come DataFrame.
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)
