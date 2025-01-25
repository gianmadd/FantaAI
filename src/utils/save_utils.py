import os
import pandas as pd
import logging

def salva_df(df: pd.DataFrame, cartella: str, nome_file: str, formato: str = "csv"):
    """
    Salva un DataFrame in formato CSV o JSON nella cartella specificata.

    Args:
        df (pd.DataFrame): Il DataFrame da salvare.
        cartella (str): Il percorso della cartella dove salvare il file.
        nome_file (str): Il nome del file senza estensione.
        formato (str, optional): Il formato di salvataggio ("csv" o "json"). Defaults to "csv".
    """
    try:
        os.makedirs(cartella, exist_ok=True)  # Crea la cartella se non esiste
        if formato == "csv":
            percorso = os.path.join(cartella, f"{nome_file}.csv")
            df.to_csv(percorso, index=False, encoding="utf-8")
            logging.info(f"Dati salvati in CSV: {percorso}")
        elif formato == "json":
            percorso = os.path.join(cartella, f"{nome_file}.json")
            df.to_json(percorso, orient="records", force_ascii=False, indent=4)
            logging.info(f"Dati salvati in JSON: {percorso}")
        else:
            logging.error(f"Formato di salvataggio non supportato: {formato}")
    except Exception as e:
        logging.error(f"Errore nel salvataggio del DataFrame: {e}")
