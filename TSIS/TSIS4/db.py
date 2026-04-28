import psycopg
from config import DB_CONFIG

def get_connection():
    try:
        return psycopg.connect(**DB_CONFIG)
    except Exception as exc:
        print(f"Database connection error: {exc}")
        return None

def init_db():
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id       SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                );
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id            SERIAL PRIMARY KEY,
                    player_id     INTEGER REFERENCES players(id),
                    score         INTEGER   NOT NULL,
                    level_reached INTEGER   NOT NULL,
                    played_at     TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()
        return True
    except Exception as exc:
        conn.rollback()
        print(f"Database initialization error: {exc}")
        return False
    finally:
        conn.close()

def save_game_result(username, score, level):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO UPDATE SET username=EXCLUDED.username RETURNING id",
                (username,),
            )
            player_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
                (player_id, score, level),
            )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        print(f"Failed to save game result: {exc}")
    finally:
        conn.close()

def get_top_scores():
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.username, s.score, s.level_reached, s.played_at
                FROM game_sessions s
                JOIN players p ON s.player_id = p.id
                ORDER BY s.score DESC
                LIMIT 10
            """)
            rows = cur.fetchall()
        return rows
    except Exception as exc:
        print(f"Failed to load top scores: {exc}")
        return []
    finally:
        conn.close()

def get_personal_best(username):
    conn = get_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT MAX(score) FROM game_sessions s
                JOIN players p ON s.player_id = p.id
                WHERE p.username = %s
            """, (username,))
            res = cur.fetchone()
        return res[0] if res and res[0] else 0
    except Exception as exc:
        print(f"Failed to load personal best: {exc}")
        return 0
    finally:
        conn.close()
