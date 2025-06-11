"""Loading to database."""
import os
from dotenv import load_dotenv
import pandas as pd

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.extensions import connection


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


def insert_dataframe(df: pd.DataFrame, table_name: str, conn: connection) -> None:
    """Insert data from a pandas Dataframe into a PostgreSQL table"""
    cursor = conn.cursor()
    columns = ", ".join(df.columns)
    # Need to convert the dataframe into a list of tuples for execute_values.
    values = df.to_records(index=False).tolist()
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES (%s)"

    # Am trying to use execute_values here as it is quicker than inserting a record at a time.
    try:
        execute_values(cursor, insert_query, values)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error inserting data: {e}")
    finally:
        cursor.close()


def get_cursor(conn):
    """Return a RealDictCursor."""
    return conn.cursor(cursor_factory=RealDictCursor)


def upload_all_data(transformed_data: dict[str, pd.DataFrame]):
    """Upload json data to all relevant tables."""
    conn = get_connection()

    for table in [
        "team",
        "competition",
        "season",
        "match",
        "match_assignment",
        "event_type",
        "match_minute_stats",
        "match_event"
    ]:
        df = transformed_data.get(table)
        insert_dataframe(df, table, conn)

    conn.close()


if __name__ == "__main__":
    load_dotenv()
    # Transformed_data_test is passed from transform script: dict[str, pd.DataFrame]
    transformed_data_test = {}
    upload_all_data(transformed_data_test)
