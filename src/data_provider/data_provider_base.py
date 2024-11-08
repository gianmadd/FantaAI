from abc import ABC, abstractmethod


class DataProviderBase(ABC):
    """
    Classe astratta base per i provider di dati delle squadre e delle partite.

    Questa classe fornisce l'interfaccia per i metodi che devono essere implementati
    da ogni provider di dati, per consentire l'accesso ai dati delle squadre e
    delle partite tramite metodi specifici.
    """
    
    @abstractmethod
    def fetch_static_data(self, endpoint):
        pass

    
    @abstractmethod
    def fetch_teams_from_league_season(self, league_id, season):
        pass

    @abstractmethod
    def fetch_players_from_team_season(self, team, season):
        pass