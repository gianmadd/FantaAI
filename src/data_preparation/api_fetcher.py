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
DATA_RAW_PATH = os.path.abspath(f"../../data/{PROVIDER_NAME}/raw/seriea1")
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


if __name__ == "__main__":
    logging.info("Inizio del processo di acquisizione dati.")
    try:
        teams = fetch_and_save_team_data()
        if not teams:
            logging.error("Nessuna squadra disponibile per il recupero delle partite.")
            sys.exit(1)

        # for team in teams:
        #     team_id = team.get("team", {}).get("id")
        #     team_name = team.get("team", {}).get("name")
        #     if team_id and team_name:
        #         fetch_and_save_team_matches(team_id, team_name)

        # logging.info("Processo di acquisizione dati completato.")

    except Exception as e:
        logging.error(f"Errore non previsto durante il processo: {e}")
        sys.exit(1)
