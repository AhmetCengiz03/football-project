import os
import psycopg2
from typing import Dict
from os import environ as ENV

from extract_transform import get_db_connection


def insert_team(cur, team: Dict) -> None:
    """Inserts a team record into the database if it doesn't 
    already exist."""

    cur.execute("""
        INSERT INTO team (team_id, team_name, team_code, logo_url)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (team_id) DO NOTHING;
    """, (team["team_id"], team["name"], team["short_code"], team["logo_url"]
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


def insert_match(cur, home_team_id: int, away_team_id: int, match_date: str) -> int:
    """Inserts a match and returns its generated ID."""

    cur.execute("""
        INSERT INTO match (home_team_id, away_team_id, match_date)
        VALUES (%s, %s, %s)
        RETURNING match_id;
    """, (home_team_id, away_team_id, match_date))

    return cur.fetchone()[0]


def insert_match_assignment(cur, match_id: int, competition_id: int, season_id: int) -> None:
    """Inserts a match assignment record with new match_id."""
    cur.execute("""
        INSERT INTO match_assignment (match_id, competition_id, season_id)
        VALUES (%s, %s, %s);
    """, (match_id, competition_id, season_id))


def load_master_data(master_data: Dict) -> None:
    """Loads validated match master data into the RDS PostgreSQL database.
    Inserts team, competition, season, match, and match_assignment data."""
    conn = get_db_connection()
    cur = conn.cursor()

    insert_team(cur, master_data["home_team"])
    insert_team(cur, master_data["away_team"])
    insert_competition(
        cur, master_data["competition_id"], master_data["competition_name"]
    )
    insert_season(
        cur, master_data["season_id"], master_data["season_name"]
    )

    # here I'm inserting into match table and receiving the new match_id
    match_id = insert_match(
        cur,
        master_data["home_team"]["team_id"],
        master_data["away_team"]["team_id"],
        master_data["match_date"]
    )
    insert_match_assignment(
        cur, match_id, master_data["competition_id"], master_data["season_id"]
    )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    pass
