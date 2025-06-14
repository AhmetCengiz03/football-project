"""Loading to database."""
from os import environ as ENV

from dotenv import load_dotenv
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import connection

from transform import get_dataframe_from_json, transform_data


def get_connection() -> connection:
    """Get database connection to the PostgreSQL database."""

    return psycopg2.connect(
        host=ENV["DB_HOST"],
        dbname=ENV["DB_NAME"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASS"],
        port=ENV["DB_PORT"]
    )


def insert_dataframe(df: pd.DataFrame, table_name: str, conn: connection, returning=None, conflict=None) -> list[tuple] | None:
    """Insert data from a pandas Dataframe into a PostgreSQL table"""

    columns = ", ".join(df.columns)
    values = df.to_records(index=False).tolist()
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES %s"

    if conflict:
        insert_query += f" ON CONFLICT ({conflict}) DO NOTHING"

    if returning:
        insert_query += f" RETURNING {returning}"

    try:
        with conn.cursor() as cursor:

            execute_values(cursor, insert_query, values)

            result = cursor.fetchall() if returning else None

            conn.commit()
            return result

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error inserting data: {e}")
        return None


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


def upload_match_event(df: pd.DataFrame, conn: connection):
    """Uploads the match event data."""

    columns = ", ".join(df.columns)
    values = df.to_records(index=False).tolist()
    print(columns)
    print(values)

    # query = """
    #         INSERT INTO match_event
    #         (match_event_id, minute_stat_id, event_type_id, team_id)
    #         VALUES (%s, %s, %s, %s)
    #         ON CONFLICT (match_event_id) DO NOTHING;
    #         """

    # with conn.cursor() as curs:
    #     curs.execute()


if __name__ == "__main__":

    load_dotenv()

    base_df = get_dataframe_from_json("match_19367875/scrape_52.json")
    a, b, c = transform_data(base_df)
    print(a.info())
    print(b)

    db_conn = get_connection()
    minute_stat_id = insert_dataframe(
        a, "match_minute_stats", db_conn, "minute_stat_id")

    if isinstance(minute_stat_id, list):
        b["minute_stat_id"] = minute_stat_id[0][0]
    print(b)

    match_event_df = b[["match_event_id",
                        "minute_stat_id", "event_type_id", "team_id"]]

    print(insert_dataframe(match_event_df, "match_event",
          db_conn, "match_event_id", "match_event_id"))

    db_conn.close()

    # upload_all_data(transformed_data)
