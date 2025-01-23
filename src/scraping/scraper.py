import re
import time

import requests
from bs4 import BeautifulSoup, NavigableString


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
        return BeautifulSoup(response.text, "html.parser")

    def scrape_teams(self, competition_url):
        """
        Estrae i nomi delle squadre e i relativi link dalla pagina di competizione.
        Restituisce una lista di dizionari con i dettagli delle squadre.
        """
        soup = self.get_soup(competition_url)
        teams = []

        # Trova la tabella delle squadre
        table = soup.find("table", class_="items")
        if not table:
            print("Non è stata trovata la tabella delle squadre.")
            return teams

        # Trova il corpo della tabella
        tbody = table.find("tbody")
        if not tbody:
            print("Non è stato trovato il corpo della tabella.")
            return teams

        # Itera sulle righe della tabella
        for row in tbody.find_all("tr", class_=lambda x: x != "bg_blau_20"):
            team_cell = row.find("td", class_="hauptlink no-border-links")
            if team_cell:
                link_tag = team_cell.find("a", href=True)
                if link_tag:
                    name = link_tag.get_text(strip=True)
                    link = f"{self.base_url}{link_tag['href']}"
                    teams.append({"name": name, "link": link})
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
        table = soup.find("table", class_="items")
        if not table:
            print(
                f"Non è stata trovata la tabella dei giocatori per la squadra: {team_url}"
            )
            return players

        # Trova il corpo della tabella
        tbody = table.find("tbody")
        if not tbody:
            print(
                f"Non è stato trovato il corpo della tabella dei giocatori per la squadra: {team_url}"
            )
            return players

        # Itera sulle righe della tabella
        for row in tbody.find_all("tr", class_=lambda x: x != "bg_blau_20"):
            player_cell = row.find("td", class_="hauptlink")
            if player_cell:
                link_tag = player_cell.find("a", href=True)
                if link_tag:
                    name = link_tag.get_text(strip=True)
                    link = f"{self.base_url}{link_tag['href']}"
                    players.append({"name": name, "link": link})
                    print(f"Giocatore trovato: {name}, Link: {link}")

        print(f"Scraping dei giocatori completato. {len(players)} giocatori trovati.")
        return players

    def scrape_player_details(self, player_url):
        """
        Estrae le informazioni dettagliate di un giocatore dalla sua pagina.
        Restituisce un dizionario con i dettagli del giocatore.
        """
        # Definizione delle colonne fisse
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
            "data_aggiornamento"
        ]


        soup = self.get_soup(player_url)
        if not soup:
            # Restituisce un dizionario con tutti i campi impostati a None
            return {col: None for col in COLUMN_ORDER}

        # Inizializza il dizionario con tutte le chiavi impostate a None
        player_details = {col: None for col in COLUMN_ORDER}

        try:
            # 1. Estrazione dall'header (Numero di Maglia, Nome, Cognome)
            header = soup.find("h1", class_="data-header__headline-wrapper")
            if header:
                # Numero di Maglia
                numero_maglia_span = header.find(
                    "span", class_="data-header__shirt-number"
                )
                if numero_maglia_span:
                    numero_maglia = numero_maglia_span.get_text(strip=True).replace(
                        "#", ""
                    )
                    player_details["numero_maglia"] = numero_maglia
                    print(f"Numero di Maglia: {numero_maglia}")
                else:
                    print("Numero di maglia non trovato.")

                # Nome e Cognome
                nome = ""
                cognome = ""

                for child in header.children:
                    if isinstance(child, NavigableString):
                        text = child.strip()
                        if text:
                            nome = text
                    elif child.name == "strong":
                        cognome = child.get_text(strip=True)

                if nome:
                    player_details["nome"] = nome
                    print(f"Nome: {nome}")
                else:
                    print("Nome non trovato.")

                if cognome:
                    player_details["cognome"] = cognome
                    print(f"Cognome: {cognome}")
                else:
                    print("Cognome non trovato.")
            else:
                print("Header del giocatore non trovato.")

            # 2. Estrazione dalla prima div (info-table)
            info_table = soup.select_one("div.info-table.info-table--right-space")
            if info_table is None:
                # Prova con l'altra classe che include 'min-height-audio'
                info_table = soup.select_one(
                    "div.info-table.info-table--right-space.min-height-audio"
                )

            if info_table:
                # Data di nascita e Età
                nato_il_label = info_table.find(
                    "span", text=re.compile(r"Nato il:", re.I)
                )
                if nato_il_label:
                    nato_il_a = nato_il_label.find_next_sibling(
                        "span", class_="info-table__content--bold"
                    ).find("a")
                    if nato_il_a:
                        nato_il = nato_il_a.get_text(strip=True)
                        if "(" in nato_il and ")" in nato_il:
                            data_nascita, età = nato_il.split("(")
                            data_nascita = data_nascita.strip()
                            età = età.strip(")")
                            player_details["data_nascita"] = data_nascita
                            player_details["età"] = età
                            print(f"Data di Nascita: {data_nascita}, Età: {età}")
                        else:
                            print("Formato inatteso per 'Nato il:'.")
                    else:
                        print("Tag <a> non trovato per 'Nato il:'.")
                else:
                    print("'Nato il:' non trovato.")

                # Luogo di nascita
                luogo_nascita_label = info_table.find(
                    "span", text=re.compile(r"Luogo di nascita:", re.I)
                )
                if luogo_nascita_label:
                    luogo_nascita_span = luogo_nascita_label.find_next_sibling(
                        "span", class_="info-table__content--bold"
                    ).find("span")
                    if luogo_nascita_span and luogo_nascita_span.contents:
                        luogo = luogo_nascita_span.contents[0].strip()
                        player_details["luogo_nascita"] = luogo
                        print(f"Luogo di Nascita: {luogo}")
                    else:
                        print(
                            "Luogo di nascita non trovato o struttura HTML inattesa."
                        )
                else:
                    print("'Luogo di nascita:' non trovato.")

                # Altezza
                altezza_label = info_table.find(
                    "span", text=re.compile(r"Altezza:", re.I)
                )
                if altezza_label:
                    altezza = (
                        altezza_label.find_next_sibling(
                            "span", class_="info-table__content--bold"
                        )
                        .get_text(strip=True)
                        .replace("&nbsp;", " ")
                        .replace("m", "")
                        .strip()
                    )
                    player_details["altezza"] = altezza
                    print(f"Altezza: {altezza}")
                else:
                    print("'Altezza:' non trovato.")

                # Nazionalità (Multiple)
                nazionalita_label = info_table.find(
                    "span", text=re.compile(r"Nazionalità:", re.I)
                )
                if nazionalita_label:
                    nazionalita_span = nazionalita_label.find_next_sibling(
                        "span", class_="info-table__content--bold"
                    )
                    if nazionalita_span:
                        nazionalita = [
                            img["title"]
                            for img in nazionalita_span.find_all("img", alt=True)
                        ]
                        player_details["nazionalità"] = nazionalita
                        print(f"Nazionalità: {nazionalita}")
                    else:
                        print("Span per 'Nazionalità' non trovato.")
                else:
                    print("'Nazionalità:' non trovato.")

                # Posizione
                posizione_label = info_table.find(
                    "span", text=re.compile(r"Posizione:", re.I)
                )
                if posizione_label:
                    posizione = posizione_label.find_next_sibling(
                        "span", class_="info-table__content--bold"
                    ).get_text(strip=True)
                    player_details["posizione"] = posizione
                    print(f"Posizione: {posizione}")
                else:
                    print("'Posizione:' non trovato.")

                # Piede
                piede_label = info_table.find("span", text=re.compile(r"Piede:", re.I))
                if piede_label:
                    piede = piede_label.find_next_sibling(
                        "span", class_="info-table__content--bold"
                    ).get_text(strip=True)
                    player_details["piede"] = piede
                    print(f"Piede: {piede}")
                else:
                    print("'Piede:' non trovato.")

                # Squadra attuale
                squadra_label = info_table.find(
                    "span", text=re.compile(r"Squadra attuale:", re.I)
                )
                if squadra_label:
                    # Usa una funzione lambda per gestire le classi multiple
                    squadra_span = squadra_label.find_next_sibling(
                        "span",
                        class_=lambda x: x
                        and "info-table__content--bold" in x
                        and "info-table__content--flex" in x,
                    )
                    if squadra_span:
                        squadra = squadra_span.find_all("a")[-1].get_text(strip=True)
                        player_details["squadra_attuale"] = squadra
                        print(f"Squadra Attuale: {squadra}")
                    else:
                        print("Span per 'Squadra attuale' non trovato.")
                else:
                    print("'Squadra attuale:' non trovato.")

                # In rosa da
                in_rosa_da_label = info_table.find(
                    "span", text=re.compile(r"In rosa da:", re.I)
                )
                if in_rosa_da_label:
                    in_rosa_da = in_rosa_da_label.find_next_sibling(
                        "span", class_="info-table__content--bold"
                    ).get_text(strip=True)
                    player_details["in_rosa_da"] = in_rosa_da
                    print(f"In Rosa Da: {in_rosa_da}")
                else:
                    print("'In rosa da:' non trovato.")

                # Scadenza
                scadenza_label = info_table.find(
                    "span", text=re.compile(r"Scadenza:", re.I)
                )
                if scadenza_label:
                    scadenza = scadenza_label.find_next_sibling(
                        "span", class_="info-table__content--bold"
                    ).get_text(strip=True)
                    player_details["scadenza"] = scadenza
                    print(f"Scadenza Contratto: {scadenza}")
                else:
                    print("'Scadenza:' non trovato.")
            else:
                print(
                    "Div 'info-table' non trovato con nessuna delle classi specificate."
                )

            # 3. Estrazione dalla seconda div (detail-position__box)
            detail_position = soup.find("div", class_="detail-position__box")
            if detail_position:
                # Ruolo naturale
                ruolo_naturale_label = detail_position.find(
                    "dt", text=re.compile(r"Ruolo naturale:", re.I)
                )
                if ruolo_naturale_label:
                    ruolo_naturale_dd = ruolo_naturale_label.find_next_sibling("dd")
                    if ruolo_naturale_dd:
                        ruolo_naturale = ruolo_naturale_dd.get_text(strip=True)
                        player_details["ruolo_naturale"] = ruolo_naturale
                        print(f"Ruolo Naturale: {ruolo_naturale}")
                    else:
                        print("Tag <dd> per 'Ruolo naturale' non trovato.")
                else:
                    print("'Ruolo naturale:' non trovato.")

                # Altri ruoli
                altri_ruoli_label = detail_position.find(
                    "dt", text=re.compile(r"Altro ruolo:", re.I)
                )
                if altri_ruoli_label:
                    altri_ruoli_dds = altri_ruoli_label.find_next_siblings("dd")
                    if altri_ruoli_dds:
                        altri_ruoli = [
                            dd.get_text(strip=True) for dd in altri_ruoli_dds
                        ]
                        player_details["altri_ruoli"] = altri_ruoli
                        print(f"Altri Ruoli: {altri_ruoli}")
                    else:
                        print("Tag <dd> per 'Altro ruolo' non trovato.")
                else:
                    print("'Altro ruolo:' non trovato.")
            else:
                print("Div 'detail-position__box' non trovato.")

            # 4. Estrazione dei valori
            valore_div = soup.find("div", class_=re.compile(r'\bcurrent-and-max\b'))
            if valore_div:
                # Valore attuale
                valore_attuale_div = valore_div.find("div", class_=re.compile(r'\bcurrent-value\b'))
                if valore_attuale_div:
                    # Cerca un tag <a>, se presente
                    valore_attuale_a = valore_attuale_div.find("a")
                    if valore_attuale_a:
                        valore_attuale = valore_attuale_a.get_text(strip=True)
                    else:
                        # Se non c'è un tag <a>, prendi il testo direttamente
                        valore_attuale = valore_attuale_div.get_text(strip=True)
                    
                    player_details["valore_attuale"] = valore_attuale
                    print(f"Valore Attuale: {valore_attuale}")
                else:
                    print("'current-value' div non trovato.")

                # Valore più alto e data di aggiornamento
                valore_max_div = valore_div.find("div", class_=re.compile(r'\bmax\b'))
                if valore_max_div:
                    valore_piu_alto_div = valore_max_div.find("div", class_=re.compile(r'\bmax-value\b'))
                    if valore_piu_alto_div:
                        valore_piu_alto = valore_piu_alto_div.get_text(strip=True)
                        # Assumendo che la data di aggiornamento sia nel terzo <div> dentro 'max'
                        divs_inside_max = valore_max_div.find_all("div")
                        if len(divs_inside_max) >= 3:
                            data_aggiornamento = divs_inside_max[2].get_text(strip=True)
                        else:
                            data_aggiornamento = "Data non disponibile"
                        player_details["valore_piu_alto"] = valore_piu_alto
                        player_details["data_aggiornamento"] = data_aggiornamento
                        print(f"Valore Più Alto: {valore_piu_alto}, Data di Aggiornamento: {data_aggiornamento}")
                    else:
                        print("Tag <div class='max-value'> non trovato.")
                else:
                    print("'max' div non trovato.")
            else:
                print("'current-and-max' div non trovato.")
                

        except Exception as e:
            print(f"Errore durante l'analisi del giocatore: {e}")

        return player_details
