import psycopg2
from config import CONFIG

def get_connection():
    """Connection with DB"""
    try:
        conn = psycopg2.connect(**CONFIG)
        print("Connected to database")
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def init_database():
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        #create table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100),
                birthday DATE,
                group_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        #create index
        cur.execute("CREATE INDEX IF NOT EXISTS idx_name ON contacts(name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_phone ON contacts(phone)")
        
        conn.commit() #save changes
        print("Database ready")
        return True
        
    except Exception as e:
        print(f"Init error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def close_connection(conn):
    """close connection"""
    if conn:
        conn.close()