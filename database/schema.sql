CREATE TABLE IF NOT EXISTS teams (
    team_id      INTEGER PRIMARY KEY,
    team_name    TEXT NOT NULL,
    country      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS venues (
    venue_id     INTEGER PRIMARY KEY,
    venue_name   TEXT NOT NULL,
    city         TEXT,
    country      TEXT,
    capacity     INTEGER
);

CREATE TABLE IF NOT EXISTS series (
    series_id       INTEGER PRIMARY KEY,
    series_name     TEXT NOT NULL,
    host_country    TEXT,
    match_type      TEXT,
    start_date      DATE,
    total_matches   INTEGER
);

CREATE TABLE IF NOT EXISTS players (
    player_id       INTEGER PRIMARY KEY,
    full_name       TEXT NOT NULL,
    country         TEXT,
    playing_role    TEXT,
    batting_style   TEXT,
    bowling_style   TEXT
);

CREATE TABLE IF NOT EXISTS matches (
    match_id         INTEGER PRIMARY KEY,
    series_id        INTEGER REFERENCES series(series_id),
    match_desc       TEXT,
    match_format     TEXT,
    team1_id         INTEGER REFERENCES teams(team_id),
    team2_id         INTEGER REFERENCES teams(team_id),
    venue_id         INTEGER REFERENCES venues(venue_id),
    match_date       DATE,
    toss_winner_id   INTEGER REFERENCES teams(team_id),
    toss_decision    TEXT,
    winner_team_id   INTEGER REFERENCES teams(team_id),
    victory_margin   INTEGER,
    victory_type     TEXT
);

CREATE TABLE IF NOT EXISTS batting_performance (
    batting_id       INTEGER PRIMARY KEY,
    match_id         INTEGER REFERENCES matches(match_id),
    player_id        INTEGER REFERENCES players(player_id),
    innings_no       INTEGER,
    batting_position INTEGER,
    runs_scored      INTEGER,
    balls_faced      INTEGER,
    fours            INTEGER,
    sixes            INTEGER,
    strike_rate      REAL,
    is_out           INTEGER,
    UNIQUE(match_id, player_id, innings_no, batting_position)
);

CREATE TABLE IF NOT EXISTS bowling_performance (
    bowling_id       INTEGER PRIMARY KEY,
    match_id         INTEGER REFERENCES matches(match_id),
    player_id        INTEGER REFERENCES players(player_id),
    innings_no       INTEGER,
    overs_bowled     REAL,
    runs_conceded    INTEGER,
    wickets_taken    INTEGER,
    economy_rate     REAL,
    UNIQUE(match_id, player_id, innings_no)
);

CREATE TABLE IF NOT EXISTS fielding_performance (
    fielding_id      INTEGER PRIMARY KEY,
    match_id         INTEGER REFERENCES matches(match_id),
    player_id        INTEGER REFERENCES players(player_id),
    catches          INTEGER,
    stumpings        INTEGER
);