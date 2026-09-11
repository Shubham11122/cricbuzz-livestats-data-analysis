from datetime import datetime

from api.cricbuzz_api import get_recent_matches, get_match_info
from utils.preprocessing import extract_matches_list
from database.db_connection import (
    get_connection,
    insert_team,
    insert_venue,
    insert_series,
    insert_match
)

def convert_epoch_ms(epoch_ms):
    """Converts epoch milliseconds (string or int) to a YYYY-MM-DD date string."""
    if epoch_ms is None:
        return None
    return datetime.fromtimestamp(int(epoch_ms) / 1000).strftime("%Y-%m-%d")

def ingest_match_metadata(conn, match_info):
    """Takes one matchInfo dict (from the recent-matches list) and inserts
    its team, venue, series, and match rows into the database."""

    match_id = match_info["matchId"]
    series_id = match_info["seriesId"]
    series_name = match_info["seriesName"]
    match_desc = match_info.get("matchDesc")
    match_format = match_info.get("matchFormat")

    team1 = match_info["team1"]
    team2 = match_info["team2"]
    venue = match_info.get("venueInfo", {})

    insert_series(conn, series_id, series_name)
    insert_team(conn, team1["teamId"], team1["teamName"])
    insert_team(conn, team2["teamId"], team2["teamName"])

    venue_id = venue.get("id")
    if venue_id:
        insert_venue(
            conn,
            venue_id,
            venue.get("ground"),
            venue.get("city"),
            venue.get("country")  # not always present in this endpoint
        )

    match_date = convert_epoch_ms(match_info.get("startDate"))

    insert_match(
        conn,
        match_id,
        series_id,
        match_desc,
        match_format,
        team1["teamId"],
        team2["teamId"],
        venue_id,
        match_date
    )

def run_ingestion(limit=55):
    conn = get_connection()

    print("Fetching recent matches list...")
    data = get_recent_matches()
    matches = extract_matches_list(data, limit=limit)
    print(f"Found {len(matches)} matches to ingest.\n")

    for i, match_info in enumerate(matches, start=1):
        match_id = match_info["matchId"]
        print(f"[{i}/{len(matches)}] Ingesting match {match_id}...")
        try:
            ingest_match_metadata(conn, match_info)
            conn.commit()
        except Exception as e:
            print(f"  Failed on match {match_id}: {e}")

    conn.close()
    print("\nIngestion complete.")

if __name__ == "__main__":
    run_ingestion(limit=55)