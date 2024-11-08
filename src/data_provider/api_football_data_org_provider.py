import json
import logging
import os
import time
from datetime import datetime
import requests
from data_provider.data_provider_base import DataProviderBase

class FootballDataOrgAPI(DataProviderBase):
    """
    Classe per l'integrazione con l'API di Football-Data.org.

    Implementa controlli per:
    - Limite giornaliero di richieste.
    - Rate limiting in caso di errore 429 (pausa di 60 secondi).

    Attributes:
        BASE_URL (str): L'URL base per l'API di Football-Data.org.
        RATE_LIMIT_SLEEP (int): Tempo in secondi per rispettare il rate limit in caso di errore 429.
        DAILY_LIMIT (int): Limite massimo di richieste giornaliere.
        api_key (str): La chiave API per autenticazione.
        headers (dict): Headers HTTP per includere la chiave API nelle richieste.
    """

    BASE_URL = "https://api.football-data.org/v4"
    RATE_LIMIT_SLEEP = 60  # Pausa di 60 secondi per rate limit
    DAILY_LIMIT = 100

    def __init__(self, provider_name, api_key, counter_dir="../../config"):
        """
        Inizializza il provider con la chiave API e il percorso per il contatore.

        Args:
            api_key (str): La chiave API per autenticarsi con il servizio.
            counter_dir (str): Directory dove salvare il file di contatore richieste.
        """
        if not api_key:
            raise ValueError("La chiave API non è valida o mancante.")

        self.api_key = api_key
        self.headers = {"X-Auth-Token": self.api_key}
        self.provider_name = provider_name

        # Nome del file di contatore specifico per la classe
        self.request_counter_file = os.path.join(
            counter_dir, f"{self.provider_name}_counter.json"
        )
        self.request_counter = self.load_request_counter()

    def load_request_counter(self):
        """
        Carica il contatore delle richieste dal file JSON o lo inizializza se non esiste.
        """
        if os.path.exists(self.request_counter_file):
            with open(self.request_counter_file, "r") as f:
                data = json.load(f)
        else:
            data = {"count": 0, "date": datetime.now().strftime("%Y-%m-%d")}
        return data

    def save_request_counter(self):
        """
        Salva il contatore delle richieste nel file JSON.
        """
        with open(self.request_counter_file, "w") as f:
            json.dump(self.request_counter, f)

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
        Effettua una singola richiesta API con gestione del rate limit e logging.

        Args:
            url (str): L'URL da richiamare.
            log_context (str): Descrizione per il logging, usata per identificare la richiesta.

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
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                logging.info(f"{log_context} recuperati con successo.")
                self.request_counter["count"] += 1
                self.save_request_counter()
                return response.json()

            elif response.status_code == 429:
                logging.warning(f"Rate limit raggiunto. Pausa di {self.RATE_LIMIT_SLEEP} secondi.")
                time.sleep(self.RATE_LIMIT_SLEEP)
                return self._make_request(url, log_context)  # Retry dopo la pausa

            else:
                logging.error(f"Errore nella chiamata API ({log_context}) - Status code: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Errore di connessione durante {log_context}: {e}")
            return None

    def fetch_teams(self, competition_id):
        """
        Recupera le squadre per una competizione specifica.

        Args:
            competition_id (str): ID della competizione (es. "SA" per Serie A).

        Returns:
            dict: Dati JSON delle squadre o None se si supera il limite.
        """
        url = f"{self.BASE_URL}/competitions/{competition_id}/teams"
        return self._make_request(url, f"Dati delle squadre per competizione {competition_id}")

    def fetch_team_matches(self, team_id):
        """
        Recupera le partite per una squadra specifica.

        Args:
            team_id (int): ID della squadra.

        Returns:
            dict: Dati JSON delle partite della squadra o None se si supera il limite.
        """
        url = f"{self.BASE_URL}/teams/{team_id}/matches"
        return self._make_request(url, f"Dati delle partite per il team {team_id}")
