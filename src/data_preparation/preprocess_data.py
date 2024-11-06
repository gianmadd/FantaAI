import json
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

import logging

import pandas as pd

from utils.save_data_utils import save_processed_data

# Configura il logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Percorsi principali
DATA_RAW_PATH = os.path.abspath("../../data/raw/seriea")
DATA_PROCESSED_PATH = os.path.abspath("../../data/processed/seriea")


def load_team_data():
    """
    Carica i dati delle squadre dal file JSON.

    Returns:
        dict: Un dizionario contenente i dati delle squadre, oppure None se si
              verifica un errore durante il caricamento.

    Logs:
        logging.info: Logga il successo del caricamento dei dati.
        logging.error: Logga un errore se il file non viene trovato o se il contenuto
                       non può essere decodificato.
    """
    teams_file = os.path.join(DATA_RAW_PATH, "teams.json")
    try:
        with open(teams_file, "r") as f:
            teams_data = json.load(f)
        logging.info("Dati delle squadre caricati con successo.")
    except FileNotFoundError:
        logging.error(f"File {teams_file} non trovato.")
        teams_data = None
    except json.JSONDecodeError:
        logging.error(f"Errore nel decodificare il file JSON {teams_file}.")
        teams_data = None
    return teams_data


def load_all_team_matches():
    """
    Carica i dati delle partite di tutte le squadre.

    Returns:
        pd.DataFrame: Un DataFrame contenente i dati delle partite di tutte le squadre.
                      Restituisce un DataFrame vuoto se non ci sono dati validi.

    Logs:
        logging.info: Logga il successo del caricamento e dell'ordinamento dei dati.
        logging.warning: Logga un avviso se non vengono trovati dati di partite.
        logging.error: Logga un errore se la directory o un file JSON non può essere
                       caricato correttamente.
    """
    matches_dir = os.path.join(DATA_RAW_PATH, "team_matches")
    all_matches = []

    if not os.path.exists(matches_dir):
        logging.error(f"La directory {matches_dir} non esiste.")
        return pd.DataFrame()

    filenames = sorted(
        f for f in os.listdir(matches_dir) if f.endswith("_matches.json")
    )

    for filename in filenames:
        file_path = os.path.join(matches_dir, filename)
        try:
            with open(file_path, "r") as f:
                matches_data = json.load(f)
                all_matches.extend(matches_data.get("matches", []))
            logging.info(f"Dati caricati dal file {filename}.")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Errore nel caricamento di {filename}: {e}")

    matches_df = pd.DataFrame(all_matches)
    if not matches_df.empty:
        matches_df = matches_df.sort_values(by=["stage", "matchday"]).reset_index(
            drop=True
        )
        logging.info("Dati delle partite caricati e ordinati con successo.")
    else:
        logging.warning("Nessun dato di partite caricato.")

    return matches_df


def clean_data(matches_df):
    """
    Rimuove colonne non necessarie e gestisce i valori mancanti nei dati delle partite.

    Args:
        matches_df (pd.DataFrame): Il DataFrame contenente i dati delle partite.

    Returns:
        pd.DataFrame: Il DataFrame con le colonne non necessarie rimosse e i
                      valori mancanti riempiti.

    Logs:
        logging.info: Logga il successo della pulizia dei dati.
    """
    columns_to_drop = [
        "id",
        "season",
        "area",
        "competition",
        "group",
        "lastUpdated",
        "odds",
    ]
    matches_df.drop(columns=columns_to_drop, inplace=True, errors="ignore")
    matches_df.fillna(0, inplace=True)
    logging.info("Dati puliti con successo.")
    return matches_df


def add_features(matches_df):
    """
    Aggiunge nuove feature personalizzate al DataFrame dei dati delle partite.

    Args:
        matches_df (pd.DataFrame): Il DataFrame contenente i dati delle partite.

    Returns:
        pd.DataFrame: Il DataFrame con le nuove feature aggiunte.

    Logs:
        logging.info: Logga l'applicazione di feature aggiuntive.
    """
    # Esempio di feature aggiuntiva
    # matches_df["is_home_win"] = (matches_df["score"]["fullTime"]["homeTeam"] > matches_df["score"]["fullTime"]["awayTeam"]).astype(int)
    logging.info("Feature aggiuntive applicate ai dati.")
    return matches_df


# Esegui il preprocessamento
if __name__ == "__main__":
    """
    Flusso principale per il preprocessamento dei dati delle squadre e delle partite.

    Descrizione:
        Questo script:
            - Carica i dati delle squadre e delle partite da file JSON.
            - Esegue operazioni di pulizia sui dati e aggiunge nuove feature.
            - Salva i dati preprocessati in un file CSV.

    Logs:
        logging.info: Logga l'inizio e la fine del processo, il caricamento, la pulizia
                      e il salvataggio dei dati.
        logging.warning: Logga avvisi se i dati delle squadre o delle partite sono mancanti.
        logging.error: Logga errori non previsti durante il processo.

    Raises:
        Exception: Se si verifica un errore inatteso durante il flusso.
    """
    logging.info("Inizio del processo di preprocessamento dei dati.")

    teams_data = load_team_data()
    if teams_data:
        matches_df = load_all_team_matches()

        if not matches_df.empty:
            matches_df = clean_data(matches_df)
            matches_df = add_features(matches_df)

            # Salva i dati preprocessati
            save_processed_data(matches_df, DATA_PROCESSED_PATH, "match_processed.csv")
        else:
            logging.warning("Non ci sono dati di partite da processare.")
    else:
        logging.warning("Non ci sono dati delle squadre da processare.")

    logging.info("Processo di preprocessamento completato.")
