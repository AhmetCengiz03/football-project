"""Loading to database."""
from os import environ as ENV
import logging

from dotenv import load_dotenv
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import connection


def configure_logger() -> None:
    """Sets up the logger."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def get_connection() -> connection:
    """Get database connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=ENV("DB_HOST"),
        dbname=ENV("DB_NAME"),
        user=ENV("DB_USER"),
        password=ENV("DB_PASSWORD"),
        port=ENV("DB_PORT")
    )
    return conn


def insert_dataframe(df: pd.DataFrame, table_name: str, conn: connection) -> None:
    """Insert data from a pandas Dataframe into a PostgreSQL table"""
    cursor = conn.cursor()
    columns = ", ".join(df.columns)
    values = df.to_records(index=False).tolist()
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES (%s)"
    try:
        with conn.cursor() as cursor:
            execute_values(cursor, insert_query, values)
            conn.commit()
            logger.info("Successfully inserted data into %s", table_name)
    except psycopg2.Error as e:
        conn.rollback()
        logger.error("Error inserting data: %s", str(e))


def upload_all_data(transformed_data: dict[str, pd.DataFrame]) -> None:
    """Upload transformed data to all relevant tables."""
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
        df = transformed_data["table"]
        insert_dataframe(df, table, conn)
    conn.close()


if __name__ == "__main__":
    load_dotenv()
    logger = configure_logger()
    upload_all_data(transformed_data)
