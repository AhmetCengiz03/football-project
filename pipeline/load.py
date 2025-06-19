"""Loading to database."""
from os import environ as ENV
import logging

from dotenv import load_dotenv
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import connection

from transform import get_dataframe_from_json, transform_data


logger = logging.getLogger(__name__)
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)


def get_connection() -> connection:
    """Get database connection to the PostgreSQL database."""

    return psycopg2.connect(
        host=ENV["DB_HOST"],
        dbname=ENV["DB_NAME"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASS"],
        port=ENV["DB_PORT"]
    )


def insert_dataframe(df: pd.DataFrame, table_name: str, db_conn: connection,
                     returning=None, conflict=None) -> list[tuple] | None:
    """Insert data from a pandas Dataframe into a PostgreSQL table."""

    columns = ", ".join(df.columns)

    if df.isnull().any().any():
        logger.info("DataFrame for table %s found null values.", table_name)
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
    else:
        logger.info("DataFrame for table %s found no null values.", table_name)
        values = df.to_records(index=False).tolist()

    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES %s"

    if conflict:
        if isinstance(conflict, (list, tuple)):
            conflict = ", ".join(conflict)
        insert_query += f" ON CONFLICT ({conflict}) DO NOTHING"

    if returning:
        insert_query += f" RETURNING {returning}"

    try:
        with db_conn.cursor() as cursor:

            logger.info("Running execute_values ...")
            execute_values(cursor, insert_query, values)

            result = cursor.fetchall() if returning else None

            db_conn.commit()

            logger.info("Upload successful.")
            return result

    except psycopg2.Error as e:
        db_conn.rollback()
        logger.error("Error inserting data: %s", e)
        return None


def upload_all_data(minute_df: pd.DataFrame, db_conn: connection,
                    event_df: pd.DataFrame = None) -> list[dict]:
    """Upload transformed data to all relevant tables."""

    logger.info("Uploading to match_minute_stats ...")
    match_minute_stats_id = insert_dataframe(
        minute_df, "match_minute_stats", db_conn, "match_minute_stats_id")

    if not event_df.empty:
        if isinstance(match_minute_stats_id, list):
            event_df["match_minute_stats_id"] = match_minute_stats_id[0][0]

        match_event_df = event_df[[
            "match_event_id", "match_minute_stats_id", "event_type_id", "team_id"]]

        goal_check = get_if_goal_scored_this_run(event_df, db_conn)

        logger.info("Uploading to match_event ...")
        insert_dataframe(match_event_df, "match_event",
                         db_conn, "match_event_id", "match_event_id")

        player_df = get_players_df(event_df)

        logger.info("Uploading to player ...")
        insert_dataframe(player_df, "player", db_conn,
                         returning="player_id", conflict="player_id")

        player_match_event_df = event_df[["match_event_id",
                                          "player_id", "related_player_id"]].copy()

        player_match_event_df["related_player_id"] = player_match_event_df[
            "related_player_id"].astype(
            float).astype('Int64')

        logger.info("Uploading to player_match_event ...")
        insert_dataframe(player_match_event_df, "player_match_event",
                         db_conn, conflict=["match_event_id", "player_id"])

        return goal_check
    return []


def get_players_df(event_df: pd.DataFrame):
    """Uploads the match event data."""

    players = pd.concat([
        event_df[["player_id", "player_name"]].rename(
            columns={"player_id": "id",
                     "player_name": "name"}),
        event_df[["related_player_id", "related_player_name"]].rename(
            columns={"related_player_id": "id",
                     "related_player_name": "name"})
    ])

    player_df = players.dropna(subset=["id"]).drop_duplicates(subset=["id"])

    logger.info("Successfully created players dataframe.")
    return player_df.rename(
        columns={"id": "player_id", "name": "player_name"})


def get_if_goal_scored_this_run(event_df: pd.DataFrame, db_conn: connection) -> list[dict]:
    """Returns information on if a goal was recorded for this minute."""

    goals_df = event_df[event_df["type_name"].str.lower() == "goal"]
    goal_event_ids = set(goals_df["match_event_id"])

    if not goal_event_ids:
        return []

    with db_conn.cursor() as curs:
        curs.execute(
            """
            SELECT m.match_event_id FROM match_event as m
            JOIN event_type as e USING (event_type_id)
            WHERE e.type_name = 'goal'
            """)
        known_goal_ids = set(row[0] for row in curs.fetchall())

    new_goals = goal_event_ids - known_goal_ids

    if not new_goals:
        return []

    new_goals_df = goals_df[goals_df["match_event_id"].isin(new_goals)]

    new_goals_info = new_goals_df[[
        "match_event_id", "match_id", "team_id", "player_name", "minute", "type_name"
    ]].to_dict(orient="records")

    return new_goals_info


if __name__ == "__main__":

    load_dotenv()

    base_df = get_dataframe_from_json("match_19348530/scrape_101.json")
    m_df, e_df, flags = transform_data(base_df)

    conn = get_connection()
    upload_all_data(m_df, conn, e_df)

    conn.close()
