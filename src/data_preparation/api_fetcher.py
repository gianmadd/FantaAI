import logging
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from dotenv import load_dotenv

from data_provider.factory import get_data_provider
from utils.save_data_utils import save_data, replace_slash_with_underscore

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


def fetch_and_save_static_data(endpoint):
    """
    Recupera e salva dati statici da un endpoint specifico.

    Args:
        endpoint (str): L'endpoint per i dati statici

        countries, leagues, seasons, timezone, odds/bets, odds/bookmakers, odds/mapping, players/profiles, players/seasons, teams/countries
    """
    url = f"{provider.BASE_URL}/{endpoint}"
    file_name = replace_slash_with_underscore(endpoint)
    static_data = provider._make_request(url, f"Dati statici per {endpoint}")
    if static_data and "response" in static_data:
        save_data(static_data, DATA_RAW_PATH, f"generics/{file_name}.json")
        logging.info(f"Dati statici per {endpoint} salvati correttamente.")
    else:
        logging.error(f"Impossibile recuperare i dati statici per {endpoint}.")


if __name__ == "__main__":
    logging.info("Inizio del processo di acquisizione dati.")
    try:

        fetch_and_save_static_data("teams/countries")

    except Exception as e:
        logging.error(f"Errore non previsto durante il processo: {e}")
        sys.exit(1)
