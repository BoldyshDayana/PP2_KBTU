# PostgreSQL integration via psycopg2, with JSON fallback.
import json
import os
from datetime import datetime

LEADERBOARD_FILE = "leaderboard.json"

# Try importing psycopg2 

try:
    import psycopg2
    import psycopg2.extras
    _PSYCOPG2_AVAILABLE = True
except ImportError:
    _PSYCOPG2_AVAILABLE = False

try:
    from config import DB_CONFIG, DB_SCHEMA
except ImportError:
    DB_CONFIG = {}
    DB_SCHEMA = ""

# JSON fallback helpers 

def _load_json() -> list:
    """Load leaderboard.json, returning a list of session dicts."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[db] JSON load failed: {e}")
        return []


def _save_json(records: list):
    """Write records list to leaderboard.json."""
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(records, f, indent=2)
    except Exception as e:
        print(f"[db] JSON save failed: {e}")


def _normalize(record: dict) -> dict:
    """
    Normalize a record from either the old or new schema into a consistent shape:
      {username, score, level_reached, played_at}
    Old schema used: name, score, distance, coins
    New schema uses: username, score, level_reached, played_at
    """
    return {
        "username":      record.get("username") or record.get("name", "???"),
        "score":         int(record.get("score", 0)),
        "level_reached": int(record.get("level_reached", record.get("coins", 1))),
        "played_at":     record.get("played_at", datetime.now().strftime("%Y-%m-%d")),
    }

# Connection helper 

def _connect():
    """Open and return a new psycopg2 connection, or None on failure."""
    if not _PSYCOPG2_AVAILABLE:
        return None
    try:
        from urllib.parse import quote_plus
        host     = str(DB_CONFIG.get("host", "localhost"))
        port     = int(DB_CONFIG.get("port", 5432))
        dbname   = str(DB_CONFIG.get("dbname", "snake_db"))
        user     = quote_plus(str(DB_CONFIG.get("user", "postgres")))
        password = quote_plus(str(DB_CONFIG.get("password", "")))
        dsn = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        conn = psycopg2.connect(dsn)
        conn.set_client_encoding("UTF8")
        return conn
    except Exception as e:
        print(f"[db] Connection failed: {e}")
        return None

# Schema bootstrap

def init_db() -> bool:
    """
    Try to create the PostgreSQL tables.
    Returns True if DB is available, False if falling back to JSON.
    """
    conn = _connect()
    if conn is None:
        print("[db] PostgreSQL unavailable — using leaderboard.json fallback.")
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(DB_SCHEMA)
        conn.commit()
        return True
    except Exception as e:
        print(f"[db] Schema init failed: {e}")
        return False
    finally:
        conn.close()

#Player helpers 

def get_or_create_player(username: str) -> int | None:
    """Return the player id for *username*, inserting a new row if needed."""
    conn = _connect()
    if conn is None:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) RETURNING id",
                (username,)
            )
            player_id = cur.fetchone()[0]
        conn.commit()
        return player_id
    except Exception as e:
        print(f"[db] get_or_create_player failed: {e}")
        return None
    finally:
        conn.close()

# Session save 

def save_session(username: str, score: int, level_reached: int) -> bool:
    """
    Save a game session. Tries PostgreSQL first, falls back to JSON.
    Returns True on success.
    """
    # Try PostgreSQL 
    player_id = get_or_create_player(username)
    if player_id is not None:
        conn = _connect()
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO game_sessions (player_id, score, level_reached)
                           VALUES (%s, %s, %s)""",
                        (player_id, score, level_reached)
                    )
                conn.commit()
                return True
            except Exception as e:
                print(f"[db] save_session (pg) failed: {e}")
            finally:
                conn.close()

    #  JSON fallback
    records = _load_json()
    records.append({
        "username":      username,
        "score":         score,
        "level_reached": level_reached,
        "played_at":     datetime.now().strftime("%Y-%m-%d"),
    })
    _save_json(records)
    print(f"[db] Session saved to JSON: {username} score={score} level={level_reached}")
    return True

# Leaderboard 

def get_top10() -> list[dict]:
    """
    Fetch the top-10 all-time scores.
    Each entry: {rank, username, score, level_reached, played_at}.
    Falls back to leaderboard.json if DB is unavailable.
    """
    #Try PostgreSQL 
    conn = _connect()
    if conn is not None:
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT p.username, gs.score, gs.level_reached, gs.played_at
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    ORDER BY gs.score DESC
                    LIMIT 10
                """)
                rows = cur.fetchall()
            return [
                {
                    "rank":          i + 1,
                    "username":      r["username"],
                    "score":         r["score"],
                    "level_reached": r["level_reached"],
                    "played_at":     r["played_at"].strftime("%Y-%m-%d") if r["played_at"] else "-",
                }
                for i, r in enumerate(rows)
            ]
        except Exception as e:
            print(f"[db] get_top10 (pg) failed: {e}")
        finally:
            conn.close()

    # JSON fallback
    records = _load_json()
    if not records:
        return []

    normalized = [_normalize(r) for r in records]
    normalized.sort(key=lambda r: r["score"], reverse=True)
    top10 = normalized[:10]

    return [
        {
            "rank":          i + 1,
            "username":      r["username"],
            "score":         r["score"],
            "level_reached": r["level_reached"],
            "played_at":     r["played_at"],
        }
        for i, r in enumerate(top10)
    ]

# Personal best 

def get_personal_best(username: str) -> int:
    """
    Return the highest score ever recorded for *username*, or 0.
    Falls back to leaderboard.json if DB is unavailable.
    """
    # Try PostgreSQL 
    conn = _connect()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT MAX(gs.score)
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    WHERE p.username = %s
                """, (username,))
                row = cur.fetchone()
                return row[0] if row and row[0] is not None else 0
        except Exception as e:
            print(f"[db] get_personal_best (pg) failed: {e}")
        finally:
            conn.close()

    # JSON fallback 
    records = _load_json()
    scores = [
        r.get("score", 0)
        for r in records
        if (r.get("username") or r.get("name", "")) == username
    ]
    return max(scores, default=0)