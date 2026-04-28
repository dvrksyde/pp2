import psycopg
from pathlib import Path
from config import DB_CONFIG

def get_connection():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        conn = psycopg.connect(**DB_CONFIG)
        return conn
    except Exception as error:
        safe_error = str(error).encode("ascii", "backslashreplace").decode("ascii")
        print(f"Error: {safe_error}")
        return None

def init_db():
    """ Initialize the database with schema and procedures """
    conn = get_connection()
    if conn:
        try:
            base_dir = Path(__file__).resolve().parent
            with conn.cursor() as cur:
                # Read and execute schema.sql
                with open(base_dir / 'schema.sql', 'r', encoding='utf-8') as f:
                    cur.execute(f.read())
                # Read and execute procedures.sql
                with open(base_dir / 'procedures.sql', 'r', encoding='utf-8') as f:
                    cur.execute(f.read())
            conn.commit()
            print("Database initialized successfully.")
        except Exception as e:
            conn.rollback()
            print(f"Failed to initialize database: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    init_db()
