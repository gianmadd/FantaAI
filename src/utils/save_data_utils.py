import json
import logging
import os

import pandas as pd


def save_data(data, directory, filename):
    """
    Salva i dati in un file JSON nella directory specificata con il nome del file fornito.

    Questo metodo crea la directory, se non esiste, e salva i dati in formato JSON.
    È utile per archiviare dati grezzi o strutturati in formato JSON.

    Args:
        data (dict or list): I dati da salvare in formato JSON. Possono essere di tipo `dict` o `list`.
        directory (str): La directory in cui salvare il file. Se la directory non esiste, viene creata.
        filename (str): Il nome del file JSON, incluso l'estensione (es. 'data.json').

    Returns:
        None

    Logs:
        logging.info: Messaggio informativo con il percorso del file salvato.

    Raises:
        OSError: Se la creazione della directory o il salvataggio del file fallisce.

    Example:
        save_data(data={"key": "value"}, directory="data/raw", filename="output.json")
    """
    try:
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        logging.info(f"Dati salvati in {file_path}")

    except OSError as e:
        logging.error(f"Errore nel salvataggio del file JSON: {e}")
        raise


def save_processed_data(matches_df, directory, filename):
    """
    Salva i dati preprocessati in un file CSV nella directory specificata con il nome del file fornito.

    Questo metodo crea la directory, se non esiste, e salva i dati in formato CSV,
    utile per la persistenza dei dati tabulari elaborati in DataFrame.

    Args:
        matches_df (pd.DataFrame): Il DataFrame contenente i dati preprocessati.
        directory (str): La directory in cui salvare il file. Se la directory non esiste, viene creata.
        filename (str): Il nome del file CSV, incluso l'estensione (es. 'processed_data.csv').

    Returns:
        None

    Logs:
        logging.info: Messaggio informativo con il percorso del file salvato.

    Raises:
        OSError: Se la creazione della directory o il salvataggio del file fallisce.

    Example:
        save_processed_data(matches_df=my_dataframe, directory="data/processed", filename="output.csv")
    """
    try:
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)

        matches_df.to_csv(file_path, index=False)
        logging.info(f"Dati preprocessati salvati in {file_path}")

    except OSError as e:
        logging.error(f"Errore nel salvataggio del file CSV: {e}")
        raise
