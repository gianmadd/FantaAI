import json
import logging
import os
import sys
from dotenv import load_dotenv

# Aggiunta del percorso per i moduli utili
sys.path.insert(0, os.path.abspath(".."))

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Carica variabili di ambiente
load_dotenv("../../config/.env")
PROVIDER_NAME = os.getenv("PROVIDER_NAME")
DATA_CLEANED_PATH_GENERIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/cleaned/generics/")
DATA_CLEANED_PATH_SPECIFIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/cleaned/specifics/")

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
    """Carica i dati da un file JSON già pulito."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        logging.info(f"Dati caricati da {file_path}")
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Errore nel caricamento di {file_path}: {e}")
        return None

def load_teams_data():
    """Carica i dati delle squadre dalla cartella cleaned."""
    return load_data(os.path.join(DATA_CLEANED_PATH_SPECIFIC, "teams", f"{LEAGUE}_{SEASON}.json"))

def load_players_data(team_id, season):
    """Carica i dati dei giocatori per una specifica squadra e stagione dalla cartella cleaned."""
    return load_data(
        os.path.join(DATA_CLEANED_PATH_SPECIFIC, "players", f"{team_id}_{season}.json")
    )

if __name__ == "__main__":
    # Carica e visualizza i dati delle squadre
    teams_data = load_teams_data()
    if teams_data:
        logging.info("Dati delle squadre caricati correttamente.")

    # Carica e visualizza i dati dei giocatori per ciascuna squadra
    for team_name, team_id in team_ids.items():
        players_data = load_players_data(team_id, SEASON)
        if players_data:
            logging.info(f"Dati dei giocatori per {team_name} caricati correttamente.")
            
