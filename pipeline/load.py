"""Loading to database."""
from os import environ as ENV

from dotenv import load_dotenv
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import connection
import numpy as np

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
    # values = df.to_records(index=False).tolist()

    values = []
    for _, row in df.iterrows():
        processed_row = []
        for item in row:
            if pd.isna(item):
                processed_row.append(None)
            elif isinstance(item, float) and item.is_integer():
                processed_row.append(int(item))
            else:
                processed_row.append(item)
        values.append(tuple(processed_row))

    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES %s"

    if conflict:
        if isinstance(conflict, (list, tuple)):
            conflict = ", ".join(conflict)
        insert_query += f" ON CONFLICT ({conflict}) DO NOTHING"

    if returning:
        insert_query += f" RETURNING {returning}"

    print(values)
    print(columns)
    print(insert_query)
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

    base_df = get_dataframe_from_json("match_19367875/scrape_117.json")
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

    players = pd.concat([
        b[["player_id", "player_name"]].rename(
            columns={"player_id": "id",
                     "player_name": "name"}),
        b[["related_player_id", "related_player_name"]].rename(
            columns={"related_player_id": "id",
                     "related_player_name": "name"})
    ])

    player_df = players.dropna(subset=["id"]).drop_duplicates(subset=["id"])
    player_df = player_df.rename(
        columns={"id": "player_id", "name": "player_name"})

    print(insert_dataframe(player_df, "player", db_conn,
          returning="player_id", conflict="player_id"))

    player_match_event_df = b[["match_event_id",
                               "player_id", "related_player_id"]].copy()
    print(player_match_event_df)

    player_match_event_df["related_player_id"] = player_match_event_df["related_player_id"].astype(
        'Int64')
    player_match_event_df["match_event_id"] = player_match_event_df["match_event_id"].astype(
        int)
    player_match_event_df["player_id"] = player_match_event_df["player_id"].astype(
        int)

    print(player_match_event_df)
    print(player_match_event_df.dtypes)

    # player_match_event_df["related_player_id"] = player_match_event_df["related_player_id"].astype(
    #     'int', errors='ignore')

    # player_match_event_df["related_player_id"] = player_match_event_df["related_player_id"].apply(
    #     lambda x: int(x) if pd.notna(x) else None
    # )
    # player_match_event_df["related_player_id"] = player_match_event_df["related_player_id"].apply(
    #     np.int64
    # )

    player_match_event_df["related_player_id"] = player_match_event_df["related_player_id"].astype(
        float).astype('Int64')
    # player_match_event_df["related_player_id"] = player_match_event_df["related_player_id"].astype(
    #     int)
    # player_match_event_df["related_player_id"] = player_match_event_df["related_player_id"].astype(
    #     str)
    # player_match_event_df["related_player_id"] = player_match_event_df["related_player_id"].replace(
    #     '-1', None)
    # player_match_event_df["related_player_id"] = player_match_event_df["related_player_id"].astype(
    #     int)

    print(player_match_event_df)

    # # print("Inserting player_match_event")
    print(player_match_event_df.info())
    insert_dataframe(player_match_event_df, "player_match_event",
                     db_conn, conflict=["match_event_id", "player_id"])
    db_conn.close()

    # upload_all_data(transformed_data)
