import os


DB_CONFIG = {
    "host": os.getenv("PHONEBOOK_DB_HOST", "localhost"),
    "port": int(os.getenv("PHONEBOOK_DB_PORT", "5432")),
    "dbname": os.getenv("PHONEBOOK_DB_NAME", "phonebook"),
    "user": os.getenv("PHONEBOOK_DB_USER", "postgres"),
    "password": os.getenv("PHONEBOOK_DB_PASSWORD", "postgres"),
}
