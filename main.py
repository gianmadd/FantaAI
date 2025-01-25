# main.py

import os
import pandas as pd

from src.scraping.scraper import TransfermarktScraper
from src.utils.save_utils import salva_df

# Configurazione dei campionati e stagioni
campionati = {
    "serie_a": {
        "url": "https://www.transfermarkt.it/serie-a/startseite/wettbewerb/IT1",
        "nome": "Serie A",
    },
    "premier_league": {
        "url": "https://www.transfermarkt.it/premier-league/startseite/wettbewerb/GB1",
        "nome": "Premier League",
    },
    "la_liga": {
        "url": "https://www.transfermarkt.it/la-liga/startseite/wettbewerb/ES1",
        "nome": "La Liga",
    },
    "bundesliga": {
        "url": "https://www.transfermarkt.it/bundesliga/startseite/wettbewerb/L1",
        "nome": "Bundesliga",
    },
    "ligue_1": {
        "url": "https://www.transfermarkt.it/ligue-1/startseite/wettbewerb/FR1",
        "nome": "Ligue 1",
    },
}

stagioni = ["2024"]

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

    print(f"\nInizio scraping per {campionato_nome} stagione {stagione}...")
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

def scrape_and_save_players(scraper: TransfermarktScraper, team: pd.Series, campionato_nome: str, stagione: str):
    """
    Scrape i giocatori di una squadra e salva i dati.

    Args:
        scraper (TransfermarktScraper): L'istanza dello scraper.
        team (pd.Series): Serie contenente i dettagli della squadra.
        campionato_nome (str): Nome del campionato.
        stagione (str): La stagione.
    """
    team_url = team["link"]
    team_name = team["name"]

    print(f"\nInizio scraping per {team_name}...")
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

    # Scrape e salva i dettagli dei giocatori
    for _, giocatore in players_df.iterrows():
        giocatore_url = giocatore["link"]
        giocatore_nome = giocatore["name"]
        scrape_and_save_player_details(scraper, giocatore_url, cartella_giocatori, giocatore_nome)

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

def main():
    # Inizializza lo scraper
    scraper = TransfermarktScraper()

    # Scraping delle squadre e dei giocatori sequenzialmente
    for campionato in campionati.values():
        for stagione in stagioni:
            print(f"Scraping per {campionato['nome']} stagione {stagione}...")
            # Scraping delle squadre del campionato
            squadre_df = scrape_and_save_teams(scraper, campionato, stagione)

            if squadre_df.empty:
                print(f"Nessuna squadra trovata per {campionato['nome']} stagione {stagione}.")
                continue

            # Scraping dei giocatori e dei loro dettagli per tutte le squadre
            for _, team in squadre_df.iterrows():
                scrape_and_save_players(scraper, team, campionato["nome"], stagione)

    print("\nScraping completato per tutti i campionati e tutte le squadre.")

if __name__ == "__main__":
    main()
