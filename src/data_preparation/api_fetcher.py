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
DATA_RAW_PATH_GENERIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/raw/generics")
DATA_RAW_PATH_SPECIFIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/raw/specifics")

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
    file_name = replace_slash_with_underscore(endpoint)
    static_data = provider.fetch_static_data(endpoint)
    if static_data and "response" in static_data:
        save_data(static_data, DATA_RAW_PATH_GENERIC, f"{file_name}.json")
        logging.info(f"Dati statici per {endpoint} salvati correttamente.")
    else:
        logging.error(f"Impossibile recuperare i dati statici per {endpoint}.")


def fetch_and_save_teams_from_league_season(league_id, season):
    """
    Recupera e salva i dati delle squadre della Serie A per una stagione.

    Args:
        provider (DataProviderBase): Il provider di dati API configurato.
        league_id (str): L'ID della lega (Serie A).
        season (str): La stagione desiderata (ad es. "2023").

    """
    teams_data = provider.fetch_teams_from_league_season(league_id=league_id, season=season)
    if teams_data:
        save_data(teams_data, f"{DATA_RAW_PATH_SPECIFIC}/teams", f"{league_id}_{season}.json")
        logging.info(f"Dati delle squadre della {league_id} dell'anno {season} salvati correttamente.")
    else:
        logging.error(f"Impossibile recuperare i dati delle squadre della {league_id} dell'anno {season}")


def fetch_and_save_players_from_team_season(team_id, season):
        """
        Recupera e salva i dati dei giocatori di una squadra specifica per una stagione.

        Args:
            team_id (str): ID della squadra di cui recuperare i giocatori.
            team_name (str): Nome della squadra, usato per nominare il file.
            season (str): Anno della stagione.
            save_dir (str): Directory dove salvare i dati.
        """
        players_data = provider.fetch_players_from_team_season(team_id, season)
        if players_data and "response" in players_data:
            save_data(players_data, f"{DATA_RAW_PATH_SPECIFIC}/players", f"{team_id}_{season}.json")
            logging.info(f"Dati dei giocatori per {team_id} nella stagione {season} salvati correttamente.")
        else:
            logging.warning(f"Dati dei giocatori per {team_id} nella stagione {season} non recuperati.")



if __name__ == "__main__":
    logging.info("Inizio del processo di acquisizione dati.")

    try:
        fetch_and_save_teams_from_league_season(league_id=LEAGUE, season=SEASON)



        fetch_and_save_players_from_team_season(team_id=team_ids.get["FROSINONE"], season=SEASON)
        fetch_and_save_players_from_team_season(team_id=team_ids.get["GENOA"], season=SEASON)
        

    except Exception as e:
        logging.error(f"Errore non previsto durante il processo: {e}")
        sys.exit(1)
