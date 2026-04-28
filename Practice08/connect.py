import psycopg2
from config import load_config

def connect():
    try:
        config = load_config()
        conn = psycopg2.connect(**config)
        print("Connected successfully!")
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print("CONNECTION ERROR:", error)
        return None

if __name__ == "__main__":
    connect()