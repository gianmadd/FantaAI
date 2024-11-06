import logging
import os
import sys
import time

import requests

sys.path.insert(0, os.path.abspath(".."))

from data_provider.data_provider_base import DataProviderBase


class FootballDataOrgAPI(DataProviderBase):
    """
    Classe per l'integrazione con l'API di Football-Data.org.

    Questa classe consente di recuperare informazioni su squadre e partite
    per una competizione specifica tramite l'API di Football-Data.org.
    Gestisce automaticamente i limiti di chiamata (rate limiting) e fornisce
    un'interfaccia per richiamare dati di squadre e partite.

    Attributes:
        BASE_URL (str): L'URL base per l'API di Football-Data.org.
        RATE_LIMIT_SLEEP (int): Tempo in secondi per rispettare il rate limit in caso di errore 429.
        api_key (str): La chiave API per autenticazione.
        headers (dict): Headers HTTP per includere la chiave API nelle richieste.
    """

    BASE_URL = "https://api.football-data.org/v4"
    RATE_LIMIT_SLEEP = 60  # Pausa di 60 secondi per rate limit, costante della classe

    def __init__(self, api_key):
        """
        Inizializza il provider con la chiave API necessaria per autenticarsi.

        Args:
            api_key (str): La chiave API per autenticarsi con il servizio Football-Data.org.

        Raises:
            ValueError: Se la chiave API non è valida o mancante.
        """
        if not api_key:
            raise ValueError("La chiave API non è valida o mancante.")

        self.api_key = api_key
        self.headers = {
            "X-Auth-Token": self.api_key
        }  # Header di autenticazione per ogni richiesta

    def fetch_teams(self, competition_id):
        """
        Recupera tutte le squadre di una competizione specifica.

        Args:
            competition_id (str): ID della competizione (es. "SA" per Serie A).

        Returns:
            dict: Dati JSON contenenti le squadre per la competizione specificata,
                  oppure None in caso di errore.

        Raises:
            requests.exceptions.RequestException: Se si verifica un errore di connessione o di richiesta.
        """
        url = f"{self.BASE_URL}/competitions/{competition_id}/teams"
        return self._make_request(
            url, f"Dati delle squadre per competizione {competition_id}"
        )

    def fetch_team_matches(self, team_id):
        """
        Recupera le partite di una squadra specifica.

        Args:
            team_id (int): ID della squadra.

        Returns:
            dict: Dati JSON contenenti le partite della squadra specificata,
                  oppure None in caso di errore.

        Raises:
            requests.exceptions.RequestException: Se si verifica un errore di connessione o di richiesta.
        """
        url = f"{self.BASE_URL}/teams/{team_id}/matches"
        return self._make_request(url, f"Dati delle partite per il team {team_id}")

    def _make_request(self, url, log_context):
        """
        Effettua una singola richiesta API con gestione del rate limit e logging.

        Args:
            url (str): L'URL da richiamare.
            log_context (str): Descrizione per il logging, utilizzata per identificare la richiesta.

        Returns:
            dict: La risposta JSON della richiesta API se l'operazione è riuscita,
                  oppure None in caso di errore.

        Logs:
            Logga messaggi informativi e di errore basati sul contesto della richiesta e
            sul codice di risposta dell'API.

        Raises:
            requests.exceptions.RequestException: Se si verifica un errore di connessione.
        """
        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                logging.info(f"{log_context} recuperati con successo.")
                return response.json()

            elif response.status_code == 429:
                logging.warning(
                    f"Limite di chiamate raggiunto. Pausa di {self.RATE_LIMIT_SLEEP} secondi..."
                )
                time.sleep(self.RATE_LIMIT_SLEEP)

                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    logging.info(
                        f"{log_context} recuperati con successo dopo la pausa."
                    )
                    return response.json()
                else:
                    logging.error(
                        f"Errore nella chiamata API ({log_context}) dopo il rate limit - Status code: {response.status_code}"
                    )
                    return None

            else:
                logging.error(
                    f"Errore nella chiamata API ({log_context}) - Status code: {response.status_code}"
                )
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Errore di connessione durante {log_context}: {e}")
            return None
