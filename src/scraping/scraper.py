import requests
from bs4 import BeautifulSoup
import json
import os
import time

class TransfermarktScraper:
    def __init__(self, base_url="https://www.transfermarkt.it", headers=None, delay=1):
        self.base_url = base_url
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        self.delay = delay  # Ritardo tra le richieste in secondi
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_soup(self, url):
        print(f"Richiesta HTTP a {url}")
        response = self.session.get(url)
        response.raise_for_status()
        print(f"Richiesta a {url} riuscita.")
        time.sleep(self.delay)  # Ritardo per evitare di sovraccaricare il server
        return BeautifulSoup(response.text, 'html.parser')

    def scrape_teams(self, competition_url, campionato, stagione):
        """
        Estrae i nomi delle squadre e i relativi link dalla pagina di competizione.
        Salva i dati in data/raw/[Campionato]/[Stagione]/squadre.json
        """
        soup = self.get_soup(competition_url)
        teams = []
        table = soup.find('table', class_='items')
        if not table:
            print("Non è stata trovata la tabella delle squadre.")
            return teams

        tbody = table.find('tbody')
        if not tbody:
            print("Non è stato trovato il corpo della tabella.")
            return teams

        for row in tbody.find_all('tr', class_=lambda x: x != 'bg_blau_20'):
            team_cell = row.find('td', class_='hauptlink no-border-links')
            if team_cell:
                link_tag = team_cell.find('a', href=True)
                if link_tag:
                    name = link_tag.get_text(strip=True)
                    link = f"{self.base_url}{link_tag['href']}"
                    teams.append({'name': name, 'link': link})
                    print(f"Squadra trovata: {name}, Link: {link}")

        # Definisci il percorso di salvataggio
        output_path = os.path.join("data", "raw", campionato, stagione, "squadre.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Salva i risultati in un file JSON
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(teams, f, ensure_ascii=False, indent=4)

        print(f"Scraping delle squadre completato. {len(teams)} squadre trovate e salvate in {output_path}.")
        return teams

    def scrape_players(self, team_url, team_name, campionato, stagione):
        """
        Estrae i giocatori di una squadra dalla pagina della squadra.
        Salva i dati in data/raw/[Campionato]/[Stagione]/[Squadra]/giocatori.json
        """
        soup = self.get_soup(team_url)
        players = []
        table = soup.find('table', class_='items')
        if not table:
            print(f"Non è stata trovata la tabella dei giocatori per la squadra: {team_url}")
            return players

        tbody = table.find('tbody')
        if not tbody:
            print(f"Non è stato trovato il corpo della tabella dei giocatori per la squadra: {team_url}")
            return players

        for row in tbody.find_all('tr', class_=lambda x: x != 'bg_blau_20'):
            player_cell = row.find('td', class_='hauptlink')
            if player_cell:
                link_tag = player_cell.find('a', href=True)
                if link_tag:
                    name = link_tag.get_text(strip=True)
                    link = f"{self.base_url}{link_tag['href']}"
                    players.append({'name': name, 'link': link})
                    print(f"Giocatore trovato: {name}, Link: {link}")

        output_dir = os.path.join("data", "raw", campionato, stagione, team_name)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "giocatori.json")
        
        # Salva i risultati in un file JSON
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(players, f, ensure_ascii=False, indent=4)

        print(f"Scraping dei giocatori completato. {len(players)} giocatori trovati e salvati in {output_path}.")
        return players
