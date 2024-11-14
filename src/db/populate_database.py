import json
import os

from database import get_db
from dotenv import load_dotenv

load_dotenv("../../config/.env")

PROVIDER_NAME = os.getenv("PROVIDER_NAME")

# Percorso dei file JSON puliti
DATA_PATH_GENERIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/cleaned/generics")
DATA_PATH_SPECIFIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/cleaned/specifics")


def load_json_data(filepath):
    """Carica i dati JSON da un file specificato."""
    with open(filepath, "r") as f:
        return json.load(f)["response"]


def truncate_tables(conn):

    truncate_tables_sql = """
        TRUNCATE TABLE player_statistics RESTART IDENTITY CASCADE;
        TRUNCATE TABLE team_statistics RESTART IDENTITY CASCADE;
        TRUNCATE TABLE players RESTART IDENTITY CASCADE;
        TRUNCATE TABLE teams RESTART IDENTITY CASCADE;
        TRUNCATE TABLE seasons RESTART IDENTITY CASCADE;
        TRUNCATE TABLE leagues RESTART IDENTITY CASCADE;
        TRUNCATE TABLE timezones RESTART IDENTITY CASCADE;
        TRUNCATE TABLE countries RESTART IDENTITY CASCADE;
    """

    with conn.cursor() as cur:
        cur.execute(truncate_tables_sql)
    conn.commit()
    print("Tutte le tabelle sono state svuotate.")


def insert_countries(data, conn):
    with conn.cursor() as cur:
        for item in data:
            cur.execute(
                """
                INSERT INTO countries (name, code, flag_url)
                VALUES (%s, %s, %s)
                ON CONFLICT (code) DO NOTHING;
                """,
                (item["name"], item.get("code"), item.get("flag")),
            )
    conn.commit()


def insert_timezones(data, conn):
    with conn.cursor() as cur:
        for tz in data:
            cur.execute(
                """
                INSERT INTO timezones (timezone)
                VALUES (%s)
                ON CONFLICT (timezone) DO NOTHING;
                """,
                (tz,),
            )
    conn.commit()


def insert_leagues(data, conn):
    with conn.cursor() as cur:
        for item in data:
            cur.execute(
                """
                INSERT INTO leagues (id, country_id, name, type, logo_url)
                VALUES (%s, (SELECT id FROM countries WHERE name = %s), %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (
                    item["league"]["id"],
                    item["country"]["name"],
                    item["league"]["name"],
                    item["league"]["type"],
                    item["league"].get("logo"),
                ),
            )
    conn.commit()





def populate_tables():
    with get_db() as conn:

        truncate_tables(conn)

        insert_countries(
            load_json_data(os.path.join(f"{DATA_PATH_GENERIC}", "countries.json")), conn
        )

        insert_timezones(
            load_json_data(os.path.join(f"{DATA_PATH_GENERIC}", "timezone.json")), conn
        )

        insert_leagues(
            load_json_data(os.path.join(f"{DATA_PATH_GENERIC}", "leagues.json")), conn
        )

        print("Database popolato con successo.")


if __name__ == "__main__":
    populate_tables()
