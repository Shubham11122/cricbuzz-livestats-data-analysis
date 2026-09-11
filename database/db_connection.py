import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cricbuzz.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def get_connection():
    """Returns a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    """Creates all tables from schema.sql if they don't exist yet."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        schema_script = f.read()
    conn.executescript(schema_script)
    conn.commit()
    conn.close()
    print("Database initialized successfully at:", DB_PATH)

if __name__ == "__main__":
    initialize_database()


def insert_team(conn, team_id, team_name):
    conn.execute(
        "INSERT OR IGNORE INTO teams (team_id, team_name, country) VALUES (?, ?, ?)",
        (team_id, team_name, team_name)
    )

def insert_venue(conn, venue_id, venue_name, city, country):
    conn.execute(
        "INSERT OR IGNORE INTO venues (venue_id, venue_name, city, country, capacity) VALUES (?, ?, ?, ?, ?)",
        (venue_id, venue_name, city, country, None)
    )

def insert_series(conn, series_id, series_name):
    conn.execute(
        "INSERT OR IGNORE INTO series (series_id, series_name, host_country, match_type, start_date, total_matches) VALUES (?, ?, ?, ?, ?, ?)",
        (series_id, series_name, None, None, None, None)
    )

def insert_match(conn, match_id, series_id, match_desc, match_format, team1_id, team2_id, venue_id, match_date):
    conn.execute(
        """INSERT OR IGNORE INTO matches
           (match_id, series_id, match_desc, match_format, team1_id, team2_id, venue_id, match_date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (match_id, series_id, match_desc, match_format, team1_id, team2_id, venue_id, match_date)
    )

def insert_batting_performance(conn, match_id, player_id, innings_no, batting_position,
                                 runs_scored, balls_faced, fours, sixes, strike_rate, is_out):
    conn.execute(
        """INSERT INTO batting_performance
           (match_id, player_id, innings_no, batting_position, runs_scored, balls_faced, fours, sixes, strike_rate, is_out)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (match_id, player_id, innings_no, batting_position, runs_scored, balls_faced, fours, sixes, strike_rate, is_out)
    )

def insert_bowling_performance(conn, match_id, player_id, innings_no,
                                 overs_bowled, runs_conceded, wickets_taken, economy_rate):
    conn.execute(
        """INSERT INTO bowling_performance
           (match_id, player_id, innings_no, overs_bowled, runs_conceded, wickets_taken, economy_rate)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (match_id, player_id, innings_no, overs_bowled, runs_conceded, wickets_taken, economy_rate)
    )

def insert_player(conn, player_id, full_name):
    conn.execute(
        "INSERT OR IGNORE INTO players (player_id, full_name, country, playing_role, batting_style, bowling_style) VALUES (?, ?, ?, ?, ?, ?)",
        (player_id, full_name, None, None, None, None)
    )