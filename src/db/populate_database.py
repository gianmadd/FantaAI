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
        TRUNCATE TABLE stadium RESTART IDENTITY CASCADE;
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


def insert_stadium(db_connection, stadium_data):
    """
    Inserisce un record nella tabella 'stadium'.

    Args:
        db_connection (psycopg2.extensions.connection): La connessione al database.
        stadium_data (dict): Dati dello stadio con le chiavi:
            - id (int): ID dello stadio
            - name (str): Nome dello stadio
            - address (str): Indirizzo dello stadio
            - city (str): Città in cui si trova lo stadio
            - capacity (int): Capacità dello stadio
            - surface (str): Tipo di superficie dello stadio
            - image_url (str): URL dell'immagine dello stadio
    """
    query = """
        INSERT INTO stadium (id, name, address, city, capacity, surface, image_url)
        VALUES (%(id)s, %(name)s, %(address)s, %(city)s, %(capacity)s, %(surface)s, %(image_url)s)
        ON CONFLICT (id) DO NOTHING;
    """

    with db_connection.cursor() as cursor:
        cursor.execute(query, stadium_data)
        db_connection.commit()


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


def insert_teams(data, conn):
    with conn.cursor() as cur:
        for item in data:
            team = item["team"]
            venue = item["venue"]
            cur.execute(
                """
                INSERT INTO teams (id, name, code, country, founded, national, logo_url, stadium_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (
                    team["id"],
                    team["name"],
                    team.get("code"),
                    team["country"],
                    team["founded"],
                    team["national"],
                    team["logo"],
                    venue["id"],
                ),
            )
            # Inserisce i dati dello stadio associato alla squadra
            cur.execute(
                """
                INSERT INTO stadium (id, name, address, city, capacity, surface, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (
                    venue["id"],
                    venue["name"],
                    venue.get("address"),
                    venue.get("city"),
                    venue.get("capacity"),
                    venue.get("surface"),
                    venue.get("image"),
                ),
            )
    conn.commit()


def insert_players(data, conn):
    with conn.cursor() as cur:
        for item in data:
            player = item["player"]
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
                    player["id"],
                    player["name"],
                    player["firstname"],
                    player["lastname"],
                    player["age"],
                    player["birth"]["date"],
                    player["birth"].get("place"),
                    player["birth"].get("country"),
                    player["nationality"],
                    player["height"],
                    player["weight"],
                    player["injured"],
                    player["photo"],
                ),
            )
    conn.commit()


def insert_seasons(data, conn):
    with conn.cursor() as cur:
        for item in data:
            league_id = item["league"]["id"]
            for season in item["seasons"]:
                cur.execute(
                    """
                    INSERT INTO seasons (
                        league_id, year, start_date, end_date, current,
                        coverage_fixtures_events, coverage_fixtures_lineups, 
                        coverage_fixtures_statistics_fixtures, coverage_fixtures_statistics_players,
                        coverage_standings, coverage_players, coverage_top_scorers,
                        coverage_top_assists, coverage_top_cards, coverage_injuries,
                        coverage_predictions, coverage_odds
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (league_id, year) DO NOTHING;
                    """,
                    (
                        league_id,
                        season["year"],
                        season["start"],
                        season["end"],
                        season["current"],
                        season["coverage"]["fixtures"]["events"],
                        season["coverage"]["fixtures"]["lineups"],
                        season["coverage"]["fixtures"]["statistics_fixtures"],
                        season["coverage"]["fixtures"]["statistics_players"],
                        season["coverage"]["standings"],
                        season["coverage"]["players"],
                        season["coverage"]["top_scorers"],
                        season["coverage"]["top_assists"],
                        season["coverage"]["top_cards"],
                        season["coverage"]["injuries"],
                        season["coverage"]["predictions"],
                        season["coverage"]["odds"],
                    ),
                )
    conn.commit()


def insert_team_statistics(data, conn):
    with conn.cursor() as cur:
        for item in data:
            team = item["team"]
            league = item["league"]
            stats = item["statistics"]
            cur.execute(
                """
                INSERT INTO team_statistics (
                    team_id, league_id, season, form,
                    fixtures_played_home, fixtures_played_away, fixtures_played_total,
                    fixtures_wins_home, fixtures_wins_away, fixtures_wins_total,
                    fixtures_draws_home, fixtures_draws_away, fixtures_draws_total,
                    fixtures_loses_home, fixtures_loses_away, fixtures_loses_total,
                    goals_for_home, goals_for_away, goals_for_total,
                    goals_against_home, goals_against_away, goals_against_total,
                    goals_for_average_home, goals_for_average_away, goals_for_average_total,
                    goals_against_average_home, goals_against_average_away, goals_against_average_total,
                    clean_sheet_home, clean_sheet_away, clean_sheet_total,
                    failed_to_score_home, failed_to_score_away, failed_to_score_total,
                    penalty_scored_total, penalty_missed_total, lineups,
                    biggest_win_home, biggest_win_away, biggest_lose_home, biggest_lose_away,
                    biggest_streak_wins, biggest_streak_draws, biggest_streak_loses
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (team_id, league_id, season) DO NOTHING;
                """,
                (
                    team["id"],
                    league["id"],
                    league["season"],
                    stats["form"],
                    stats["fixtures"]["played"]["home"],
                    stats["fixtures"]["played"]["away"],
                    stats["fixtures"]["played"]["total"],
                    stats["fixtures"]["wins"]["home"],
                    stats["fixtures"]["wins"]["away"],
                    stats["fixtures"]["wins"]["total"],
                    stats["fixtures"]["draws"]["home"],
                    stats["fixtures"]["draws"]["away"],
                    stats["fixtures"]["draws"]["total"],
                    stats["fixtures"]["loses"]["home"],
                    stats["fixtures"]["loses"]["away"],
                    stats["fixtures"]["loses"]["total"],
                    stats["goals"]["for"]["home"],
                    stats["goals"]["for"]["away"],
                    stats["goals"]["for"]["total"],
                    stats["goals"]["against"]["home"],
                    stats["goals"]["against"]["away"],
                    stats["goals"]["against"]["total"],
                    stats["goals"]["for"]["average"]["home"],
                    stats["goals"]["for"]["average"]["away"],
                    stats["goals"]["for"]["average"]["total"],
                    stats["goals"]["against"]["average"]["home"],
                    stats["goals"]["against"]["average"]["away"],
                    stats["goals"]["against"]["average"]["total"],
                    stats["clean_sheet"]["home"],
                    stats["clean_sheet"]["away"],
                    stats["clean_sheet"]["total"],
                    stats["failed_to_score"]["home"],
                    stats["failed_to_score"]["away"],
                    stats["failed_to_score"]["total"],
                    stats["penalty"]["scored"]["total"],
                    stats["penalty"]["missed"]["total"],
                    json.dumps(stats.get("lineups", [])),
                    stats["biggest"]["wins"]["home"],
                    stats["biggest"]["wins"]["away"],
                    stats["biggest"]["loses"]["home"],
                    stats["biggest"]["loses"]["away"],
                    stats["biggest"]["streak"]["wins"],
                    stats["biggest"]["streak"]["draws"],
                    stats["biggest"]["streak"]["loses"],
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

        # insert_stadium(
        #     load_json_data(os.path.join(f"{DATA_PATH_GENERIC}", "stadium.json")), conn
        # )

        # DA RIVEREDERE TABELLA STADIUM (venue - sull'api si recuperano dal nome del paese)

        insert_leagues(
            load_json_data(os.path.join(f"{DATA_PATH_GENERIC}", "leagues.json")), conn
        )

        insert_seasons(
            load_json_data(os.path.join(f"{DATA_PATH_GENERIC}", "leagues.json")), conn
        )

        # insert_teams(load_json_data(os.path.join(f"{DATA_PATH_SPECIFIC}", "teams.json")), conn)
        # insert_players(load_json_data(os.path.join(f"{DATA_PATH_SPECIFIC}", "players.json")), conn)
        # insert_team_statistics(
        #     load_json_data(os.path.join(f"{DATA_PATH_SPECIFIC}", "teams_statistics.json")), conn
        # )
        print("Database popolato con successo.")


if __name__ == "__main__":
    populate_tables()
