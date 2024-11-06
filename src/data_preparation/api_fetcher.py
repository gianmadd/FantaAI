import json
import logging
import os
import time

import requests
from dotenv import load_dotenv

# Configura il logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

ENV_PATH = "../../config/.env"
DATA_RAW_PATH = "../../data/raw/seriea"
BASE_URL = "https://api.football-data.org/v4"

# Carica la chiave API dal file .env
load_dotenv(ENV_PATH)
API_KEY = os.getenv("FOOTBALL_API_KEY")

# Header per l'autenticazione
headers = {"X-Auth-Token": API_KEY}

if not API_KEY:
    logging.error(
        "La chiave API non è stata trovata. Assicurarsi che il file .env sia configurato correttamente."
    )
    exit(1)


def fetch_teams(competition_id="SA"):
    """
    Recupera tutte le squadre di una competizione specifica (es. Serie A).
    """
    url = f"{BASE_URL}/competitions/{competition_id}/teams"
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info("Dati delle squadre recuperati con successo.")
            return response.json()
        elif response.status_code == 429:
            # logging.warning("Limite di chiamate raggiunto. Pausa di 60 secondi...")
            time.sleep(0)  # Pausa di un minuto prima di riprovare
        else:
            logging.error(
                f"Errore nella chiamata API (status code: {response.status_code})"
            )
            return None


def fetch_team_matches(team_id):
    """
    Recupera le partite di una squadra specifica.
    """
    url = f"{BASE_URL}/teams/{team_id}/matches"
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info(
                f"Dati delle partite per il team {team_id} recuperati con successo."
            )
            return response.json()
        elif response.status_code == 429:
            # logging.warning("Limite di chiamate raggiunto. Pausa di 60 secondi...")
            time.sleep(0)  # Pausa di un minuto prima di riprovare
        else:
            logging.error(
                f"Errore nella chiamata API per il team {team_id} (status code: {response.status_code})"
            )
            return None


def save_data(data, filename):
    """
    Salva i dati in un file JSON.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    logging.info(f"Dati salvati in {filename}")


# Esempio di utilizzo
if __name__ == "__main__":
    # Recupera le squadre della Serie A
    teams_data = fetch_teams()

    if teams_data and "teams" in teams_data:
        save_data(teams_data, f"{DATA_RAW_PATH}/teams.json")
        logging.info(" -------------------------- Dati delle squadre salvati correttamente. -------------------------- ")

        # Recupera e salva le partite per ogni squadra
        for team in teams_data["teams"]:
            team_id = team.get("id")
            team_name = team.get("name")
            if team_id and team_name:
                matches_data = fetch_team_matches(team_id)
                if matches_data:
                    # Rimuovi caratteri speciali dal nome della squadra per evitare errori nel nome file
                    safe_team_name = "".join(
                        c for c in team_name if c.isalnum() or c in (" ", "_")
                    ).replace(" ", "_")
                    save_data(
                        matches_data, f"{DATA_RAW_PATH}/team_matches/{safe_team_name}_matches.json"
                    )
                    logging.info(
                        f" -------------------------- Dati delle partite per {team_name} salvati correttamente. -------------------------- "
                    )
                # Pausa per rispettare il limite di 10 chiamate al minuto
                time.sleep(0)
