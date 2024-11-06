from abc import ABC, abstractmethod


class DataProviderBase(ABC):
    """
    Classe astratta base per i provider di dati delle squadre e delle partite.

    Questa classe fornisce l'interfaccia per i metodi che devono essere implementati
    da ogni provider di dati, per consentire l'accesso ai dati delle squadre e
    delle partite tramite metodi specifici.
    """

    @abstractmethod
    def fetch_teams(self, competition_id):
        """
        Recupera le squadre per una competizione specificata.

        Args:
            competition_id (str): ID della competizione di cui recuperare le squadre
                                  (ad esempio, "SA" per la Serie A).

        Returns:
            dict: Un dizionario contenente i dati delle squadre, solitamente in formato JSON.
                  La struttura del dizionario varia in base al provider di dati specifico.

        Raises:
            Exception: Può sollevare eccezioni specifiche se l'implementazione concreta
                       incontra problemi durante il recupero dei dati.
        """
        pass

    @abstractmethod
    def fetch_team_matches(self, team_id):
        """
        Recupera le partite per una squadra specificata.

        Args:
            team_id (int): ID della squadra di cui recuperare le partite.

        Returns:
            dict: Un dizionario contenente i dati delle partite della squadra specificata,
                  in genere in formato JSON. La struttura del dizionario varia in base
                  al provider di dati specifico.

        Raises:
            Exception: Può sollevare eccezioni specifiche se l'implementazione concreta
                       incontra problemi durante il recupero dei dati.
        """
        pass
