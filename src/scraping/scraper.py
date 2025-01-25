import re
import time

import requests
from bs4 import BeautifulSoup, NavigableString

from src.utils.scraper_utils import (
    extract_altri_ruoli,
    extract_links_from_table,
    extract_nationalities,
    extract_player_details_from_header,
    extract_value_from_div,
    find_label_content,
    find_table,
    make_absolute_url,
    parse_player_name,
)


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
        Sends an HTTP GET request and returns a BeautifulSoup object.
        """
        print(f"Sending HTTP request to {url}")
        try:
            response = self.session.get(url)
            response.raise_for_status()
            print(f"Successfully fetched content from {url}")
            time.sleep(self.delay)
            return BeautifulSoup(response.text, "html.parser")
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred while fetching {url}: {http_err}")
        except Exception as err:
            print(f"An error occurred while fetching {url}: {err}")
        return None

    def scrape_teams(self, competition_url):
        """
        Extracts team names and links from the competition page.
        Returns a list of dictionaries with team details.
        """
        print(f"Starting to scrape teams from {competition_url}")
        soup = self.get_soup(competition_url)
        teams = []

        if not soup:
            print(f"Failed to retrieve soup for {competition_url}")
            return teams

        table = find_table(soup, table_class="items")
        if not table:
            print("Teams table not found.")
            return teams

        # Extract links from the table
        extracted_teams = extract_links_from_table(
            table, exclude_class="bg_blau_20", td_class="hauptlink no-border-links"
        )

        # Convert relative URLs to absolute URLs
        for team in extracted_teams:
            team["link"] = make_absolute_url(self.base_url, team["link"])
            teams.append(team)
            print(f"Found team: {team['name']}, Link: {team['link']}")

        print(f"Completed scraping teams. Total teams found: {len(teams)}")
        return teams

    def scrape_players(self, team_url):
        """
        Extracts players from a team's page.
        Returns a list of dictionaries with player details.
        """
        print(f"Starting to scrape players from {team_url}")
        soup = self.get_soup(team_url)
        players = []

        if not soup:
            print(f"Failed to retrieve soup for {team_url}")
            return players

        table = find_table(soup, table_class="items")
        if not table:
            print(f"Players table not found for team: {team_url}")
            return players

        # Extract links from the table
        extracted_players = extract_links_from_table(
            table, exclude_class="bg_blau_20", td_class="hauptlink"
        )

        # Convert relative URLs to absolute URLs
        for player in extracted_players:
            player["link"] = make_absolute_url(self.base_url, player["link"])
            players.append(player)
            print(f"Found player: {player['name']}, Link: {player['link']}")

        print(f"Completed scraping players. Total players found: {len(players)}")
        return players

    def scrape_player_details(self, player_url):
        """
        Extracts detailed information about a player from their Transfermarkt page.
        Returns a dictionary with player details.
        """
        # Define fixed columns
        COLUMN_ORDER = [
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

        # Initialize the details dictionary with None
        player_details = {col: None for col in COLUMN_ORDER}

        try:
            soup = self.get_soup(player_url)
            if not soup:
                return player_details

            # 1. Extract details from the header
            header = soup.find("h1", class_="data-header__headline-wrapper")
            if header:
                header_details = extract_player_details_from_header(header)
                player_details.update(header_details)
            else:
                print("Player header not found.")

            # 2. Extract from the first info-table div
            info_table = soup.select_one("div.info-table.info-table--right-space")
            if not info_table:
                # Try alternative class
                info_table = soup.select_one(
                    "div.info-table.info-table--right-space.min-height-audio"
                )

            if info_table:
                # Data di nascita and Età
                nato_il = find_label_content(info_table, r"Nato il:")
                if nato_il:
                    # Split data_nascita and età
                    if "(" in nato_il and ")" in nato_il:
                        data_nascita, età = nato_il.split("(")
                        player_details["data_nascita"] = data_nascita.strip()
                        player_details["età"] = età.strip(")")
                    else:
                        print("Unexpected format for 'Nato il:'")

                # Luogo di nascita
                luogo_nascita = find_label_content(info_table, r"Luogo di nascita:")
                if luogo_nascita:
                    player_details["luogo_nascita"] = luogo_nascita

                # Altezza
                altezza = find_label_content(info_table, r"Altezza:")
                if altezza:
                    player_details["altezza"] = (
                        altezza.replace("&nbsp;", " ").replace("m", "").strip()
                    )

                # Nazionalità
                nazionalita_span = info_table.find(
                    "span", text=re.compile(r"Nazionalità:", re.I)
                )
                if nazionalita_span:
                    nazionalita_content = nazionalita_span.find_next_sibling(
                        "span", class_="info-table__content--bold"
                    )
                    if nazionalita_content:
                        player_details["nazionalità"] = extract_nationalities(
                            nazionalita_content
                        )

                # Posizione
                posizione = find_label_content(info_table, r"Posizione:")
                if posizione:
                    player_details["posizione"] = posizione

                # Piede
                piede = find_label_content(info_table, r"Piede:")
                if piede:
                    player_details["piede"] = piede

                # Squadra attuale
                squadra_attuale = find_label_content(info_table, r"Squadra attuale:")
                if squadra_attuale:
                    # Assuming the last <a> tag contains the team name
                    squadra_links = info_table.find_all("a")
                    if squadra_links:
                        player_details["squadra_attuale"] = squadra_links[-1].get_text(
                            strip=True
                        )

                # In rosa da
                in_rosa_da = find_label_content(info_table, r"In rosa da:")
                if in_rosa_da:
                    player_details["in_rosa_da"] = in_rosa_da

                # Scadenza
                scadenza = find_label_content(info_table, r"Scadenza:")
                if scadenza:
                    player_details["scadenza"] = scadenza
            else:
                print("Info table div not found.")

            # 3. Extract from the second div (detail-position__box)
            detail_position = soup.find("div", class_="detail-position__box")
            if detail_position:
                # Ruolo naturale
                ruolo_naturale = find_label_content(detail_position, r"Ruolo naturale:")
                if ruolo_naturale:
                    player_details["ruolo_naturale"] = ruolo_naturale

                # Altri ruoli
                altri_ruoli = extract_altri_ruoli(detail_position)
                if altri_ruoli:
                    player_details["altri_ruoli"] = altri_ruoli
            else:
                print("Detail position box not found.")

            # 4. Extract values
            valore_div = soup.find("div", class_=re.compile(r"\bcurrent-and-max\b"))
            if valore_div:
                # Valore attuale
                valore_attuale = extract_value_from_div(
                    valore_div, r"\bcurrent-value\b"
                )
                if valore_attuale:
                    player_details["valore_attuale"] = valore_attuale

                # Valore più alto and data di aggiornamento
                max_div = valore_div.find("div", class_=re.compile(r"\bmax\b"))
                if max_div:
                    valore_piu_alto = extract_value_from_div(max_div, r"\bmax-value\b")
                    if valore_piu_alto:
                        player_details["valore_piu_alto"] = valore_piu_alto

                    # Assuming the third <div> inside 'max' contains 'data_aggiornamento'
                    divs_inside_max = max_div.find_all("div")
                    if len(divs_inside_max) >= 3:
                        data_aggiornamento = divs_inside_max[2].get_text(strip=True)
                        player_details["data_aggiornamento"] = data_aggiornamento
                    else:
                        player_details["data_aggiornamento"] = "Data non disponibile"
            else:
                print("'current-and-max' div not found.")

        except Exception as e:
            print(f"Error while scraping player details from {player_url}: {e}")

        return player_details
