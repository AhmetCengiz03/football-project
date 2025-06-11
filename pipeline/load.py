"""Loading to database."""
import os
from dotenv import load_dotenv

import pyscopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    """Get database connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    return conn


def load_json_to_table():
    pass


def get_cursor(conn):
    """Return a RealDictCursor."""
    return conn.cursor(cursor_factory=RealDictCursor)


def upload_all_data():
    """Upload json data to all relevant tables."""
    conn = get_connection()

    conn.close()


if __name__ == "__main__":
    upload_all_data()
