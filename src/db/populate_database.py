import json
import os

import pandas as pd
from database import get_db
from dotenv import load_dotenv

load_dotenv("../../config/.env")

PROVIDER_NAME = os.getenv("PROVIDER_NAME")

# Percorso dei file JSON puliti
DATA_PATH_GENERIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/cleaned/generics")
DATA_PATH_SPECIFIC = os.path.abspath(f"../../data/{PROVIDER_NAME}/cleaned/specifics")

team_ids = {
    "LAZIO": "487",
    "SASSUOLO": "488",
    "MILAN": "489",
    "CAGLIARI": "490",
    "NAPOLI": "492",
    "UDINESE": "494",
    "GENOA": "495",
    "JUVENTUS": "496",
    "ROMA": "497",
    "ATALANTA": "499",
    "BOLOGNA": "500",
    "FIORENTINA": "502",
    "TORINO": "503",
    "VERONA": "504",
    "INTER": "505",
    "EMPOLI": "511",
    "FROSINONE": "512",
    "SALERNITANA": "514",
    "LECCE": "867",
    "MONZA": "1579",
}

seasons = ["2019", "2020", "2021", "2022", "2023"]
SEASON = "2023"


def load_json_data(field_name, filepath):
    """Carica i dati JSON da un file specificato."""
    with open(filepath, "r") as f:
        return json.load(f)[field_name]


def truncate_tables(conn):

    truncate_tables_sql = """
        TRUNCATE TABLE player_statistics RESTART IDENTITY CASCADE;
        TRUNCATE TABLE team_statistics RESTART IDENTITY CASCADE;
        TRUNCATE TABLE players RESTART IDENTITY CASCADE;
        TRUNCATE TABLE teams RESTART IDENTITY CASCADE;
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
    print("Tabella 'countries' popolata con successo.")


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
    print("Tabella 'timezone' popolata con successo.")


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
    print("Tabella 'leagues' popolata con successo.")


def insert_teams(data, conn):
    """
    Inserisce i dati delle squadre nella tabella 'teams'.

    Args:
        data (list): Lista di dizionari contenenti i dati delle squadre.
        conn: Connessione al database.
    """

    with conn.cursor() as cur:
        for item in data:
            cur.execute(
                """
                INSERT INTO teams (
                    id, name, code, country, founded, national, logo_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (
                    item["team_id"],
                    item["team_name"],
                    item["team_code"],
                    item["team_country"],
                    item["team_founded"],
                    item["team_national"],
                    item["team_logo"],
                ),
            )
    conn.commit()
    print("Tabella 'teams' popolata con successo.")


def insert_players(data, conn):
    """
    Inserisce i dati dei giocatori nella tabella 'players'.

    Args:
        data (dict): Dizionario contenente i dati dei giocatori.
        conn: Connessione al database.
    """
    with conn.cursor() as cur:
        for item in data:  # Itera sulla lista di giocatori
            cur.execute(
                """
                INSERT INTO players (
                    id, name, firstname, lastname, age, birth_date, birth_place,
                    birth_country, nationality, height, weight, injured, photo_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (
                    item["player_id"],
                    item["player_name"],
                    item.get("player_firstname"),
                    item.get("player_lastname"),
                    item.get("player_age"),
                    item.get("player_birth_date"),
                    item.get("player_birth_place"),
                    item.get("player_birth_country"),
                    item.get("player_nationality"),
                    item.get("player_height"),
                    item.get("player_weight"),
                    item.get("player_injured", False),
                    item.get("player_photo"),
                ),
            )
    conn.commit()
    print("Tabella 'players' popolata con successo.")


def insert_player_statistics(data, conn):
    """
    Inserisce i dati delle statistiche dei giocatori nella tabella 'player_statistics'.

    Args:
        data (dict): Dizionario contenente i dati delle statistiche dei giocatori.
        conn: Connessione al database.
    """

    with conn.cursor() as cur:
        for item in data:  # Itera sulla lista di giocatori
            cur.execute(
                """
                INSERT INTO player_statistics (
                    player_id, team_id, season, league_id, position, games_appearances, games_lineups, games_minutes, rating, captain,
                    substitutes_in, substitutes_out, substitutes_bench, shots_total, shots_on, goals_total,
                    goals_assists, passes_total, passes_key, passes_accuracy,
                    tackles_total, tackles_blocks, tackles_interceptions, duels_total, duels_won,
                    dribbles_attempts, dribbles_success, fouls_drawn, fouls_committed,
                    cards_yellow, cards_yellowred, cards_red, penalties_won, penalties_committed,
                    penalties_scored, penalties_missed, penalties_saved
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
                """,
                (
                    item.get("player_id"),
                    item.get("statistics_team_id"),
                    item.get("statistics_league_season"),
                    item.get("statistics_league_id"),
                    item.get("statistics_games_position"),
                    item.get("statistics_games_appearences"),
                    item.get("statistics_games_lineups"),
                    item.get("statistics_games_minutes"),
                    item.get("statistics_games_rating"),
                    item.get("statistics_games_captain"),
                    item.get("statistics_substitutes_in"),
                    item.get("statistics_substitutes_out"),
                    item.get("statistics_substitutes_bench"),
                    item.get("statistics_shots_total"),
                    item.get("statistics_shots_on"),
                    item.get("statistics_goals_total"),
                    item.get("statistics_goals_assists"),
                    item.get("statistics_passes_total"),
                    item.get("statistics_passes_key"),
                    item.get("statistics_passes_accuracy"),
                    item.get("statistics_tackles_total"),
                    item.get("statistics_tackles_blocks"),
                    item.get("statistics_tackles_interceptions"),
                    item.get("statistics_duels_total"),
                    item.get("statistics_duels_won"),
                    item.get("statistics_dribbles_attempts"),
                    item.get("statistics_dribbles_success"),
                    item.get("statistics_fouls_drawn"),
                    item.get("statistics_fouls_committed"),
                    item.get("statistics_cards_yellow"),
                    item.get("statistics_cards_yellowred"),
                    item.get("statistics_cards_red"),
                    item.get("statistics_penalty_won"),
                    item.get("statistics_penalty_committed"),
                    item.get("statistics_penalty_scored"),
                    item.get("statistics_penalty_missed"),
                    item.get("statistics_penalty_saved"),
                ),
            )
    conn.commit()
    print("Tabella 'player_statistics' popolata con successo.")


def populate_tables():
    with get_db() as conn:

        truncate_tables(conn)

        insert_countries(
            load_json_data(
                "countries", os.path.join(f"{DATA_PATH_GENERIC}", "countries.json")
            ),
            conn,
        )

        insert_timezones(
            load_json_data(
                "timezone", os.path.join(f"{DATA_PATH_GENERIC}", "timezone.json")
            ),
            conn,
        )

        insert_leagues(
            load_json_data(
                "leagues", os.path.join(f"{DATA_PATH_GENERIC}", "leagues.json")
            ),
            conn,
        )

        for season in seasons:
            insert_teams(
                load_json_data(
                    "teams",
                    os.path.join(f"{DATA_PATH_SPECIFIC}/teams", f"135_{season}.json"),
                ),
                conn,
            )

        ################################################## TEMPORANEO. USARE CICLO QUANDO I DATI SONO RECUPERATI
        insert_players(
            load_json_data(
                "players",
                os.path.join(
                    f"{DATA_PATH_SPECIFIC}/players/{season}", f"487_{SEASON}.json"
                ),
            ),
            conn,
        )

        insert_player_statistics(
            load_json_data(
                "players",
                os.path.join(
                    f"{DATA_PATH_SPECIFIC}/players/{season}", f"487_{SEASON}.json"
                ),
            ),
            conn,
        )
        #####################################################

        # for season in seasons:

        #     for team_id in team_ids.values():

        #         insert_players(
        #             load_json_data(
        #                 "players",
        #                 os.path.join(
        #                     f"{DATA_PATH_SPECIFIC}/players/{season}",
        #                     f"{team_id}_{season}.json",
        #                 ),
        #             ),
        #             conn,
        #         )

        #         insert_player_statistics(
        #             load_json_data(
        #                 "players",
        #                 os.path.join(
        #                     f"{DATA_PATH_SPECIFIC}/players/{season}",
        #                     f"{team_id}_{season}.json",
        #                 ),
        #             ),
        #             conn,
        #         )

        print("Database popolato con successo.")


if __name__ == "__main__":

    populate_tables()
    print("Dati inseriti con successo.")
