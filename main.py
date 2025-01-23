import os

import pandas as pd

from src.scraping.scraper import TransfermarktScraper

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


def salva_df(df, cartella, nome_file):
    """
    Salva un DataFrame in formato JSON e CSV nella cartella specificata.
    """
    os.makedirs(cartella, exist_ok=True)  # Crea la cartella se non esiste

    # Salva in JSON
    percorso_json = os.path.join(cartella, f"{nome_file}.json")
    df.to_json(percorso_json, orient="records", force_ascii=False, indent=4)
    print(f"Dati salvati in JSON: {percorso_json}")

    # Salva in CSV
    percorso_csv = os.path.join(cartella, f"{nome_file}.csv")
    df.to_csv(percorso_csv, index=False, encoding="utf-8")
    print(f"Dati salvati in CSV: {percorso_csv}")


def scrape_campionato(scraper, campionato_url, campionato_nome, stagione):
    """
    Scrapes teams for a single campionato and stagione, restituisce un DataFrame
    contenente i dati delle squadre, il campionato e la stagione.
    """
    print(f"\nInizio scraping per {campionato_nome} stagione {stagione}...")
    teams = scraper.scrape_teams(campionato_url)
    print(f"Squadre scaricate: {len(teams)}")

    # Converti le squadre in DataFrame
    teams_df = pd.DataFrame(teams)

    teams_df = teams_df.drop_duplicates()

    # Aggiungi colonne per campionato e stagione
    teams_df["campionato"] = campionato_nome
    teams_df["stagione"] = stagione

    teams_df = teams_df[["campionato", "stagione", "name", "link"]]

    return teams_df


def scrape_squadra(scraper, team_url, team_name, campionato_nome, stagione):
    """
    Scrapes players for a single squadra, restituisce un DataFrame
    contenente i dati dei giocatori, il nome della squadra, il campionato e la stagione.
    """
    print(f"\nInizio scraping per {team_name}...")
    players = scraper.scrape_players(team_url)
    print(f"Giocatori scaricati: {len(players)}")

    # Converti i giocatori in DataFrame
    players_df = pd.DataFrame(players)

    players_df = players_df.drop_duplicates()

    # Aggiungi colonne per squadra, campionato e stagione
    players_df["squadra"] = team_name
    players_df["campionato"] = campionato_nome
    players_df["stagione"] = stagione

    players_df = players_df[["campionato", "stagione", "squadra", "name", "link"]]

    return players_df


def main():
    # # Inizializza lo scraper
    scraper = TransfermarktScraper()

    # # Itera su tutti i campionati
    # for campionato in campionati.values():
    #     campionato_url = campionato["url"]
    #     campionato_nome = campionato["nome"]

    #     # Itera su tutte le stagioni
    #     for stagione in stagioni:
    #         print(f"\nInizio scraping per {campionato_nome} stagione {stagione}...")

    #         # Scraping delle squadre del campionato
    #         squadre_df = scrape_campionato(scraper, campionato_url, campionato_nome, stagione)
    #         print(f"Squadre scaricate: {len(squadre_df)}")

    #         # Salva i dati delle squadre
    #         cartella_squadre = os.path.join("data", "raw", campionato_nome.lower(), stagione)
    #         salva_df(squadre_df, cartella_squadre, "squadre")

    #         # Itera su tutte le squadre del campionato
    #         for _, team in squadre_df.iterrows():
    #             team_url = team["link"]
    #             team_name = team["name"]
    #             print(f"\nInizio scraping per {team_name}...")

    #             # Scraping dei giocatori della squadra
    #             giocatori_df = scrape_squadra(scraper, team_url, team_name, campionato_nome, stagione)
    #             print(f"Giocatori scaricati: {len(giocatori_df)}")

    #             # Salva i dati dei giocatori
    #             cartella_giocatori = os.path.join("data", "raw", campionato_nome.lower(), stagione, team_name)
    #             salva_df(giocatori_df, cartella_giocatori, "giocatori")

    # print("\nScraping completato per tutti i campionati e tutte le squadre.")

    DATA_PATH = "data/raw/"

    informazioni_giocatori_df = pd.DataFrame(
        columns=[
            "numero_maglia",
            "nome",
            "cognome",
            "data_nascita",
            "età",
            "luogo_nascita",
            "altezza",
            "nazionalità",
            "posizione",
            "piede",
            "ruolo_naturale",
            "altri_ruoli",
            "in_rosa_da",
            "scadenza",
            "squadra_attuale",
            "valore_attuale",
            "valore_piu_alto",
            "data_aggiornamento",
        ]
    )

    for campionato in os.listdir(DATA_PATH):
        CAMPIOANTO_PATH = os.path.join(DATA_PATH, campionato)
        for stagione in os.listdir(CAMPIOANTO_PATH):
            STAGIONE_PATH = os.path.join(CAMPIOANTO_PATH, stagione)
            for squadra in os.listdir(STAGIONE_PATH):
                if squadra == "SSC Napoli":
                    SQUADRA_PATH = os.path.join(STAGIONE_PATH, squadra)
                    GIOCATORI_PATH = os.path.join(SQUADRA_PATH, "giocatori.csv")
                    giocatori_df = pd.read_csv(GIOCATORI_PATH)
                    for _, giocatore in giocatori_df.iterrows():
                        giocatore_url = giocatore["link"]
                        giocatore_nome = giocatore["name"]
                        print(f"\nInizio scraping per {giocatore_nome}...")

                        # Estrai i dettagli del giocatore
                        dettagli_giocatore = scraper.scrape_player_details(giocatore_url)

                        dettagli_giocatore = pd.DataFrame([dettagli_giocatore])

                        # Concatena i dettagli al DataFrame
                        informazioni_giocatori_df = pd.concat(
                            [informazioni_giocatori_df, dettagli_giocatore],
                            ignore_index=True,
                        )

                        print(f"Dettagli del giocatore {giocatore_nome} scaricati.")

                    salva_df(
                        informazioni_giocatori_df, SQUADRA_PATH, "informazioni_giocatori"
                    )




if __name__ == "__main__":
    main()
