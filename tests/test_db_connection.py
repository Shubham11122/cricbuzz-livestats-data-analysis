from database.db_connection import get_connection

def test_connection_works():
    conn = get_connection()
    assert conn is not None
    conn.close()

def test_tables_exist():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    expected = ["teams", "venues", "series", "players", "matches",
                "batting_performance", "bowling_performance", "fielding_performance"]
    for table in expected:
        assert table in tables
    conn.close()

def test_data_populated():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM matches")
    assert cursor.fetchone()[0] > 0
    conn.close()