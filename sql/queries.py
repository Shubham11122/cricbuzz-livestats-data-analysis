QUERIES = {
    1: {"title": "Matches in the last 30 days", "sql": """
        SELECT m.match_desc, t1.team_name AS team1, t2.team_name AS team2,
               v.venue_name, v.city, m.match_date
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE m.match_date >= date('now', '-30 day')
        ORDER BY m.match_date DESC;
    """},
    2: {"title": "Top 10 ODI run scorers", "sql": """
        SELECT p.full_name, SUM(b.runs_scored) AS total_runs,
               ROUND(SUM(b.runs_scored) * 1.0 / NULLIF(SUM(b.is_out), 0), 2) AS batting_average,
               SUM(CASE WHEN b.runs_scored >= 100 THEN 1 ELSE 0 END) AS centuries
        FROM batting_performance b
        JOIN players p ON b.player_id = p.player_id
        JOIN matches m ON b.match_id = m.match_id
        WHERE m.match_format = 'ODI'
        GROUP BY p.player_id ORDER BY total_runs DESC LIMIT 10;
    """},
    3: {"title": "Matches won per team", "sql": """
        SELECT t.team_name, COUNT(*) AS total_wins
        FROM matches m JOIN teams t ON m.winner_team_id = t.team_id
        GROUP BY t.team_id ORDER BY total_wins DESC;
    """},
    4: {"title": "Highest individual score per format", "sql": """
        SELECT m.match_format, MAX(b.runs_scored) AS highest_score
        FROM batting_performance b JOIN matches m ON b.match_id = m.match_id
        GROUP BY m.match_format;
    """},
    5: {"title": "Matches played per series", "sql": """
        SELECT s.series_name, COUNT(m.match_id) AS matches_played,
               COUNT(DISTINCT m.match_format) AS formats_played
        FROM series s JOIN matches m ON s.series_id = m.series_id
        GROUP BY s.series_id ORDER BY matches_played DESC;
    """},
    6: {"title": "All-rounders: 200+ runs AND 5+ wickets (thresholds scaled to sample size)", "sql": """
        SELECT p.full_name, SUM(b.runs_scored) AS total_runs, SUM(bo.wickets_taken) AS total_wickets
        FROM players p
        JOIN batting_performance b ON p.player_id = b.player_id
        JOIN bowling_performance bo ON p.player_id = bo.player_id
        GROUP BY p.player_id
        HAVING SUM(b.runs_scored) >= 200 AND SUM(bo.wickets_taken) >= 5
        ORDER BY total_runs DESC;
    """},
    7: {"title": "Last 20 completed matches", "sql": """
        SELECT m.match_desc, t1.team_name AS team1, t2.team_name AS team2,
               tw.team_name AS winner, m.victory_margin, m.victory_type, v.venue_name
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        LEFT JOIN teams tw ON m.winner_team_id = tw.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        ORDER BY m.match_date DESC LIMIT 20;
    """},
    8: {"title": "Cross-format performance comparison", "sql": """
        SELECT p.full_name,
               SUM(CASE WHEN m.match_format = 'TEST' THEN b.runs_scored ELSE 0 END) AS test_runs,
               SUM(CASE WHEN m.match_format = 'ODI' THEN b.runs_scored ELSE 0 END) AS odi_runs,
               SUM(CASE WHEN m.match_format = 'T20' THEN b.runs_scored ELSE 0 END) AS t20_runs,
               ROUND(SUM(b.runs_scored) * 1.0 / NULLIF(SUM(b.is_out), 0), 2) AS overall_average,
               COUNT(DISTINCT m.match_format) AS formats_played
        FROM batting_performance b
        JOIN players p ON b.player_id = p.player_id
        JOIN matches m ON b.match_id = m.match_id
        GROUP BY p.player_id HAVING COUNT(DISTINCT m.match_format) >= 2;
    """},
    9: {"title": "Partnerships (consecutive batsmen) totaling 100+ runs", "sql": """
        SELECT b1.match_id, b1.innings_no, p1.full_name AS batsman1, p2.full_name AS batsman2,
               (b1.runs_scored + b2.runs_scored) AS combined_runs
        FROM batting_performance b1
        JOIN batting_performance b2 ON b1.match_id = b2.match_id AND b1.innings_no = b2.innings_no
            AND b2.batting_position = b1.batting_position + 1
        JOIN players p1 ON b1.player_id = p1.player_id
        JOIN players p2 ON b2.player_id = p2.player_id
        WHERE (b1.runs_scored + b2.runs_scored) >= 100
        ORDER BY combined_runs DESC;
    """},
    10: {"title": "Bowling performance by venue", "sql": """
        SELECT p.full_name, v.venue_name, ROUND(AVG(bo.economy_rate), 2) AS avg_economy,
               SUM(bo.wickets_taken) AS total_wickets, COUNT(DISTINCT bo.match_id) AS matches_at_venue
        FROM bowling_performance bo
        JOIN players p ON bo.player_id = p.player_id
        JOIN matches m ON bo.match_id = m.match_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE bo.overs_bowled >= 4
        GROUP BY p.player_id, v.venue_id HAVING COUNT(DISTINCT bo.match_id) >= 2;
    """},
    11: {"title": "Performance in close matches", "sql": """
        SELECT p.full_name, ROUND(AVG(b.runs_scored), 2) AS avg_runs, COUNT(*) AS close_matches_played
        FROM batting_performance b
        JOIN players p ON b.player_id = p.player_id
        JOIN matches m ON b.match_id = m.match_id
        WHERE (m.victory_type = 'runs' AND m.victory_margin < 50)
           OR (m.victory_type = 'wickets' AND m.victory_margin < 5)
        GROUP BY p.player_id ORDER BY avg_runs DESC;
    """},
    12: {"title": "Year-over-year batting trend", "sql": """
        SELECT p.full_name, strftime('%Y', m.match_date) AS year,
               ROUND(AVG(b.runs_scored), 2) AS avg_runs, ROUND(AVG(b.strike_rate), 2) AS avg_strike_rate,
               COUNT(*) AS innings_played
        FROM batting_performance b
        JOIN players p ON b.player_id = p.player_id
        JOIN matches m ON b.match_id = m.match_id
        WHERE m.match_date IS NOT NULL
        GROUP BY p.player_id, year HAVING COUNT(*) >= 3 ORDER BY avg_runs DESC;
    """},
    13: {"title": "Most economical bowlers (3+ matches, thresholds scaled to sample size)", "sql": """
        SELECT p.full_name, ROUND(AVG(bo.economy_rate), 2) AS overall_economy,
               SUM(bo.wickets_taken) AS total_wickets, COUNT(DISTINCT bo.match_id) AS matches_played
        FROM bowling_performance bo
        JOIN players p ON bo.player_id = p.player_id
        JOIN matches m ON bo.match_id = m.match_id
        WHERE m.match_format IN ('ODI', 'T20')
        GROUP BY p.player_id
        HAVING COUNT(DISTINCT bo.match_id) >= 3 AND AVG(bo.overs_bowled) >= 2
        ORDER BY overall_economy ASC;
    """},
    14: {"title": "Batting consistency (avg + std dev)", "sql": """
        SELECT p.full_name, ROUND(AVG(b.runs_scored), 2) AS avg_runs,
               ROUND(SQRT(AVG(b.runs_scored * b.runs_scored) - AVG(b.runs_scored) * AVG(b.runs_scored)), 2) AS std_dev_runs
        FROM batting_performance b
        JOIN players p ON b.player_id = p.player_id
        WHERE b.balls_faced >= 10
        GROUP BY p.player_id HAVING COUNT(*) >= 2 ORDER BY avg_runs DESC;
    """},
    15: {"title": "Format-wise match count and batting average (3+ matches, thresholds scaled)", "sql": """
        SELECT p.full_name,
               COUNT(DISTINCT CASE WHEN m.match_format = 'TEST' THEN b.match_id END) AS test_matches,
               COUNT(DISTINCT CASE WHEN m.match_format = 'ODI' THEN b.match_id END) AS odi_matches,
               COUNT(DISTINCT CASE WHEN m.match_format = 'T20' THEN b.match_id END) AS t20_matches,
               ROUND(AVG(b.runs_scored), 2) AS overall_avg_runs
        FROM batting_performance b
        JOIN players p ON b.player_id = p.player_id
        JOIN matches m ON b.match_id = m.match_id
        GROUP BY p.player_id HAVING COUNT(DISTINCT b.match_id) >= 3
        ORDER BY overall_avg_runs DESC;
    """},
    16: {"title": "Head-to-head team analysis (2+ meetings, thresholds scaled)", "sql": """
        SELECT t1.team_name AS team_a, t2.team_name AS team_b, COUNT(*) AS total_matches,
               SUM(CASE WHEN m.winner_team_id = m.team1_id THEN 1 ELSE 0 END) AS team_a_wins,
               SUM(CASE WHEN m.winner_team_id = m.team2_id THEN 1 ELSE 0 END) AS team_b_wins,
               ROUND(AVG(m.victory_margin), 2) AS avg_margin
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        GROUP BY m.team1_id, m.team2_id HAVING COUNT(*) >= 2;
    """},
    17: {"title": "Recent form and momentum (last 10 innings)", "sql": """
        WITH ranked_innings AS (
            SELECT b.*, p.full_name, m.match_date,
                   ROW_NUMBER() OVER (PARTITION BY b.player_id ORDER BY m.match_date DESC) AS rn
            FROM batting_performance b
            JOIN players p ON b.player_id = p.player_id
            JOIN matches m ON b.match_id = m.match_id
        )
        SELECT full_name,
               ROUND(AVG(CASE WHEN rn <= 5 THEN runs_scored END), 2) AS avg_last5,
               ROUND(AVG(CASE WHEN rn <= 10 THEN runs_scored END), 2) AS avg_last10,
               SUM(CASE WHEN rn <= 10 AND runs_scored >= 50 THEN 1 ELSE 0 END) AS scores_above_50,
               CASE
                   WHEN AVG(CASE WHEN rn <= 5 THEN runs_scored END) >= 40 THEN 'Excellent Form'
                   WHEN AVG(CASE WHEN rn <= 5 THEN runs_scored END) >= 25 THEN 'Good Form'
                   WHEN AVG(CASE WHEN rn <= 5 THEN runs_scored END) >= 15 THEN 'Average Form'
                   ELSE 'Poor Form'
               END AS form_category
        FROM ranked_innings WHERE rn <= 10
        GROUP BY player_id ORDER BY avg_last5 DESC;
    """},
    18: {"title": "Best batting partnerships", "sql": """
        SELECT p1.full_name AS player1, p2.full_name AS player2,
               ROUND(AVG(b1.runs_scored + b2.runs_scored), 2) AS avg_partnership_runs,
               SUM(CASE WHEN (b1.runs_scored + b2.runs_scored) > 50 THEN 1 ELSE 0 END) AS partnerships_over_50,
               MAX(b1.runs_scored + b2.runs_scored) AS highest_partnership
        FROM batting_performance b1
        JOIN batting_performance b2 ON b1.match_id = b2.match_id AND b1.innings_no = b2.innings_no
            AND b2.batting_position = b1.batting_position + 1
        JOIN players p1 ON b1.player_id = p1.player_id
        JOIN players p2 ON b2.player_id = p2.player_id
        GROUP BY p1.player_id, p2.player_id HAVING COUNT(*) >= 2
        ORDER BY highest_partnership DESC;
    """},
    19: {"title": "Career trajectory (quarterly, thresholds scaled)", "sql": """
        WITH quarterly AS (
            SELECT b.player_id, p.full_name,
                   strftime('%Y', m.match_date) || '-Q' || ((CAST(strftime('%m', m.match_date) AS INTEGER) - 1) / 3 + 1) AS quarter,
                   AVG(b.runs_scored) AS avg_runs
            FROM batting_performance b
            JOIN players p ON b.player_id = p.player_id
            JOIN matches m ON b.match_id = m.match_id
            GROUP BY b.player_id, quarter HAVING COUNT(*) >= 2
        )
        SELECT full_name, COUNT(DISTINCT quarter) AS quarters_active, ROUND(AVG(avg_runs), 2) AS overall_avg_runs
        FROM quarterly GROUP BY player_id HAVING COUNT(DISTINCT quarter) >= 2
        ORDER BY overall_avg_runs DESC;
    """},
    20: {"title": "Top 10 strike rates (min 20 balls faced)", "sql": """
        SELECT p.full_name, b.runs_scored, b.balls_faced, b.strike_rate, m.match_format
        FROM batting_performance b
        JOIN players p ON b.player_id = p.player_id
        JOIN matches m ON b.match_id = m.match_id
        WHERE b.balls_faced >= 20 ORDER BY b.strike_rate DESC LIMIT 10;
    """},
    21: {"title": "Most sixes hit", "sql": """
        SELECT p.full_name, SUM(b.sixes) AS total_sixes, SUM(b.fours) AS total_fours
        FROM batting_performance b JOIN players p ON b.player_id = p.player_id
        GROUP BY p.player_id ORDER BY total_sixes DESC LIMIT 10;
    """},
    22: {"title": "Best individual bowling figures in a match", "sql": """
        SELECT p.full_name, m.match_desc, bo.wickets_taken, bo.runs_conceded, bo.overs_bowled
        FROM bowling_performance bo
        JOIN players p ON bo.player_id = p.player_id
        JOIN matches m ON bo.match_id = m.match_id
        ORDER BY bo.wickets_taken DESC, bo.runs_conceded ASC LIMIT 10;
    """},
    23: {"title": "Highest innings totals across all matches (window function ranking)", "sql": """
        WITH innings_totals AS (
            SELECT match_id, innings_no, SUM(runs_scored) AS innings_total
            FROM batting_performance
            GROUP BY match_id, innings_no
        ),
        ranked AS (
            SELECT match_id, innings_no, innings_total,
                   RANK() OVER (ORDER BY innings_total DESC) AS overall_rank
            FROM innings_totals
        )
        SELECT r.match_id, m.match_desc, r.innings_no, r.innings_total
        FROM ranked r JOIN matches m ON r.match_id = m.match_id
        WHERE r.overall_rank <= 10
        ORDER BY r.innings_total DESC;
    """},
    24: {"title": "Boundary reliance leaders (min 100 runs)", "sql": """
        SELECT p.full_name, SUM(b.runs_scored) AS total_runs,
               (SUM(b.fours) * 4 + SUM(b.sixes) * 6) AS boundary_runs,
               ROUND((SUM(b.fours) * 4 + SUM(b.sixes) * 6) * 100.0 / NULLIF(SUM(b.runs_scored), 0), 2) AS boundary_pct
        FROM batting_performance b
        JOIN players p ON b.player_id = p.player_id
        GROUP BY p.player_id
        HAVING SUM(b.runs_scored) >= 100
        ORDER BY boundary_pct DESC LIMIT 10;
    """},
    25: {"title": "Most consistent bowlers by wicket variance (3+ matches)", "sql": """
        WITH bowler_match_wickets AS (
            SELECT player_id, match_id, SUM(wickets_taken) AS match_wickets
            FROM bowling_performance
            GROUP BY player_id, match_id
        )
        SELECT p.full_name, COUNT(*) AS matches_played,
               ROUND(AVG(match_wickets), 2) AS avg_wickets,
               ROUND(SQRT(AVG(match_wickets * match_wickets) - AVG(match_wickets) * AVG(match_wickets)), 2) AS std_dev_wickets
        FROM bowler_match_wickets bmw
        JOIN players p ON bmw.player_id = p.player_id
        GROUP BY bmw.player_id
        HAVING COUNT(*) >= 3
        ORDER BY std_dev_wickets ASC;
    """},
}