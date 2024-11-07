import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from data_provider.api_football_data_org_provider import FootballDataOrgAPI
from data_provider.api_football_rapid_provider import FootballRapidAPI


def get_data_provider(provider_name, api_key):
    """
    Crea e restituisce un'istanza del provider di dati specificato.

    Questa funzione accetta il nome del provider e la chiave API per autenticarsi.
    In base al nome del provider, restituisce un'istanza della classe appropriata
    per interagire con l'API del provider scelto.

    Args:
        provider_name (str): Il nome del provider di dati desiderato.
                             Esempio: "api_football_data_org".
        api_key (str): La chiave API per autenticarsi con il provider specificato.

    Returns:
        DataProviderBase: Un'istanza del provider di dati richiesto che implementa
                          `DataProviderBase`.

    Raises:
        ValueError: Se il nome del provider specificato non è supportato.

    Example:
        provider = get_data_provider("api_football_data_org", "your_api_key")
    """
    if provider_name == "api_football_data_org":
        return FootballDataOrgAPI(api_key, counter_dir="config")
    elif provider_name == "api_football_rapid":
        return FootballRapidAPI(api_key, counter_dir="config")
    else:
        raise ValueError(f"Provider {provider_name} non supportato.")
