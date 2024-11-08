import json
import logging
import os
import time
from datetime import datetime

import requests

from data_provider.data_provider_base import DataProviderBase


class FootballRapidAPI(DataProviderBase):
    """
    Classe per l'integrazione con Football API di RapidAPI.

    Questa classe implementa un controllo rigoroso per rispettare i limiti di utilizzo dell'API:
    - 100 richieste al giorno
    - 30 richieste al minuto

    Attributes:
        BASE_URL (str): L'URL base per l'API di Football su RapidAPI.
        RATE_LIMIT_SLEEP (float): Pausa per rispettare il limite di 30 richieste al minuto.
        api_key (str): La chiave API per autenticazione.
        headers (dict): Headers HTTP per includere la chiave API nelle richieste.
        request_counter_file (str): Percorso del file di contatore richieste giornaliero.
    """

    BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
    RATE_LIMIT_MINUTE = 30
    DAILY_LIMIT = 100
    RATE_LIMIT_SLEEP = 60 / RATE_LIMIT_MINUTE

    def __init__(self, provider_name, api_key, counter_dir="../../config"):
        """
        Inizializza il provider con la chiave API necessaria e il percorso di salvataggio del contatore.

        Args:
            api_key (str): La chiave API per autenticarsi con il servizio.
            counter_dir (str): Directory dove salvare il file di contatore richieste.
        """
        if not api_key:
            raise ValueError("La chiave API non è valida o mancante.")

        self.api_key = api_key
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
        }
        self.provider_name = provider_name

        # Nome del file di contatore specifico per la classe, nella directory specificata
        self.request_counter_file = os.path.join(
            counter_dir, f"{self.provider_name}_counter.json"
        )
        self.request_counter = self.load_request_counter()

    def load_request_counter(self):
        """
        Carica il contatore delle richieste dal file JSON. Se il file è vuoto,
        danneggiato, o non esiste, lo inizializza con i campi necessari.
        """
        if os.path.exists(self.request_counter_file):
            try:
                with open(self.request_counter_file, "r") as f:
                    data = json.load(f)
                    # Verifica che il file contenga i dati corretti
                    if (
                        not isinstance(data, dict)
                        or "count" not in data
                        or "date" not in data
                    ):
                        logging.warning(
                            "File di contatore danneggiato o incompleto. Reinizializzo il contatore."
                        )
                        data = self.initialize_request_counter()
            except json.JSONDecodeError:
                logging.warning(
                    "File di contatore vuoto o corrotto. Reinizializzo il contatore."
                )
                data = self.initialize_request_counter()
        else:
            # Inizializza un nuovo contatore se il file non esiste
            data = self.initialize_request_counter()

        return data

    def initialize_request_counter(self):
        """
        Inizializza il contatore con i campi necessari e lo salva nel file JSON.
        """
        data = {"count": 0, "date": datetime.now().strftime("%Y-%m-%d")}
        self.save_request_counter(data)
        return data

    def save_request_counter(self, data=None):
        """
        Salva il contatore delle richieste nel file JSON.
        """
        if data is None:
            data = (
                self.request_counter
            )  # Usa self.request_counter solo se è stato già inizializzato
        with open(self.request_counter_file, "w") as f:
            json.dump(data, f)

    def reset_request_counter_if_new_day(self):
        """
        Resetta il contatore giornaliero se la data è cambiata rispetto all'ultima richiesta.
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        if self.request_counter["date"] != current_date:
            self.request_counter = {"count": 0, "date": current_date}
            self.save_request_counter()

    def _make_request(self, url, log_context):
        """
        Effettua una singola richiesta API con gestione di rate limiting e limite giornaliero.

        Args:
            url (str): L'URL da richiamare.
            log_context (str): Contesto per i log.

        Returns:
            dict: Risultato JSON della richiesta o None se si supera il limite.
        """
        # Controlla e resetta il contatore giornaliero se necessario
        self.reset_request_counter_if_new_day()

        # Blocca se il limite giornaliero è stato raggiunto
        if self.request_counter["count"] >= self.DAILY_LIMIT:
            logging.warning("Limite giornaliero di richieste raggiunto.")
            return None

        try:
            # Effettua la richiesta
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:

                remaining_requests = response.headers.get(
                    "x-ratelimit-requests-remaining"
                )
                logging.info(f"Richieste rimanenti per oggi: {remaining_requests}")

                logging.info(f"{log_context} recuperati con successo.")
                self.request_counter["count"] += 1
                self.save_request_counter()
                time.sleep(
                    self.RATE_LIMIT_SLEEP
                )  # Pausa per rispettare il rate limit minuto
                return response.json()

            elif response.status_code == 429:
                logging.warning(
                    f"Rate limit raggiunto. Pausa di {self.RATE_LIMIT_SLEEP} secondi."
                )
                time.sleep(self.RATE_LIMIT_SLEEP)
                logging.info("Riprovo la richiesta dopo pausa.")
                return self._make_request(url, log_context)  # Retry dopo la pausa

            else:
                logging.error(
                    f"Errore nella chiamata API ({log_context}) - Status code: {response.status_code}"
                )
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Errore di connessione durante {log_context}: {e}")
            return None

    def fetch_teams(self, league_id, season):
        """
        Recupera le squadre per una specifica lega e stagione.

        Args:
            league_id (str): L'ID della lega.
            season (str): La stagione.

        Returns:
            dict: I dati JSON delle squadre o None se si supera il limite.
        """
        url = f"{self.BASE_URL}/teams?league={league_id}&season={season}"
        return self._make_request(
            url, f"Dati delle squadre per lega {league_id} e stagione {season}"
        )

    def fetch_team_matches(self, team_id, season):
        """
        Recupera le partite per una squadra e stagione specifica.

        Args:
            team_id (int): L'ID della squadra.
            season (str): La stagione.

        Returns:
            dict: I dati JSON delle partite o None se si supera il limite.
        """
        url = f"{self.BASE_URL}/fixtures?team={team_id}&season={season}"
        return self._make_request(
            url, f"Dati delle partite per il team {team_id} e stagione {season}"
        )

    def fetch_countries(self):
        """
        Recupera la lista dei paesi disponibili nell'API.

        Returns:
            dict: Dati JSON dei paesi o None se si supera il limite.
        """
        url = f"{self.BASE_URL}/countries"
        return self._make_request(url, "Dati dei paesi")

    def fetch_leagues(self):
        """
        Recupera la lista dei campionati disponibili nell'API.

        Returns:
            dict: Dati JSON dei campionati o None se si supera il limite.
        """
        url = f"{self.BASE_URL}/leagues"
        return self._make_request(url, "Dati dei campionati")
