import os


DB_CONFIG = {
    "host": os.getenv("SNAKE_DB_HOST", "localhost"),
    "port": int(os.getenv("SNAKE_DB_PORT", "5432")),
    "dbname": os.getenv("SNAKE_DB_NAME", "snake_game"),
    "user": os.getenv("SNAKE_DB_USER", "postgres"),
    "password": os.getenv("SNAKE_DB_PASSWORD", "postgres"),
}

# Game Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BLOCK_SIZE = 20
FPS = 10
