import json
import os

import pandas as pd

from src.scraping.scraper import TransfermarktScraper

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
}

stagioni = ["2024"]


# Inizializza lo scraper
scraper = TransfermarktScraper()

for campionato in campionati.values():
    campionato_url = campionato["url"]
    campionato_nome = campionato["nome"]

    for stagione in stagioni:
        print(f"\nInizio scraping per {campionato_nome} stagione {stagione}...")
        teams = scraper.scrape_teams(campionato_url, campionato_nome, stagione)
        print(f"Squadre scaricate: {len(teams)}")


CAMPIONATI_PATH = "data/raw/"

for campionato in os.listdir(CAMPIONATI_PATH):
    for stagione in os.listdir(os.path.join(CAMPIONATI_PATH, campionato)):
        teams = json.load(open(os.path.join(CAMPIONATI_PATH, campionato, stagione, "squadre.json"), "r", encoding="utf-8"))
        for team in teams:
            team_url = team["link"]
            team_name = team["name"]
            print(f"\nInizio scraping per {team_name}...")
            players = scraper.scrape_players(team_url, team_name, campionato, stagione)
            print(f"Giocatori scaricati: {len(players)}")
