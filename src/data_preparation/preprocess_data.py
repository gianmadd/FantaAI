import json
import os

import pandas as pd

# Percorso alla cartella principale del progetto
DATA_RAW_PATH = "../../data/raw/seriea"
DATA_PROCESSED_PATH = "../../data/processed/seriea"


# Carica i dati delle squadre
def load_team_data():
    teams_file = f"{DATA_RAW_PATH}/teams.json"
    with open(teams_file, "r") as f:
        teams_data = json.load(f)
    return teams_data


# Carica i dati delle partite di tutte le squadre
def load_all_team_matches():
    matches_dir = f"{DATA_RAW_PATH}/team_matches"
    all_matches = []
    for filename in os.listdir(matches_dir):
        if filename.endswith("_matches.json"):
            with open(os.path.join(matches_dir, filename), "r") as f:
                matches_data = json.load(f)
                all_matches.extend(
                    matches_data["matches"]
                )  # Aggiunge tutte le partite in una lista
    matches_df = pd.DataFrame(all_matches)

    # Ordina per "matchday" e "stage"
    matches_df = matches_df.sort_values(by=["stage", "matchday"]).reset_index(drop=True)

    return matches_df


# Pulizia dei dati
def clean_data(matches_df):
    # Rimuove colonne non necessarie
    columns_to_drop = [
        "id",
        "season",
        "area",
        "competition",
        "group",
        "lastUpdated",
        "odds",
    ]  # Esempio
    matches_df.drop(columns=columns_to_drop, inplace=True, errors="ignore")

    # Gestione dei valori mancanti
    matches_df.fillna(0, inplace=True)

    return matches_df


# Feature Engineering
def add_features(matches_df):
    # Aggiungi nuove feature personalizzate qui
    # Esempio: una colonna per rappresentare il risultato della partita
    # matches_df["is_home_win"] = (matches_df["score"]["fullTime"]["homeTeam"] > matches_df["score"]["fullTime"]["awayTeam"]).astype(int)

    return matches_df


# Salvataggio dei dati preprocessati
def save_processed_data(matches_df):
    processed_dir = DATA_PROCESSED_PATH
    os.makedirs(processed_dir, exist_ok=True)
    processed_file = os.path.join(processed_dir, "matches_processed.csv")
    matches_df.to_csv(processed_file, index=False)
    print(f"Dati preprocessati salvati in {processed_file}")


# Esegui il preprocessamento
if __name__ == "__main__":
    teams_data = load_team_data()
    matches_df = load_all_team_matches()

    # Pulizia e aggiunta di feature
    matches_df = clean_data(matches_df)
    matches_df = add_features(matches_df)

    # Salva i dati preprocessati
    save_processed_data(matches_df)
