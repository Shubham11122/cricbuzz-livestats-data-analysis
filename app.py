import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

from database.db_connection import get_connection
from sql.queries import QUERIES
from api.cricbuzz_api import get_recent_matches
from utils.preprocessing import extract_matches_list

st.set_page_config(page_title="Cricbuzz LiveStats", layout="wide", page_icon="🏏")

# ---------- GLOBAL STYLE ----------
def inject_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        h1, h2, h3 { font-family: 'Fraunces', serif !important; font-weight: 600 !important; color: #F2EFE6 !important; }

        .hero { padding: 2.5rem 0 1.5rem 0; border-bottom: 1px solid #2A3B30; margin-bottom: 2rem; }
        .hero-label { color: #C9A227; font-size: 0.85rem; letter-spacing: 0.04em; margin-bottom: 0.4rem; }
        .hero-title { font-family: 'Fraunces', serif !important; font-weight: 700 !important; font-size: 2.8rem !important; color: #F2EFE6 !important; line-height: 1.15 !important; margin: 0 !important; }
        .hero-sub { color: #8FA396 !important; font-size: 1.1rem !important; margin-top: 0.6rem !important; max-width: 680px; }
        .section-header { font-family: 'Fraunces', serif !important; font-size: 1.5rem !important; font-weight: 600 !important; color: #F2EFE6 !important; margin: 1.8rem 0 0.8rem 0 !important; }
        .info-card ul { padding-left: 1.3rem; }
        .info-card li { margin-bottom: 0.4rem; }

        .stat-box { background-color: #16241C; border: 1px solid #2A3B30; border-radius: 6px; padding: 1.4rem 1.6rem; }
        .stat-number { font-family: 'Fraunces', serif; font-size: 2.4rem; font-weight: 700; color: #C9A227; line-height: 1; }
        .stat-label { color: #8FA396; font-size: 0.9rem; margin-top: 0.4rem; }

        .match-card { background-color: #16241C; border: 1px solid #2A3B30; border-left: 3px solid #C9A227; border-radius: 4px; padding: 1.1rem 1.4rem; margin-bottom: 0.9rem; }
        .match-teams { font-family: 'Fraunces', serif; font-size: 1.2rem; color: #F2EFE6; font-weight: 600; }
        .match-meta { color: #8FA396; font-size: 0.85rem; margin-top: 0.3rem; }
        .match-status { color: #C9A227; font-size: 0.9rem; margin-top: 0.5rem; }

        .info-card { background-color: #16241C; border: 1px solid #2A3B30; border-radius: 6px; padding: 1.5rem 1.8rem; margin-bottom: 1.2rem; }
        .info-card h4 { font-family: 'Fraunces', serif; color: #C9A227; margin-top: 0; }
        .info-card p, .info-card li { color: #DCE3DE; line-height: 1.6; }

        .phase-badge {
            display: inline-block; background-color: #C9A227; color: #0F1B14;
            font-weight: 600; font-size: 0.8rem; padding: 0.2rem 0.6rem;
            border-radius: 3px; margin-right: 0.6rem;
        }

        section[data-testid="stSidebar"] { background-color: #0B140F; border-right: 1px solid #2A3B30; }
        [data-testid="stDataFrame"] { border: 1px solid #2A3B30; border-radius: 4px; }
        </style>
    """, unsafe_allow_html=True)

def hero(label, title, subtitle):
    html = f"""<div class="hero"><div class="hero-label">{label}</div><p class="hero-title">{title}</p><p class="hero-sub">{subtitle}</p></div>"""
    st.markdown(html, unsafe_allow_html=True)

def stat_box(number, label):
    st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{number}</div>
            <div class="stat-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

def info_card(title_text, body_html):
    clean_body = " ".join(line.strip() for line in body_html.strip().split("\n"))
    html = f'<div class="info-card"><h4>{title_text}</h4>{clean_body}</div>'
    st.markdown(html, unsafe_allow_html=True)

def section_header(text):
    st.markdown(f'<p class="section-header">{text}</p>', unsafe_allow_html=True)

# ---------- PROJECT OVERVIEW ----------
def show_project_overview():
    hero("PROJECT BRIEF", "Cricbuzz LiveStats", "Real-time cricket insights and SQL-based analytics, built from the ground up on live Cricbuzz API data.")

    col1, col2 = st.columns(2)
    with col1:
        info_card("Business Problem", """
            <p>Cricket data from live match feeds arrives as raw, deeply nested JSON —
            useful for a single glance, but not queryable, comparable, or analyzable.
            This project turns that feed into structured, relational data that can
            support real statistical analysis.</p>
        """)
        info_card("Data Source", """
            <p>All data is pulled from the <b>Cricbuzz Cricket API</b> via RapidAPI —
            covering recent international, league, domestic, and women's matches.
            The current database holds <b>55 real matches</b> across Test, ODI, and
            T20 formats, ingested directly from live endpoints, not sample or
            mock data.</p>
        """)
    with col2:
        info_card("Objective", """
            <p>Build a single Streamlit application with five functional areas —
            Home, Live Match, Player Stats, SQL Analytics, and CRUD — backed by a
            database-agnostic SQL layer, capable of running on SQLite for
            deployment.</p>
        """)
        info_card("Tech Stack", """
            <ul>
                <li><b>Python</b> — requests, pandas for ingestion and cleaning</li>
                <li><b>SQLite</b> — normalized relational schema, 8 tables</li>
                <li><b>Streamlit</b> — single-file multi-page dashboard</li>
                <li><b>Plotly</b> — interactive charts and visualizations</li>
            </ul>
        """)

    info_card("Known Data Limitations", """
        <p>Some fields are not available from the Cricbuzz endpoints used —
        player nationality/role, venue capacity, venue country, and toss
        information are structurally absent from the source data and are
        documented rather than faked. SQL questions depending on these fields
        are noted accordingly in the SQL Analytics section.</p>
    """)

# ---------- PROJECT APPROACH ----------
def show_project_approach():
    hero("METHODOLOGY", "Project approach", "How the raw API feed became this dashboard, stage by stage.")

    stages = [
        ("STAGE 1", "API Integration", "A dedicated module (api/cricbuzz_api.py) handles all communication with Cricbuzz — fetching recent matches, match metadata, and full scorecards, with error handling for failed or rate-limited requests."),
        ("STAGE 2", "Preprocessing & Cleaning", "Nested JSON responses are flattened into flat rows using pandas-style logic — converting string fields (strike rate, economy) to numbers, deriving is_out from dismissal text, and validating data before it reaches the database."),
        ("STAGE 3", "Database Design & Loading", "An 8-table normalized SQLite schema (teams, venues, series, players, matches, batting/bowling/fielding performance) stores the cleaned data, with UNIQUE constraints preventing duplicate rows on re-ingestion."),
        ("STAGE 4", "SQL Analytics", "20 SQL queries — ranging from basic filters to window functions and CTEs — run directly against the database, covering player performance, team records, partnerships, and time-based trends."),
        ("STAGE 5", "Dashboard & Visualization", "A single-file Streamlit app presents live API data, database-driven leaderboards, interactive Plotly charts, and full CRUD operations on player records."),
    ]

    for badge, title, desc in stages:
        st.markdown(f"""
            <div class="info-card">
                <span class="phase-badge">{badge}</span>
                <span style="font-family:'Fraunces',serif; font-size:1.15rem; color:#F2EFE6;">{title}</span>
                <p style="margin-top:0.6rem;">{desc}</p>
            </div>
        """, unsafe_allow_html=True)

# ---------- HOME ----------
def show_home():
    hero("CRICBUZZ LIVESTATS", "Real cricket data, queried properly.", "Live match feeds and SQL analyses built on a database populated directly from the Cricbuzz API.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM matches")
    match_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM players")
    player_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM batting_performance")
    batting_count = cursor.fetchone()[0]
    conn.close()

    col1, col2, col3 = st.columns(3)
    with col1: stat_box(match_count, "Matches tracked")
    with col2: stat_box(player_count, "Players in database")
    with col3: stat_box(batting_count, "Batting innings recorded")

    st.write("")
    st.markdown("#### Where to go")
    st.markdown("""
    - **Live Match** — current match feed, pulled directly from the Cricbuzz API
    - **Player Stats** — top run scorers and wicket takers from the local database
    - **Analytics Overview** — key metrics and leaderboards at a glance
    - **Visualizations** — interactive, filterable charts
    - **SQL Analytics** — 20 SQL questions spanning basic filters to window functions and CTEs
    - **CRUD** — add, update, and remove player records
    """)

# ---------- LIVE MATCH ----------
def show_live_match():
    hero("LIVE FEED", "Recent matches", "Pulled directly from the Cricbuzz API.")
    if st.button("Refresh"):
        st.cache_data.clear()

    @st.cache_data(ttl=300)
    def fetch_matches():
        data = get_recent_matches()
        return extract_matches_list(data, limit=20)

    try:
        matches = fetch_matches()
        for m in matches:
            venue = m.get("venueInfo", {})
            st.markdown(f"""
                <div class="match-card">
                    <div class="match-teams">{m['team1']['teamName']} vs {m['team2']['teamName']}</div>
                    <div class="match-meta">{m.get('seriesName', '')} · {m.get('matchDesc', '')} · {venue.get('ground', '')}, {venue.get('city', '')}</div>
                    <div class="match-status">{m.get('status', 'N/A')}</div>
                </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not fetch live data: {e}")

# ---------- TOP PLAYER STATS ----------
def show_player_stats():
    hero("LEADERBOARD", "Top player stats", "Aggregated from every match in the local database.")
    conn = get_connection()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("Top Run Scorers")
        df_runs = pd.read_sql_query("""
            SELECT p.full_name AS "Player", SUM(b.runs_scored) AS "Runs"
            FROM batting_performance b JOIN players p ON b.player_id = p.player_id
            GROUP BY p.player_id ORDER BY "Runs" DESC LIMIT 10
        """, conn)
        st.dataframe(df_runs, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("Top Wicket Takers")
        df_wickets = pd.read_sql_query("""
            SELECT p.full_name AS "Player", SUM(bo.wickets_taken) AS "Wickets"
            FROM bowling_performance bo JOIN players p ON bo.player_id = p.player_id
            GROUP BY p.player_id ORDER BY "Wickets" DESC LIMIT 10
        """, conn)
        st.dataframe(df_wickets, use_container_width=True, hide_index=True)
    conn.close()

# ---------- ANALYTICS OVERVIEW ----------
def show_analytics_overview():
    hero("OVERVIEW", "Analytics overview", "Key metrics and leaderboards across the full dataset.")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM matches"); total_matches = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM players"); total_players = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT team_id) FROM teams"); total_teams = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(runs_scored) FROM batting_performance"); total_runs = cursor.fetchone()[0] or 0

    col1, col2, col3, col4 = st.columns(4)
    with col1: stat_box(total_matches, "Total matches")
    with col2: stat_box(total_players, "Total players")
    with col3: stat_box(total_teams, "Teams")
    with col4: stat_box(f"{total_runs:,}", "Total runs scored")

    st.write("")
    st.markdown("##### Team performance")
    df_teams = pd.read_sql_query("""
        SELECT t.team_name AS "Team", COUNT(DISTINCT m.match_id) AS "Matches",
               COALESCE(SUM(b.runs_scored), 0) AS "Total Runs",
               ROUND(COALESCE(AVG(b.runs_scored), 0), 1) AS "Avg Runs/Innings"
        FROM teams t
        LEFT JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id)
        LEFT JOIN batting_performance b ON b.match_id = m.match_id
        GROUP BY t.team_id HAVING "Matches" > 0 ORDER BY "Total Runs" DESC LIMIT 15
    """, conn)
    st.dataframe(df_teams, use_container_width=True, hide_index=True)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown("##### Top batsmen")
        df_bat = pd.read_sql_query("""
            SELECT p.full_name AS "Player", SUM(b.runs_scored) AS "Runs"
            FROM batting_performance b JOIN players p ON b.player_id = p.player_id
            GROUP BY p.player_id ORDER BY "Runs" DESC LIMIT 8
        """, conn)
        st.dataframe(df_bat, use_container_width=True, hide_index=True)
    with col6:
        st.markdown("##### Top bowlers")
        df_bowl = pd.read_sql_query("""
            SELECT p.full_name AS "Player", SUM(bo.wickets_taken) AS "Wickets"
            FROM bowling_performance bo JOIN players p ON bo.player_id = p.player_id
            GROUP BY p.player_id ORDER BY "Wickets" DESC LIMIT 8
        """, conn)
        st.dataframe(df_bowl, use_container_width=True, hide_index=True)
    conn.close()

# ---------- VISUALIZATIONS ----------
def show_visualizations():
    hero("EXPLORE", "Visualizations", "Interactive charts — filter by format and series.")
    conn = get_connection()
    formats_df = pd.read_sql_query("SELECT DISTINCT match_format FROM matches", conn)
    series_df = pd.read_sql_query("SELECT DISTINCT series_name FROM series", conn)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_formats = st.multiselect("Format", formats_df["match_format"].tolist(), default=formats_df["match_format"].tolist())
    with col_f2:
        selected_series = st.multiselect("Series", series_df["series_name"].tolist(), default=series_df["series_name"].tolist())

    if not selected_formats or not selected_series:
        st.warning("Select at least one format and one series.")
        conn.close()
        return

    format_list = "', '".join(selected_formats)
    series_list = "', '".join([s.replace("'", "''") for s in selected_series])

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        df_runs = pd.read_sql_query(f"""
            SELECT p.full_name, SUM(b.runs_scored) as total_runs
            FROM batting_performance b
            JOIN players p ON b.player_id = p.player_id
            JOIN matches m ON b.match_id = m.match_id
            JOIN series s ON m.series_id = s.series_id
            WHERE m.match_format IN ('{format_list}') AND s.series_name IN ('{series_list}')
            GROUP BY p.player_id ORDER BY total_runs DESC LIMIT 10
        """, conn)
        if not df_runs.empty:
            fig = px.bar(df_runs, x="total_runs", y="full_name", orientation="h", title="Top Run Scorers",
                         color="total_runs", color_continuous_scale="Sunsetdark")
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, paper_bgcolor="#16241C", plot_bgcolor="#16241C", font_color="#F2EFE6")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for this filter combination.")
    with col2:
        df_formats = pd.read_sql_query(f"""
            SELECT m.match_format, COUNT(*) as cnt FROM matches m JOIN series s ON m.series_id = s.series_id
            WHERE m.match_format IN ('{format_list}') AND s.series_name IN ('{series_list}') GROUP BY m.match_format
        """, conn)
        if not df_formats.empty:
            fig = px.pie(df_formats, names="match_format", values="cnt", hole=0.5, title="Format Split",
                         color_discrete_sequence=["#C9A227", "#3E7C59", "#8FA396"])
            fig.update_layout(paper_bgcolor="#16241C", font_color="#F2EFE6")
            st.plotly_chart(fig, use_container_width=True)
        st.write("")
    col3, col4 = st.columns(2)
    with col3:
        df_sr = pd.read_sql_query(f"""
            SELECT b.strike_rate, m.match_format
            FROM batting_performance b
            JOIN matches m ON b.match_id = m.match_id
            JOIN series s ON m.series_id = s.series_id
            WHERE m.match_format IN ('{format_list}') AND s.series_name IN ('{series_list}')
            AND b.balls_faced >= 5
        """, conn)
        if not df_sr.empty:
            fig = px.box(df_sr, x="match_format", y="strike_rate", color="match_format", title="Strike Rate by Format",
                         color_discrete_sequence=["#C9A227", "#3E7C59", "#8FA396"])
            fig.update_layout(paper_bgcolor="#16241C", plot_bgcolor="#16241C", font_color="#F2EFE6", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        df_wkts = pd.read_sql_query(f"""
            SELECT p.full_name, SUM(bo.wickets_taken) as total_wickets
            FROM bowling_performance bo
            JOIN players p ON bo.player_id = p.player_id
            JOIN matches m ON bo.match_id = m.match_id
            JOIN series s ON m.series_id = s.series_id
            WHERE m.match_format IN ('{format_list}') AND s.series_name IN ('{series_list}')
            GROUP BY p.player_id ORDER BY total_wickets DESC LIMIT 10
        """, conn)
        if not df_wkts.empty:
            fig = px.bar(df_wkts, x="total_wickets", y="full_name", orientation="h", title="Top Wicket Takers",
                         color="total_wickets", color_continuous_scale="Tealgrn")
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, paper_bgcolor="#16241C", plot_bgcolor="#16241C", font_color="#F2EFE6")
            st.plotly_chart(fig, use_container_width=True)

    df_sun = pd.read_sql_query(f"""
        SELECT s.series_name, m.match_format, v.venue_name, COUNT(*) as cnt
        FROM matches m
        JOIN series s ON m.series_id = s.series_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE m.match_format IN ('{format_list}') AND s.series_name IN ('{series_list}')
        GROUP BY s.series_id, m.match_format, v.venue_id
    """, conn)
    if not df_sun.empty:
        fig = px.sunburst(df_sun, path=["series_name", "match_format", "venue_name"], values="cnt",
                           title="Series → Format → Venue Breakdown", color="cnt", color_continuous_scale="Sunset")
        fig.update_layout(paper_bgcolor="#16241C", font_color="#F2EFE6", margin=dict(t=50, l=0, r=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    df_time = pd.read_sql_query(f"""
        SELECT m.match_date FROM matches m JOIN series s ON m.series_id = s.series_id
        WHERE m.match_format IN ('{format_list}') AND s.series_name IN ('{series_list}') AND m.match_date IS NOT NULL
    """, conn)
    if not df_time.empty:
        df_time["match_date"] = pd.to_datetime(df_time["match_date"])
        df_grouped = df_time.groupby(df_time["match_date"].dt.date).size().reset_index(name="matches")
        fig = px.line(df_grouped, x="match_date", y="matches", markers=True, title="Matches Over Time", color_discrete_sequence=["#C9A227"])
        fig.update_layout(paper_bgcolor="#16241C", plot_bgcolor="#16241C", font_color="#F2EFE6")
        st.plotly_chart(fig, use_container_width=True)
    conn.close()

# ---------- SQL ANALYTICS ----------
def show_sql_analytics():
    hero("ANALYTICS", "SQL queries", "25 questions — run directly against the database.")
    question_options = {f"Q{qid}: {q['title']}": qid for qid, q in QUERIES.items()}
    selected_label = st.selectbox("Choose a question", list(question_options.keys()))
    qid = question_options[selected_label]
    sql = QUERIES[qid]["sql"]
    with st.expander("View SQL"):
        st.code(sql, language="sql")
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn)
        if df.empty:
            st.info("No rows returned with the current dataset volume or fields.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Query failed: {e}")
    conn.close()

# ---------- CRUD ----------
def show_crud():
    hero("MANAGE DATA", "Player records", "Create, update, and remove entries — and fill in profile details the API doesn't provide.")

    conn = get_connection()
    cursor = conn.cursor()

    action = st.radio("Action", ["View", "Add", "Update", "Delete"], horizontal=True)
    st.write("")

    if action == "View":
        df = pd.read_sql_query("""
            SELECT p.player_id,
                   p.full_name AS "Player",
                   COALESCE(p.country, 'Not set') AS "Country",
                   COALESCE(p.playing_role, 'Not set') AS "Role",
                   COALESCE(bat.total_runs, 0) AS "Runs",
                   COALESCE(bowl.total_wickets, 0) AS "Wickets",
                   COALESCE(bat.matches_batted, 0) + COALESCE(bowl.matches_bowled, 0) AS "Matches (approx)"
            FROM players p
            LEFT JOIN (
                SELECT player_id, SUM(runs_scored) AS total_runs, COUNT(DISTINCT match_id) AS matches_batted
                FROM batting_performance GROUP BY player_id
            ) bat ON p.player_id = bat.player_id
            LEFT JOIN (
                SELECT player_id, SUM(wickets_taken) AS total_wickets, COUNT(DISTINCT match_id) AS matches_bowled
                FROM bowling_performance GROUP BY player_id
            ) bowl ON p.player_id = bowl.player_id
            ORDER BY "Runs" DESC
            LIMIT 50
        """, conn)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("Country and Role show 'Not set' where the Cricbuzz API doesn't provide profile data — use **Update** below to fill these in manually.")

    elif action == "Add":
        with st.form("add_player_form"):
            player_id = st.number_input("Player ID", min_value=1, step=1)
            full_name = st.text_input("Full Name")
            country = st.text_input("Country (optional)")
            role = st.text_input("Playing Role (optional)")
            submitted = st.form_submit_button("Add player")
            if submitted:
                try:
                    cursor.execute(
                        "INSERT INTO players (player_id, full_name, country, playing_role) VALUES (?, ?, ?, ?)",
                        (player_id, full_name, country or None, role or None)
                    )
                    conn.commit()
                    st.success(f"Added {full_name}")
                except Exception as e:
                    st.error(f"Failed to add: {e}")

    elif action == "Update":
        df = pd.read_sql_query(
            "SELECT player_id, full_name, country, playing_role, batting_style, bowling_style FROM players ORDER BY full_name",
            conn
        )
        player_map = dict(zip(df["full_name"], df["player_id"]))
        selected_name = st.selectbox("Select player", list(player_map.keys()))

        current = df[df["player_id"] == player_map[selected_name]].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            new_country = st.text_input("Country", value=current["country"] or "")
            new_role = st.text_input("Playing Role", value=current["playing_role"] or "")
        with col2:
            new_batting_style = st.text_input("Batting Style", value=current["batting_style"] or "")
            new_bowling_style = st.text_input("Bowling Style", value=current["bowling_style"] or "")

        if st.button("Save changes"):
            cursor.execute(
                "UPDATE players SET country = ?, playing_role = ?, batting_style = ?, bowling_style = ? WHERE player_id = ?",
                (new_country or None, new_role or None, new_batting_style or None, new_bowling_style or None, player_map[selected_name])
            )
            conn.commit()
            st.success(f"Updated {selected_name}")

    elif action == "Delete":
        df = pd.read_sql_query("SELECT player_id, full_name FROM players ORDER BY full_name", conn)
        player_map = dict(zip(df["full_name"], df["player_id"]))
        selected_name = st.selectbox("Select player", list(player_map.keys()))
        if st.button("Delete", type="primary"):
            cursor.execute("DELETE FROM players WHERE player_id = ?", (player_map[selected_name],))
            conn.commit()
            st.success(f"Deleted {selected_name}")

    conn.close()

# ---------- SIDEBAR NAVIGATION ----------
inject_css()

with st.sidebar:
    st.markdown("""
        <div style="text-align:center; padding: 1rem 0 0.5rem 0;">
            <div style="font-size: 2.8rem;">🏏</div>
            <div style="font-family:'Fraunces',serif; font-size:1.3rem; font-weight:700; color:#F2EFE6;">Cricbuzz LiveStats</div>
            <div style="color:#8FA396; font-size:0.8rem; margin-top:0.2rem;">Real-time cricket analytics</div>
        </div>
    """, unsafe_allow_html=True)

    page = option_menu(
        menu_title=None,
        options=["Project Overview", "Project Approach", "Home", "Live Match", "Player Stats",
                 "Analytics Overview", "Visualizations", "SQL Analytics", "CRUD"],
        icons=["info-circle", "diagram-3", "house", "broadcast", "bar-chart-line",
               "graph-up-arrow", "sliders", "database", "gear"],
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "#0B140F"},
            "icon": {"color": "#C9A227", "font-size": "16px"},
            "nav-link": {"font-size": "14px", "color": "#DCE3DE", "text-align": "left", "margin": "2px 0", "border-radius": "4px"},
            "nav-link-selected": {"background-color": "#16241C", "color": "#F2EFE6", "border-left": "3px solid #C9A227"},
        }
    )

if page == "Project Overview":
    show_project_overview()
elif page == "Project Approach":
    show_project_approach()
elif page == "Home":
    show_home()
elif page == "Live Match":
    show_live_match()
elif page == "Player Stats":
    show_player_stats()
elif page == "Analytics Overview":
    show_analytics_overview()
elif page == "Visualizations":
    show_visualizations()
elif page == "SQL Analytics":
    show_sql_analytics()
elif page == "CRUD":
    show_crud()