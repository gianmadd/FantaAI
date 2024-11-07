import os
import sys

sys.path.insert(0, os.path.abspath("../"))

from sqlalchemy import text

from src.db.database import engine, get_db

if __name__ == "__main__":

    print("Verifica della connessione al database...")

    # # METODO 1 - engine
    # # Per connessioni dirette e semplici verifiche di connessione.
    # try:
    #     # Crea una connessione temporanea usando engine
    #     with engine.connect() as connection:
    #         result = connection.execute(text("SELECT 1926"))  # Esegue una semplice query di test
    #         numero = result.scalar()
    #         print("Connessione al database riuscita!")
    #         print(f"Numero : {numero}")
    # except Exception as e:
    #     print(f"Errore di connessione al database: {e}")
    # finally:
    #     engine.dispose()  # Chiude l'engine e rilascia le risorse

    # METODO 2 - SessionLocal()
    # Gestione sicura delle sessioni, utile nelle operazioni CRUD dove servono transazioni.
    try:
        # Usa get_db() per ottenere una sessione
        with get_db() as db:
            # Esegue la query per ottenere la versione di PostgreSQL
            result = db.execute(text("SELECT 1926"))
            numero = result.scalar()  # Recupera il risultato singolo
            print("Connessione al database riuscita!")
            print(f"Numero: {numero}")
    except Exception as e:
        print(f"Errore di connessione al database: {e}")
