import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "clon_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "clon_pass")
    DB_NAME = os.getenv("DB_NAME", "clon_db")

settings = Settings()
