import logging
import os
import sys
import time

sys.path.insert(0, os.path.abspath(".."))

from dotenv import load_dotenv
from data_provider.factory import get_data_provider
from utils.save_data_utils import save_data

# Configura il logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Percorsi principali
DATA_RAW_PATH = os.path.abspath("../../data/raw/seriea")
TEAM_MATCHES_DIR = os.path.join(DATA_RAW_PATH, "team_matches")
RATE_LIMIT_PAUSE = 6  # Pausa in secondi per rispettare il limite API
LEAGUE_ID = "135"  # ID della Serie A per Football API su RapidAPI
SEASON = "2023"  # Stagione desiderata

# Carica la chiave API dal file .env
load_dotenv("../../config/.env")
API_KEY = os.getenv("RAPIDAPI_KEY")
if not API_KEY:
    logging.error(
        "La chiave API non è stata trovata. Assicurarsi che il file .env sia configurato correttamente."
    )
    sys.exit(1)

# Crea il provider
provider = get_data_provider("football_rapidapi", API_KEY)


def fetch_and_save_team_data():
    """
    Recupera e salva i dati delle squadre per la stagione specificata.

    Effettua una chiamata all'API per recuperare le informazioni di tutte le squadre
    della competizione specificata e salva i dati in formato JSON
    nella directory specificata.

    Returns:
        list: Una lista di dizionari contenenti le informazioni delle squadre,
              o None in caso di errore.

    Logs:
        logging.info: Logga il successo del salvataggio dei dati.
        logging.error: Logga un errore se i dati non possono essere recuperati.
    """
    teams_data = provider.fetch_teams(league_id=LEAGUE_ID, season=SEASON)
    if teams_data and "response" in teams_data:
        save_data(teams_data, DATA_RAW_PATH, "teams.json")
        logging.info("Dati delle squadre salvati correttamente.")
        return teams_data["response"]
    else:
        logging.error("Impossibile recuperare i dati delle squadre.")
        return None


def fetch_and_save_team_matches(team_id, team_name):
    """
    Recupera e salva i dati delle partite per una specifica squadra.

    Args:
        team_id (int): L'ID della squadra per cui recuperare le partite.
        team_name (str): Il nome della squadra, utilizzato per nominare il file.

    Logs:
        logging.info: Logga il successo del salvataggio dei dati per la squadra.
        logging.warning: Logga un avviso se i dati delle partite non possono essere recuperati.
    """
    matches_data = provider.fetch_team_matches(team_id=team_id, season=SEASON)
    if matches_data and "response" in matches_data:
        # Rimuove caratteri speciali dal nome della squadra per il nome del file
        safe_team_name = "".join(
            c for c in team_name if c.isalnum() or c in (" ", "_")
        ).replace(" ", "_")

        save_data(matches_data, TEAM_MATCHES_DIR, f"{safe_team_name}_matches.json")
        logging.info(f"Dati delle partite per {team_name} salvati correttamente.")
    else:
        logging.warning(f"Partite per {team_name} non recuperate.")


# Flusso principale
if __name__ == "__main__":
    """
    Flusso principale per l'acquisizione e il salvataggio dei dati delle squadre e delle partite.

    Descrizione:
        Questo script:
            - Carica la chiave API dal file .env per autenticarsi con il provider di dati.
            - Recupera e salva i dati di tutte le squadre in una competizione specifica.
            - Per ciascuna squadra, recupera e salva i dati delle partite.

    Logs:
        logging.info: Logga l'inizio e la fine del processo, e ogni salvataggio di successo.
        logging.error: Logga errori in caso di fallimento del recupero o salvataggio dei dati.
        logging.warning: Logga avvisi se i dati di partite di una squadra specifica non possono essere recuperati.
    """
    logging.info("Inizio del processo di acquisizione dati.")

    try:
        # Recupera e salva i dati delle squadre della Serie A
        teams = fetch_and_save_team_data()
        if not teams:
            logging.error("Nessuna squadra disponibile per il recupero delle partite.")
            sys.exit(1)

        # Recupera e salva le partite per ogni squadra
        for team in teams:
            team_id = team.get("team", {}).get("id")
            team_name = team.get("team", {}).get("name")
            if team_id and team_name:
                fetch_and_save_team_matches(team_id, team_name)
                # Pausa per rispettare il limite di 10 chiamate al minuto
                time.sleep(RATE_LIMIT_PAUSE)

        logging.info("Processo di acquisizione dati completato.")

    except Exception as e:
        logging.error(f"Errore non previsto durante il processo: {e}")
        sys.exit(1)  # Esci con codice di errore
