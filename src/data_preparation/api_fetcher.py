import logging
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from dotenv import load_dotenv

from data_provider.factory import get_data_provider
from utils.save_data_utils import save_data

# Configura il logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv("../../config/.env")

# Percorsi principali
PROVIDER_NAME = os.getenv("PROVIDER_NAME")
DATA_RAW_PATH = os.path.abspath(f"../../data/{PROVIDER_NAME}/raw/")
TEAM_MATCHES_DIR = os.path.join(DATA_RAW_PATH, "team_matches")
LEAGUE_ID = "135"  # ID della Serie A per Football API su RapidAPI
SEASON = "2023"  # Stagione desiderata

# Carica la chiave API dal file .env
API_KEY = os.getenv(f"{PROVIDER_NAME.upper()}_KEY")

if not API_KEY:
    logging.error(
        "La chiave API non è stata trovata. Assicurarsi che il file .env sia configurato correttamente."
    )
    sys.exit(1)

# Crea il provider
provider = get_data_provider(PROVIDER_NAME, API_KEY)


def fetch_and_save_team_data():
    teams_data = provider.fetch_teams(league_id=LEAGUE_ID, season=SEASON)
    if teams_data and "response" in teams_data:
        save_data(teams_data, DATA_RAW_PATH, "teams.json")
        logging.info("Dati delle squadre salvati correttamente.")
        return teams_data["response"]
    else:
        logging.error("Impossibile recuperare i dati delle squadre.")
        return None


def fetch_and_save_team_matches(team_id, team_name):
    matches_data = provider.fetch_team_matches(team_id=team_id, season=SEASON)
    if matches_data and "response" in matches_data:
        safe_team_name = "".join(
            c for c in team_name if c.isalnum() or c in (" ", "_")
        ).replace(" ", "_")
        save_data(matches_data, TEAM_MATCHES_DIR, f"{safe_team_name}_matches.json")
        logging.info(f"Dati delle partite per {team_name} salvati correttamente.")
    else:
        logging.warning(f"Partite per {team_name} non recuperate.")


def fetch_and_save_countries():
    """
    Recupera e salva i dati dei paesi.

    Returns:
        list: Una lista di dizionari contenenti le informazioni dei paesi,
              oppure None in caso di errore.
    """
    countries_data = provider.fetch_countries()
    if countries_data and "response" in countries_data:
        save_data(countries_data, DATA_RAW_PATH, "countries.json")
        logging.info("Dati dei paesi salvati correttamente.")
        return countries_data["response"]
    else:
        logging.error("Impossibile recuperare i dati dei paesi.")
        return None


def fetch_and_save_leagues():
    """
    Recupera e salva i dati dei campionati.

    Returns:
        list: Una lista di dizionari contenenti le informazioni dei campionati,
              oppure None in caso di errore.
    """
    leagues_data = provider.fetch_leagues()
    if leagues_data and "response" in leagues_data:
        save_data(leagues_data, DATA_RAW_PATH, "leagues.json")
        logging.info("Dati dei campionati salvati correttamente.")
        return leagues_data["response"]
    else:
        logging.error("Impossibile recuperare i dati dei campionati.")
        return None


if __name__ == "__main__":
    logging.info("Inizio del processo di acquisizione dati.")
    try:
        
        # Recupera e salva i dati dei paesi
        countries = fetch_and_save_countries()
        if not countries:
            logging.error("Nessun paese disponibile.")

        # Recupera e salva i dati dei campionati
        leagues = fetch_and_save_leagues()
        if not leagues:
            logging.error("Nessun campionato disponibile.")

    except Exception as e:
        logging.error(f"Errore non previsto durante il processo: {e}")
        sys.exit(1)
