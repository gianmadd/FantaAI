import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.utils.save_utils import salva_df
from src.scraping.scraper import TransfermarktScraper

def scrape_and_save_teams(scraper: TransfermarktScraper, campionato: dict, stagione: str) -> pd.DataFrame:
    """
    Scrape le squadre di un campionato per una specifica stagione e salva i dati.

    Args:
        scraper (TransfermarktScraper): L'istanza dello scraper.
        campionato (dict): Dizionario contenente le informazioni del campionato.
        stagione (str): La stagione da scrapare.

    Returns:
        pd.DataFrame: DataFrame contenente le squadre scrappate.
    """
    campionato_url = campionato["url"]
    campionato_nome = campionato["nome"]

    print(f"Inizio scraping per {campionato_nome} stagione {stagione}...")
    teams = scraper.scrape_teams(campionato_url)
    print(f"Squadre scaricate: {len(teams)}")

    if not teams:
        print(f"Nessuna squadra trovata per {campionato_nome} stagione {stagione}.")
        return pd.DataFrame()

    # Converti le squadre in DataFrame
    teams_df = pd.DataFrame(teams).drop_duplicates()

    # Aggiungi colonne per campionato e stagione
    teams_df["campionato"] = campionato_nome
    teams_df["stagione"] = stagione

    teams_df = teams_df[["campionato", "stagione", "name", "link"]]

    # Salva i dati delle squadre
    cartella_squadre = os.path.join("data", "raw", campionato_nome.lower(), stagione)
    salva_df(teams_df, cartella_squadre, "squadre")

    print(f"Squadre salvate in {cartella_squadre}/squadre.csv")
    return teams_df

def scrape_and_save_players(scraper: TransfermarktScraper, team: pd.Series, campionato_nome: str, stagione: str, max_workers: int = 5):
    """
    Scrape i giocatori di una squadra e salva i dati, inclusi i dettagli dei giocatori in parallelo.

    Args:
        scraper (TransfermarktScraper): L'istanza dello scraper.
        team (pd.Series): Serie contenente i dettagli della squadra.
        campionato_nome (str): Nome del campionato.
        stagione (str): La stagione.
        max_workers (int): Numero massimo di thread da utilizzare per la parallelizzazione.
    """
    team_url = team["link"]
    team_name = team["name"]

    print(f"Inizio scraping per {team_name}...")
    players = scraper.scrape_players(team_url)
    print(f"Giocatori scaricati: {len(players)}")

    if not players:
        print(f"Nessun giocatore trovato per la squadra {team_name}.")
        return

    # Converti i giocatori in DataFrame
    players_df = pd.DataFrame(players).drop_duplicates()

    # Aggiungi colonne per squadra, campionato e stagione
    players_df["squadra"] = team_name
    players_df["campionato"] = campionato_nome
    players_df["stagione"] = stagione

    players_df = players_df[["campionato", "stagione", "squadra", "name", "link"]]

    # Salva i dati dei giocatori
    cartella_giocatori = os.path.join("data", "raw", campionato_nome.lower(), stagione, team_name)
    salva_df(players_df, cartella_giocatori, "giocatori")

    print(f"Giocatori salvati in {cartella_giocatori}/giocatori.csv")

    # Scrape e salva i dettagli dei giocatori in parallelo
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_giocatore = {
            executor.submit(scrape_and_save_player_details, scraper, giocatore["link"], cartella_giocatori, giocatore["name"]): giocatore["name"]
            for _, giocatore in players_df.iterrows()
        }

        for future in as_completed(future_to_giocatore):
            giocatore_nome = future_to_giocatore[future]
            try:
                future.result()
            except Exception as e:
                print(f"Errore nello scraping del giocatore {giocatore_nome}: {e}")

def scrape_and_save_player_details(scraper: TransfermarktScraper, giocatore_url: str, squadra_path: str, giocatore_nome: str):
    """
    Scrape i dettagli di un giocatore e salva i dati.

    Args:
        scraper (TransfermarktScraper): L'istanza dello scraper.
        giocatore_url (str): URL del giocatore da scrapare.
        squadra_path (str): Percorso della cartella della squadra.
        giocatore_nome (str): Nome del giocatore.
    """
    try:
        print(f"Inizio scraping dei dettagli per il giocatore {giocatore_nome}...")
        dettagli = scraper.scrape_player_details(giocatore_url)

        if dettagli:
            # Converti i dettagli in DataFrame
            df_dettagli = pd.DataFrame([dettagli])

            # Definisci il percorso del file 'informazioni_giocatori.csv'
            informazioni_path_csv = os.path.join(squadra_path, "informazioni_giocatori.csv")

            # Salva in CSV (in modalità append)
            if os.path.exists(informazioni_path_csv):
                df_dettagli.to_csv(informazioni_path_csv, mode='a', header=False, index=False, encoding="utf-8")
            else:
                df_dettagli.to_csv(informazioni_path_csv, index=False, encoding="utf-8")

            print(f"Dettagli del giocatore {giocatore_nome} salvati in {informazioni_path_csv}")
        else:
            print(f"Dettagli del giocatore {giocatore_nome} non disponibili.")
    except Exception as e:
        print(f"Errore nello scraping del giocatore {giocatore_nome} ({giocatore_url}): {e}")


