import os
import psycopg2
from typing import Dict
from os import environ as ENV


def get_db_connection() -> psycopg2.extensions.connection:
    """Creates and returns a connection to the PostgreSQL 
    database using environment variables."""
    return psycopg2.connect(
        dbname=ENV["DB_NAME"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"]
    )


def insert_team(cur, team: Dict) -> None:
    """Inserts a team record into the database if it doesn't 
    already exist."""

    cur.execute("""
        INSERT INTO team (team_id, team_name, logo_url)
        VALUES (%s, %s, %s)
        ON CONFLICT (team_id) DO NOTHING;
    """, (
        team["team_id"],
        team["name"],
        team["logo_url"]
    ))


def insert_competition(cur, competition_id: int, name: str) -> None:
    """Inserts a competition record into the database if 
    it doesn't already exist."""
    cur.execute("""
        INSERT INTO competition (competition_id, competition_name)
        VALUES (%s, %s)
        ON CONFLICT (competition_id) DO NOTHING;
    """, (competition_id, name))


def insert_season(cur, season_id: int, name: str) -> None:
    """
    Inserts a season record into the database if it does not already exist.
    """
    cur.execute("""
        INSERT INTO season (season_id, season_name)
        VALUES (%s, %s)
        ON CONFLICT (season_id) DO NOTHING;
    """, (season_id, name))


def load_master_data(master_data: Dict) -> None:
    """Loads validated match master data into the RDS PostgreSQL database.
    Inserts team, competition, season, match, and match_assignment data."""
    conn = get_db_connection()

    with conn.cursor() as cur:
        insert_team(cur, master_data["home_team"])
        insert_team(cur, master_data["away_team"])

        insert_competition(
            cur, master_data["competition_id"], master_data["competition_name"]
        )
        insert_season(
            cur, master_data["season_id"], master_data["season_name"]
        )

        cur.execute("""
            INSERT INTO match (match_id, home_team_id, away_team_id, match_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (match_id) DO NOTHING;
        """, (
            master_data["match_id"],
            master_data["home_team"]["team_id"],
            master_data["away_team"]["team_id"],
            master_data["match_date"]
        ))

        cur.execute("""
            INSERT INTO match_assignment (match_id, competition_id, season_id)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (
            master_data["match_id"],
            master_data["competition_id"],
            master_data["season_id"]
        ))
