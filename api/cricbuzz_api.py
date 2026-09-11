import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST")
BASE_URL = f"https://{API_HOST}"

HEADERS = {
    "x-rapidapi-host": API_HOST,
    "x-rapidapi-key": API_KEY
}

def get_recent_matches():
    """Fetch the list of recent matches across all match types."""
    url = f"{BASE_URL}/matches/v1/recent"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_match_info(match_id):
    """Fetch metadata (venue, teams, series) for a single match."""
    url = f"{BASE_URL}/mcenter/v1/{match_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_match_scorecard(match_id):
    """Fetch full batting/bowling scorecard for a single match."""
    url = f"{BASE_URL}/mcenter/v1/{match_id}/hscard"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()