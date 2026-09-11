import re
from api.cricbuzz_api import get_recent_matches
from utils.preprocessing import extract_matches_list
from database.db_connection import get_connection

def parse_status(status_text, team1_name, team2_name):
    """Extracts winner_team_name, margin, victory_type from a status string.
    Returns (winner_name, margin, victory_type) or (None, None, None) if not parseable
    (e.g. 'Match drawn', 'No result', 'Match tied')."""
    match = re.match(r"^(.*?) won by (\d+)\s*(runs?|wkts?)", status_text)
    if not match:
        return None, None, None
    winner_name = match.group(1).strip()
    margin = int(match.group(2))
    victory_type = "runs" if "run" in match.group(3) else "wickets"
    return winner_name, margin, victory_type

def run_backfill():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT match_id FROM matches")
    existing_ids = set(row[0] for row in cursor.fetchall())

    print("Fetching recent matches list (1 API call)...")
    data = get_recent_matches()
    all_matches = extract_matches_list(data, limit=500)  # grab as many as the response has

    updated = 0
    for m in all_matches:
        match_id = m["matchId"]
        if match_id not in existing_ids:
            continue

        status = m.get("status", "")
        team1_name = m["team1"]["teamName"]
        team2_name = m["team2"]["teamName"]
        team1_id = m["team1"]["teamId"]
        team2_id = m["team2"]["teamId"]

        winner_name, margin, victory_type = parse_status(status, team1_name, team2_name)
        if winner_name is None:
            continue

        if winner_name == team1_name:
            winner_id = team1_id
        elif winner_name == team2_name:
            winner_id = team2_id
        else:
            continue  # couldn't confidently match winner name to a team

        cursor.execute(
            "UPDATE matches SET winner_team_id = ?, victory_margin = ?, victory_type = ? WHERE match_id = ?",
            (winner_id, margin, victory_type, match_id)
        )
        updated += 1

    conn.commit()
    conn.close()
    print(f"Backfilled winner/margin data for {updated} matches.")

if __name__ == "__main__":
    run_backfill()