import time
from api.cricbuzz_api import get_match_scorecard
from database.db_connection import (
    get_connection,
    insert_player,
    insert_batting_performance,
    insert_bowling_performance
)

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def ingest_batsman(conn, match_id, innings_no, position, batsman):
    player_id = batsman["id"]
    insert_player(conn, player_id, batsman.get("name"))

    outdec = batsman.get("outdec", "") or ""
    is_out = 0 if (outdec == "" or outdec.lower() == "not out") else 1

    insert_batting_performance(
        conn,
        match_id,
        player_id,
        innings_no,
        position,
        batsman.get("runs", 0),
        batsman.get("balls", 0),
        batsman.get("fours", 0),
        batsman.get("sixes", 0),
        safe_float(batsman.get("strkrate")),
        is_out
    )

def ingest_bowler(conn, match_id, innings_no, bowler):
    player_id = bowler["id"]
    insert_player(conn, player_id, bowler.get("name"))

    insert_bowling_performance(
        conn,
        match_id,
        player_id,
        innings_no,
        safe_float(bowler.get("overs")),
        bowler.get("runs", 0),
        bowler.get("wickets", 0),
        safe_float(bowler.get("economy"))
    )

def ingest_scorecard_for_match(conn, match_id):
    data = get_match_scorecard(match_id)
    innings_list = data.get("scorecard", [])

    for innings in innings_list:
        innings_no = innings.get("inningsid")

        for position, batsman in enumerate(innings.get("batsman", []), start=1):
            ingest_batsman(conn, match_id, innings_no, position, batsman)

        for bowler in innings.get("bowler", []):
            ingest_bowler(conn, match_id, innings_no, bowler)

def run_scorecard_ingestion():
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute("SELECT match_id FROM matches")
    match_ids = [row[0] for row in cursor.fetchall()]

    print(f"Ingesting scorecards for {len(match_ids)} matches...\n")

    for i, match_id in enumerate(match_ids, start=1):
        print(f"[{i}/{len(match_ids)}] Match {match_id}...")
        try:
            ingest_scorecard_for_match(conn, match_id)
            conn.commit()
        except Exception as e:
            print(f"  Failed on match {match_id}: {e}")
        time.sleep(0.5)  # small pause to avoid hammering the rate limit

    conn.close()
    print("\nScorecard ingestion complete.")

if __name__ == "__main__":
    run_scorecard_ingestion()