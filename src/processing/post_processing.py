import pandas as pd 
import os
import config

from src.utils.save_utils import salva_df
    

def order_players_by_position(positions: pd.DataFrame, players: pd.DataFrame):
    players_with_order = pd.merge(players, positions[["posizione", "ordine"]], on="posizione", how="left")

    players_sorted = players_with_order.sort_values(by="ordine")

    players = players_sorted.drop("ordine", axis=1)

    return players

def order_positions():
    POSITIONS_PATH = "data/posizioni.csv"
    DATA_PATH = "data/raw"
    FILE_NAME = "informazioni_giocatori"

    positions = pd.read_csv(POSITIONS_PATH)

    for campionato in config.campionati.values():
        for stagione in config.stagioni:
            for squadra in os.listdir(f"{DATA_PATH}/{campionato['nome']}/{stagione}"):
                if not os.path.isdir(f"{DATA_PATH}/{campionato['nome']}/{stagione}/{squadra}"):
                    continue
                info_players = pd.read_csv(f"{DATA_PATH}/{campionato['nome']}/{stagione}/{squadra}/{FILE_NAME}.csv")
                info_players = order_players_by_position(positions, info_players)
                salva_df(info_players, f"{DATA_PATH}/{campionato['nome']}/{stagione}/{squadra}/", FILE_NAME, "csv")