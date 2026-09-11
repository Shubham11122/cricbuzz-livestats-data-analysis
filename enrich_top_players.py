import os
import time
import requests
from dotenv import load_dotenv
from database.db_connection import get_connection

load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST")
headers = {"x-rapidapi-host": API_HOST, "x-rapidapi-key": API_KEY}

def get_top_players(conn, limit=40):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.player_id, p.full_name,
               COALESCE(bat.total_runs, 0) + COALESCE(bowl.total_wickets, 0) * 20 AS impact_score
        FROM players p
        LEFT JOIN (SELECT player_id, SUM(runs_scored) AS total_runs FROM batting_performance GROUP BY player_id) bat
            ON p.player_id = bat.player_id
        LEFT JOIN (SELECT player_id, SUM(wickets_taken) AS total_wickets FROM bowling_performance GROUP BY player_id) bowl
            ON p.player_id = bowl.player_id
        WHERE p.country IS NULL
        ORDER BY impact_score DESC
        LIMIT ?
    """, (limit,))
    return cursor.fetchall()

def fetch_profile(player_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def run_enrichment(limit=40):
    conn = get_connection()
    cursor = conn.cursor()

    players = get_top_players(conn, limit)
    print(f"Enriching {len(players)} players...\n")

    for i, (player_id, name, score) in enumerate(players, start=1):
        print(f"[{i}/{len(players)}] {name}...")
        try:
            data = fetch_profile(player_id)
            country = data.get("intlTeam")
            role = data.get("role")
            bat_style = data.get("bat")
            bowl_style = data.get("bowl")

            cursor.execute(
                "UPDATE players SET country = ?, playing_role = ?, batting_style = ?, bowling_style = ? WHERE player_id = ?",
                (country, role, bat_style, bowl_style, player_id)
            )
            conn.commit()
        except Exception as e:
            print(f"  Failed: {e}")
        time.sleep(1)

    conn.close()
    print("\nEnrichment complete.")

if __name__ == "__main__":
    run_enrichment(limit=40)