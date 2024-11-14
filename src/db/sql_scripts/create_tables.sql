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

-- Tabella per i campionati
CREATE TABLE leagues (
    id INT PRIMARY KEY,
    country_id INT REFERENCES countries(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    logo_url VARCHAR(255)
);

-------------------------------------------------------------------------------------------

-- Tabella per le squadre con riferimento al campionato
CREATE TABLE teams (
    id INT PRIMARY KEY,
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


-- Statistiche delle squadre con meno campi per focalizzarsi sulle metriche più rilevanti
CREATE TABLE team_statistics (
    id SERIAL PRIMARY KEY,
    team_id INT REFERENCES teams(id) ON DELETE CASCADE,
    season INT,
    league_id INT REFERENCES leagues(id) ON DELETE SET NULL,
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
    fixtures_losses_home INT,
    fixtures_losses_away INT,
    fixtures_losses_total INT,
    goals_for_home INT,
    goals_for_away INT,
    goals_for_total INT,
    goals_against_home INT,
    goals_against_away INT,
    goals_against_total INT,
    clean_sheets_home INT,
    clean_sheets_away INT,
    clean_sheets_total INT,
    failed_to_score_home INT,
    failed_to_score_away INT,
    failed_to_score_total INT,
    penalty_scored INT,
    penalty_missed INT
);


-- Statistiche dei giocatori con un set ridotto di campi
CREATE TABLE player_statistics (
    id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(id) ON DELETE CASCADE,
    team_id INT REFERENCES teams(id) ON DELETE CASCADE,
    season INT,
    league_id INT REFERENCES leagues(id) ON DELETE SET NULL,
    position VARCHAR(50),
    games_appearances INT,
    games_lineups INT,
    games_minutes INT,
    rating DECIMAL(3, 2),
    captain BOOLEAN,
    substitutes_in INT,
    substitutes_out INT,
    substitutes_bench INT,
    shots_total INT,
    shots_on INT,
    goals_total INT,
    goals_assists INT,
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
    fouls_drawn INT,
    fouls_committed INT,
    cards_yellow INT,
    cards_yellowred INT,
    cards_red INT,
    penalties_won INT,
    penalties_committed INT,
    penalties_scored INT,
    penalties_missed INT,
    penalties_saved INT
);

