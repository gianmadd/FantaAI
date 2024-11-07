import contextlib
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Carica le variabili di ambiente dal file .env
load_dotenv("config/.env")

# Assegna le variabili di ambiente
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def get_database_url():
    """
    Costruisce e restituisce la stringa di connessione al database.

    Returns:
        str: Stringa di connessione al database.

    Raises:
        ValueError: Se una delle variabili di ambiente richieste è assente.
    """
    # Verifica che tutte le variabili di ambiente siano caricate correttamente
    missing_vars = [
        var
        for var, value in {
            "DB_NAME": DB_NAME,
            "DB_USER": DB_USER,
            "DB_PASSWORD": DB_PASSWORD,
            "DB_HOST": DB_HOST,
            "DB_PORT": DB_PORT,
        }.items()
        if not value
    ]

    if missing_vars:
        raise ValueError(f"Variabili di ambiente mancanti: {', '.join(missing_vars)}")

    return (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


# Configura la stringa di connessione
DATABASE_URL = get_database_url()

# Crea l'engine di SQLAlchemy
engine = create_engine(DATABASE_URL)

# Gestione delle sessioni
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base per definire le tabelle
Base = declarative_base()


@contextlib.contextmanager
# Trasforma la funzione in un generatore compatibile con il contesto with
def get_db():
    """
    Genera una sessione del database, utilizzabile con il costrutto 'with'.

    Yields:
        Session: Una sessione del database per interazioni sicure.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
