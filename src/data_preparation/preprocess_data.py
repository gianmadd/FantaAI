import json
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

import pandas as pd
from dotenv import load_dotenv

from utils.save_data_utils import save_processed_data

# Configurazione di logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Carica variabili di ambiente
load_dotenv("../../config/.env")
PROVIDER_NAME = os.getenv("PROVIDER_NAME")
DATA_RAW_PATH_GENERIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/raw/generics")
DATA_RAW_PATH_SPECIFIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/raw/specifics")
DATA_PROCESSED_PATH_GENERIC = os.path.abspath(
    f"../../data/{PROVIDER_NAME}/processed/generics"
)
DATA_PROCESSED_PATH_SPECIFIC = os.path.abspath(
    f"../../data/{PROVIDER_NAME}/processed/specifics"
)


LEAGUE = "135"
SEASON = "2023"

team_ids = {
    "ATALANTA": "499",
    "BOLOGNA": "500",
    "CAGLIARI": "490",
    "EMPOLI": "511",
    "FIORENTINA": "502",
    "FROSINONE": "512",
    "GENOA": "495",
    "INTER": "505",
    "JUVENTUS": "496",
    "LAZIO": "487",
    "LECCE": "867",
    "MILAN": "489",
    "MONZA": "1579",
    "NAPOLI": "492",
    "ROMA": "497",
    "SALERNITANA": "514",
    "SASSUOLO": "488",
    "TORINO": "503",
    "UDINESE": "494",
    "VERONA": "504",
}


def load_data(file_path):
    """Carica i dati da un file JSON."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        logging.info(f"Dati caricati da {file_path}")
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Errore nel caricamento di {file_path}: {e}")
        return None


def load_teams_data():
    """Carica i dati delle squadre dal file JSON."""
    return load_data(os.path.join(DATA_RAW_PATH_SPECIFIC, "teams", "135_2023.json"))


def load_players_data(team_id, season):
    """Carica i dati dei giocatori per una specifica squadra e stagione."""
    return load_data(
        os.path.join(DATA_RAW_PATH_SPECIFIC, "players", f"{team_id}_{season}.json")
    )


def clean_and_process_data(raw_data, columns_to_drop=None):
    """
    Pulizia dei dati e rimozione di colonne non necessarie.

    Args:
        raw_data (list or dict): Dati grezzi caricati dal file JSON.
        columns_to_drop (list): Colonne da rimuovere dai dati.
    """
    df = pd.DataFrame(raw_data["response"])

    if columns_to_drop:
        df.drop(columns=columns_to_drop, inplace=True, errors="ignore")

    # Esempio di gestione dei valori mancanti
    df.fillna(0, inplace=True)
    logging.info("Dati puliti con successo.")
    return df


if __name__ == "__main__":
    # Processo di preprocessamento dei dati
    logging.info("Inizio del processo di preprocessamento.")

    teams_data = load_teams_data()
    if teams_data:
        teams_df = clean_and_process_data(
            teams_data, columns_to_drop=["venue", "id", "area"]
        )
        save_processed_data(
            teams_df, DATA_PROCESSED_PATH_SPECIFIC, "teams_processed.csv"
        )

    for team_name, team_id in team_ids.items():

        players_data = load_players_data(team_id, SEASON)
        if players_data:
            players_df = clean_and_process_data(players_data)
            save_processed_data(
                players_df,
                DATA_PROCESSED_PATH_SPECIFIC,
                f"{team_id}_players_processed.csv",
            )

    logging.info("Processo di preprocessamento completato.")
