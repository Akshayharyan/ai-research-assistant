from dotenv import load_dotenv
load_dotenv()
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True
)

def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        print("Connected to Supabase!")
        print(result.scalar())

if __name__ == "__main__":
    test_connection()