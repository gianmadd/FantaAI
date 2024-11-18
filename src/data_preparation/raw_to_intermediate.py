import json
import logging
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(".."))
from utils.save_data_utils import save_data

# Configura il logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv("../../config/.env")

# Percorsi principali (seguendo la struttura del fetcher)
PROVIDER_NAME = os.getenv("PROVIDER_NAME")
DATA_RAW_PATH_GENERIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/raw/generics/")
DATA_RAW_PATH_SPECIFIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/raw/specifics/players/2023")
DATA_CLEANED_PATH_GENERIC = os.path.abspath(
    f"../../data/{PROVIDER_NAME}/cleaned/generics/"
)
DATA_CLEANED_PATH_SPECIFIC = os.path.abspath(
    f"../../data/{PROVIDER_NAME}/cleaned/specifics/players/2023"
)


def clean_json(input_path, output_path):
    """
    Pulisce un file JSON mantenendo solo i campi 'get', 'parameters' e 'response'.

    Args:
        input_path (str): Il percorso del file JSON da pulire.
        output_path (str): Il percorso di destinazione per il file JSON pulito.

    Logs:
        logging.info: Logga il successo del processo di pulizia.
        logging.error: Logga errori in caso di problemi.
    """
    try:
        with open(input_path, "r") as f:
            data = json.load(f)

        # Estrarre solo i campi necessari
        cleaned_data = {
            "get": data.get("get"),
            "parameters": data.get("parameters", {}),
            "response": data.get("response", []),
        }

        # Dividi output_path in directory e filename per compatibilità con save_data
        directory = os.path.dirname(output_path)
        filename = os.path.basename(output_path)

        # Salva il JSON pulito nella cartella cleaned
        os.makedirs(directory, exist_ok=True)
        save_data(cleaned_data, directory, filename)

        logging.info(f"Dati puliti salvati correttamente in {output_path}")

    except FileNotFoundError:
        logging.error(f"File {input_path} non trovato.")
    except json.JSONDecodeError:
        logging.error(f"Errore nel decodificare il file JSON {input_path}.")


def process_raw_data_files(data_type):
    """
    Pulisce tutti i file JSON grezzi in una cartella specifica e li salva nella cartella dei dati puliti.

    Args:
        data_type (str): Tipo di dati ('generic' o 'specific') per determinare le directory di input/output.
    """
    if data_type == "generics":
        input_dir = DATA_RAW_PATH_GENERIC
        output_dir = DATA_CLEANED_PATH_GENERIC
    elif data_type == "specifics":
        input_dir = DATA_RAW_PATH_SPECIFIC
        output_dir = DATA_CLEANED_PATH_SPECIFIC
    else:
        logging.error("Tipo di dati non valido. Utilizzare 'generics' o 'specifics'.")
        return

    # Crea la directory di output se non esiste
    os.makedirs(output_dir, exist_ok=True)

    # Elabora ciascun file nella directory di input
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            clean_json(input_path, output_path)


if __name__ == "__main__":
    logging.info("Inizio del processo di pulizia dei dati.")

    # Pulizia dei dati generici e specifici
    # process_raw_data_files("generics")
    process_raw_data_files("specifics")

    logging.info("Processo di pulizia dei dati completato.")
