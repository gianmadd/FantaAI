-- Tabella per i paesi
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE,
    flag_url VARCHAR(255)
);

-- Tabella per i fusi orari
CREATE TABLE timezones (
    id SERIAL PRIMARY KEY,
    timezone VARCHAR(100) UNIQUE NOT NULL
);

-- Tabella per gli stadi
CREATE TABLE stadium (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    address VARCHAR(255),
    city VARCHAR(100),
    capacity INT,
    surface VARCHAR(50),
    image_url VARCHAR(255)
);

-- Tabella per i campionati
CREATE TABLE leagues (
    id INT PRIMARY KEY,
    country_id INT REFERENCES countries(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    logo_url VARCHAR(255)
);

-- Tabella per le squadre
CREATE TABLE teams (
    id INT PRIMARY KEY,
    stadium_id INT REFERENCES stadium(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10),
    country VARCHAR(100),
    founded INT,
    national BOOLEAN,
    logo_url VARCHAR(255)
);

-- Tabella per i giocatori
CREATE TABLE players (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    age INT,
    birth_date DATE,
    birth_place VARCHAR(100),
    birth_country VARCHAR(100),
    nationality VARCHAR(100),
    height VARCHAR(10),
    weight VARCHAR(10),
    injured BOOLEAN,
    photo_url VARCHAR(255)
);

-- Tabella per le stagioni
CREATE TABLE seasons (
    id SERIAL PRIMARY KEY,
    league_id INT REFERENCES leagues(id) ON DELETE CASCADE,
    year INT NOT NULL,
    start_date DATE,
    end_date DATE,
    current BOOLEAN DEFAULT FALSE,
    coverage_fixtures_events BOOLEAN,
    coverage_fixtures_lineups BOOLEAN,
    coverage_fixtures_statistics_fixtures BOOLEAN,
    coverage_fixtures_statistics_players BOOLEAN,
    coverage_standings BOOLEAN,
    coverage_players BOOLEAN,
    coverage_top_scorers BOOLEAN,
    coverage_top_assists BOOLEAN,
    coverage_top_cards BOOLEAN,
    coverage_injuries BOOLEAN,
    coverage_predictions BOOLEAN,
    coverage_odds BOOLEAN,
    UNIQUE(league_id, year)
);

-- Tabella per le statistiche delle squadre
CREATE TABLE team_statistics (
    id SERIAL PRIMARY KEY,
    team_id INT REFERENCES teams(id) ON DELETE CASCADE,
    league_id INT REFERENCES leagues(id) ON DELETE CASCADE,
    season_id INT REFERENCES seasons(id) ON DELETE CASCADE,  -- Modifica: usa season_id come chiave esterna
    form VARCHAR(100),
    fixtures_played_home INT,
    fixtures_played_away INT,
    fixtures_played_total INT,
    fixtures_wins_home INT,
    fixtures_wins_away INT,
    fixtures_wins_total INT,
    fixtures_draws_home INT,
    fixtures_draws_away INT,
    fixtures_draws_total INT,
    fixtures_loses_home INT,
    fixtures_loses_away INT,
    fixtures_loses_total INT,
    goals_for_home INT,
    goals_for_away INT,
    goals_for_total INT,
    goals_against_home INT,
    goals_against_away INT,
    goals_against_total INT,
    goals_for_average_home DECIMAL(3, 2),
    goals_for_average_away DECIMAL(3, 2),
    goals_for_average_total DECIMAL(3, 2),
    goals_against_average_home DECIMAL(3, 2),
    goals_against_average_away DECIMAL(3, 2),
    goals_against_average_total DECIMAL(3, 2),
    clean_sheet_home INT,
    clean_sheet_away INT,
    clean_sheet_total INT,
    failed_to_score_home INT,
    failed_to_score_away INT,
    failed_to_score_total INT,
    penalty_scored_total INT,
    penalty_missed_total INT,
    lineups JSONB,
    biggest_win_home VARCHAR(10),
    biggest_win_away VARCHAR(10),
    biggest_lose_home VARCHAR(10),
    biggest_lose_away VARCHAR(10),
    biggest_streak_wins INT,
    biggest_streak_draws INT,
    biggest_streak_loses INT
);

-- Tabella per le statistiche dei giocatori
CREATE TABLE player_statistics (
    id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(id) ON DELETE CASCADE,
    team_id INT REFERENCES teams(id) ON DELETE CASCADE,
    league_id INT REFERENCES leagues(id) ON DELETE CASCADE,
    season_id INT REFERENCES seasons(id) ON DELETE CASCADE,  -- Modifica: usa season_id come chiave esterna
    position VARCHAR(50),
    games_appearances INT,
    games_lineups INT,
    games_minutes INT,
    games_number INT,
    games_rating DECIMAL(3, 2),
    captain BOOLEAN,
    substitutes_in INT,
    substitutes_out INT,
    substitutes_bench INT,
    shots_total INT,
    shots_on INT,
    goals_total INT,
    goals_conceded INT,
    goals_assists INT,
    goals_saves INT,
    passes_total INT,
    passes_key INT,
    passes_accuracy INT,
    tackles_total INT,
    tackles_blocks INT,
    tackles_interceptions INT,
    duels_total INT,
    duels_won INT,
    dribbles_attempts INT,
    dribbles_success INT,
    dribbles_past INT,
    fouls_drawn INT,
    fouls_committed INT,
    cards_yellow INT,
    cards_yellowred INT,
    cards_red INT,
    penalty_won INT,
    penalty_committed INT,
    penalty_scored INT,
    penalty_missed INT,
    penalty_saved INT
);
