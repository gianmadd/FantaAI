import requests
from bs4 import BeautifulSoup
import time

class TransfermarktScraper:
    def __init__(self, base_url="https://www.transfermarkt.it", headers=None, delay=1):
        """
        Inizializza lo scraper con l'URL di base, gli header HTTP e un ritardo tra le richieste.
        """
        self.base_url = base_url
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.delay = delay  # Ritardo tra le richieste in secondi
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_soup(self, url):
        """
        Effettua una richiesta HTTP e restituisce un oggetto BeautifulSoup.
        """
        print(f"Richiesta HTTP a {url}")
        response = self.session.get(url)
        response.raise_for_status()  # Solleva un'eccezione per risposte non valide
        print(f"Richiesta a {url} riuscita.")
        time.sleep(self.delay)  # Ritardo per evitare di sovraccaricare il server
        return BeautifulSoup(response.text, 'html.parser')

    def scrape_teams(self, competition_url):
        """
        Estrae i nomi delle squadre e i relativi link dalla pagina di competizione.
        Restituisce una lista di dizionari con i dettagli delle squadre.
        """
        soup = self.get_soup(competition_url)
        teams = []

        # Trova la tabella delle squadre
        table = soup.find('table', class_='items')
        if not table:
            print("Non è stata trovata la tabella delle squadre.")
            return teams

        # Trova il corpo della tabella
        tbody = table.find('tbody')
        if not tbody:
            print("Non è stato trovato il corpo della tabella.")
            return teams

        # Itera sulle righe della tabella
        for row in tbody.find_all('tr', class_=lambda x: x != 'bg_blau_20'):
            team_cell = row.find('td', class_='hauptlink no-border-links')
            if team_cell:
                link_tag = team_cell.find('a', href=True)
                if link_tag:
                    name = link_tag.get_text(strip=True)
                    link = f"{self.base_url}{link_tag['href']}"
                    teams.append({'name': name, 'link': link})
                    print(f"Squadra trovata: {name}, Link: {link}")

        print(f"Scraping delle squadre completato. {len(teams)} squadre trovate.")
        return teams

    def scrape_players(self, team_url):
        """
        Estrae i giocatori di una squadra dalla pagina della squadra.
        Restituisce una lista di dizionari con i dettagli dei giocatori.
        """
        soup = self.get_soup(team_url)
        players = []

        # Trova la tabella dei giocatori
        table = soup.find('table', class_='items')
        if not table:
            print(f"Non è stata trovata la tabella dei giocatori per la squadra: {team_url}")
            return players

        # Trova il corpo della tabella
        tbody = table.find('tbody')
        if not tbody:
            print(f"Non è stato trovato il corpo della tabella dei giocatori per la squadra: {team_url}")
            return players

        # Itera sulle righe della tabella
        for row in tbody.find_all('tr', class_=lambda x: x != 'bg_blau_20'):
            player_cell = row.find('td', class_='hauptlink')
            if player_cell:
                link_tag = player_cell.find('a', href=True)
                if link_tag:
                    name = link_tag.get_text(strip=True)
                    link = f"{self.base_url}{link_tag['href']}"
                    players.append({'name': name, 'link': link})
                    print(f"Giocatore trovato: {name}, Link: {link}")

        print(f"Scraping dei giocatori completato. {len(players)} giocatori trovati.")
        return players