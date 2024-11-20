import logging
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(".."))

from dotenv import load_dotenv

from db.query_database import fetch_static_data
from utils.save_data_utils import save_processed_data_parquet  

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Carica le variabili di ambiente dal file .env
load_dotenv("../../config/.env")

# Variabili di percorso per i file di output
PROVIDER_NAME = os.getenv("PROVIDER_NAME")
DATA_PROCESSED_PATH_GENERIC = os.path.abspath(
    f"../../data/{PROVIDER_NAME}/processed/generics/"
)


def preprocess_and_save(table_name, filename):
    """
    Recupera, preprocessa e salva i dati statici utilizzando una funzione di recupero specificata.

    Args:
        table_name (str): Nome della tabella nel database.
        filename (str): Nome del file CSV da salvare (es. 'countries.csv').
    """
    try:
        df = fetch_static_data(table_name)
        df = df.drop_duplicates()
        save_processed_data_parquet(df, DATA_PROCESSED_PATH_GENERIC, filename)
    except Exception as e:
        logging.error(
            f"Errore durante il preprocessamento e salvataggio di {filename}: {e}"
        )


if __name__ == "__main__":
    logging.info("Inizio del processo di preprocessamento dei dati statici.")

    # Preprocessa e salva i dati per ogni tabella statica
    preprocess_and_save("countries", "countries.parquet")
    preprocess_and_save("timezones", "timezones.parquet")
    preprocess_and_save("leagues", "leagues.parquet")

    logging.info("Processo di preprocessamento completato.")
