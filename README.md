# 🏏 Cricbuzz LiveStats

A full-stack cricket analytics dashboard that pulls live and recent match data from the Cricbuzz API, stores it in a structured relational database, and presents it through an interactive Streamlit application — covering live match tracking, player statistics, 25 SQL analytics questions, and full CRUD operations.

**Live Demo:** (https://cricbuzz-livestats-data-analysis-project.streamlit.app/)

---

## 📋 Table of Contents

- [Business Problem](#business-problem)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Database Schema](#database-schema)
- [SQL Analytics](#sql-analytics)
- [Data Pipeline](#data-pipeline)
- [Known Data Limitations](#known-data-limitations)
- [Testing](#testing)
- [Deployment](#deployment)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Business Problem

Cricket data from live match feeds arrives as raw, deeply nested JSON — useful for a single glance, but not queryable, comparable, or analyzable at scale. This project builds a complete pipeline that turns that live feed into structured, relational data, supporting real SQL-based analysis and interactive visualization.

## Features

- **📡 Live Match** — current match data pulled directly from the Cricbuzz API in real time
- **📊 Player Stats** — top run scorers and wicket takers, aggregated from the local database
- **📈 Analytics Overview** — key metrics, team performance, and leaderboards at a glance
- **🔎 Visualizations** — interactive, filterable Plotly charts (bar, donut, box plot, sunburst, and more)
- **🗄️ SQL Analytics** — 25 SQL questions spanning basic filters through window functions and CTEs
- **🛠️ CRUD** — create, read, update, and delete player records directly from the UI
- **📓 EDA Notebook** — a documented Jupyter notebook (`eda.ipynb`) with 18+ exploratory visualizations

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Data Ingestion | `requests`, `python-dotenv` |
| Data Processing | `pandas` |
| Database | SQLite |
| Web App | Streamlit, `streamlit-option-menu` |
| Visualization | Plotly, Matplotlib |
| Data Source | Cricbuzz Cricket API (via RapidAPI) |

## Project Structure
cricbuzz-livestats/
├── app.py # Main Streamlit application
├── config.py # Environment/config loader
├── requirements.txt # Python dependencies
├── pytest.ini # Pytest configuration
├── README.md
│
├── api/
│ └── cricbuzz_api.py # Cricbuzz API integration layer
│
├── database/
│ ├── db_connection.py # SQLite connector + CRUD helper functions
│ └── schema.sql # Database schema (8 tables)
│
├── sql/
│ └── queries.py # 25 SQL analytics questions
│
├── utils/
│ └── preprocessing.py # JSON flattening, cleaning, extraction logic
│
├── data/
│ └── cricbuzz.db # Pre-populated SQLite database (55 matches)
│
├── .streamlit/
│ └── config.toml # Custom dashboard theme
│
├── tests/
│ └── test_db_connection.py # Basic database layer tests
│
├── eda.ipynb # Exploratory data analysis notebook
│
├── ingest.py # One-time script: fetch match metadata
├── ingest_scorecards.py # One-time script: fetch scorecards
├── backfill_winners.py # One-time script: backfill winner/margin data
└── enrich_top_players.py # One-time script: enrich player profiles


## Installation & Setup

### Prerequisites
- Python 3.10+
- A [RapidAPI](https://rapidapi.com) account subscribed to the [Cricbuzz Cricket API](https://rapidapi.com/cricketapilive/api/cricbuzz-cricket)

### 1. Clone the repository
```bash
git clone https://github.com/Shubham11122/cricbuzz-livestats.git
cd cricbuzz-livestats
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

## Environment Variables
Create a `.env` file in the project root:
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=cricbuzz-cricket.p.rapidapi.com


> **Note:** Never commit `.env` to version control. When deploying on Streamlit Community Cloud, add these same values under **App Settings → Secrets** instead.

## Running the App

The database (`data/cricbuzz.db`) comes pre-populated with 55 real matches, so you can run the app immediately:

```bash
streamlit run app.py
```

### Re-running the data pipeline (optional)
If you want to fetch fresh data instead of using the bundled database:
```bash
python database/db_connection.py     # Initialize schema
python ingest.py                     # Fetch match metadata
python ingest_scorecards.py          # Fetch full scorecards
python backfill_winners.py           # Backfill winner/margin data
python enrich_top_players.py         # Enrich top players' profiles
```
⚠️ These scripts call the live Cricbuzz API and consume your RapidAPI quota — only re-run if needed.

## Database Schema

8 normalized tables: `teams`, `venues`, `series`, `players`, `matches`, `batting_performance`, `bowling_performance`, `fielding_performance` — linked by foreign keys, with `UNIQUE` constraints preventing duplicate rows on re-ingestion.

## SQL Analytics

25 questions covering:
- **Basic** — filters, top-N rankings, format comparisons
- **Intermediate** — partnerships (self-joins), venue-based aggregation, cross-format analysis
- **Advanced** — window functions (`ROW_NUMBER`, `RANK`), CTEs, manually computed standard deviation, time-series trends

Some thresholds (e.g. "20+ matches," "5+ head-to-head meetings") were scaled down from typical career-level benchmarks to match this project's 55-match dataset size, noted directly in each query's title within the app.

## Data Pipeline


> **Note:** Never commit `.env` to version control. When deploying on Streamlit Community Cloud, add these same values under **App Settings → Secrets** instead.

## Running the App

The database (`data/cricbuzz.db`) comes pre-populated with 55 real matches, so you can run the app immediately:

```bash
streamlit run app.py
```

### Re-running the data pipeline (optional)
If you want to fetch fresh data instead of using the bundled database:
```bash
python database/db_connection.py     # Initialize schema
python ingest.py                     # Fetch match metadata
python ingest_scorecards.py          # Fetch full scorecards
python backfill_winners.py           # Backfill winner/margin data
python enrich_top_players.py         # Enrich top players' profiles
```
⚠️ These scripts call the live Cricbuzz API and consume your RapidAPI quota — only re-run if needed.

## Database Schema

8 normalized tables: `teams`, `venues`, `series`, `players`, `matches`, `batting_performance`, `bowling_performance`, `fielding_performance` — linked by foreign keys, with `UNIQUE` constraints preventing duplicate rows on re-ingestion.

## SQL Analytics

25 questions covering:
- **Basic** — filters, top-N rankings, format comparisons
- **Intermediate** — partnerships (self-joins), venue-based aggregation, cross-format analysis
- **Advanced** — window functions (`ROW_NUMBER`, `RANK`), CTEs, manually computed standard deviation, time-series trends

Some thresholds (e.g. "20+ matches," "5+ head-to-head meetings") were scaled down from typical career-level benchmarks to match this project's 55-match dataset size, noted directly in each query's title within the app.

## Data Pipeline

Cricbuzz API → Fetch (requests) → Clean/Flatten (pandas-style) → Validate → SQLite → SQL Analytics → Streamlit


Full methodology is documented in-app under **Project Approach**.

## Known Data Limitations

The Cricbuzz endpoints used do not provide:
- Venue capacity and venue country
- Toss winner/decision
- Player nationality, role, and batting/bowling style for most players (top players by impact are enriched separately via a per-player profile API call)

These gaps are handled transparently — affected fields show "Not set" rather than fabricated values, and dependent SQL queries are adjusted or noted accordingly.

## Testing

Basic tests validate the database layer:
```bash
pytest tests/
```

## Deployment

Deployed on **Streamlit Community Cloud**, connected directly to this GitHub repository. API credentials are managed via Streamlit's Secrets manager rather than a committed `.env` file.

## Future Improvements

- Expand the ingested dataset beyond 55 matches for more statistically robust threshold-based queries
- Add toss and venue-country data via additional API endpoints
- Full player profile enrichment (currently limited to top players by impact score)
- Add automated scheduled re-ingestion for live data freshness

## Author

**Shubham**
GitHub: [Shubham11122](https://github.com/Shubham11122)






