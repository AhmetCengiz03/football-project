"""Script to get all necessary data for dashboard."""
from os import environ as ENV

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import pandas as pd
import streamlit as st


@st.cache_resource
def get_connection() -> connection:
    """Get database connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=ENV("DB_HOST"),
        dbname=ENV("DB_NAME"),
        user=ENV("DB_USER"),
        password=ENV("DB_PASSWORD"),
        port=ENV("DB_PORT")
    )


def execute_query(query: str, params=None) -> pd.DataFrame:
    """Execute query and handle the connection/cursor."""
    conn = get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, params or [])
        records = cursor.fetchall()
        all_matches = pd.DataFrame(records)
    return all_matches


@st.cache_data
def get_all_matches() -> pd.DataFrame:
    """Get all matches for the dropdown."""
    query = """
            SELECT m.match_id, m.match_date,
                ht.team_name as home_team,
                at.team_name as away_team,
                c.competition_name,
                s.season_name
            FROM match m
            JOIN team ht ON m.home_team_id = ht.team_id
            JOIN team at ON m.away_team_id = at.team_id
            JOIN match_assignment ma ON m.match_id = ma.match_id
            JOIN competition c ON ma.competition_id = c.competition_id
            JOIN season s ON ma.season_id = s.season_id
            """
    return execute_query(query)


@st.cache_data
def get_event_data_for_selected_match(match_id: int) -> pd.DataFrame:
    """Retrieve all event data for the selected match."""
    query = """
                SELECT me.*, et.type_name
                FROM match_event me
                JOIN event_type et
                ON me.event_type_id = et.event_type_id
                WHERE me.match_id = %s
                 """
    return execute_query(query, match_id)


@st.cache_data
def get_all_stats_for_selected_match(match_id: int) -> pd.DataFrame:
    """Retrieve all the stats data for the selected match."""
    query = """
            SELECT *
            FROM match_minute_stats 
            WHERE match_id = %s
            """
    return execute_query(query, match_id)


@st.cache_data
def get_match_info_for_selected_match(match_id: int) -> pd.DataFrame:
    """Retrieve all the match info for the selected match."""
    query = """
            SELECT * 
            FROM match
            WHERE match_id = %s
            """
    return execute_query(query, match_id)
