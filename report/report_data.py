
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection


def get_db_connection(config: dict) -> connection:
    """Creates and returns a connection to the PostgreSQL
    database using environment variables."""
    return connect(
        dbname=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"],
        port=config["DB_PORT"],
        cursor_factory=RealDictCursor
    )


def get_match_data(config: dict, match_id: int) -> dict[str]:
    """Get match data from database."""

    match_query = """
    SELECT 
        m.match_id,
        m.match_date,
        ht.team_name as home_team,
        at.team_name as away_team,
        c.competition_name,
        s.season_name
    FROM match m
    JOIN team ht ON m.home_team_id = ht.team_id
    JOIN team at ON m.away_team_id = at.team_id
    JOIN match_assignment ma USING(match_id)
    JOIN competition c USING(competition_id)
    JOIN season s USING(season_id)
    WHERE m.match_id = %s
    """

    stats_query = """
    SELECT 
        mms.*
    FROM match_minute_stats mms
    WHERE mms.match_id = %s
    ORDER BY mms.match_minute, mms.half
    """

    events_query = """
    SELECT 
        me.match_event_id,
        mms.match_minute,
        mms.half,
        et.type_name as event_type,
        t.team_name,
        p.player_name
        FROM match_event me
    JOIN match_minute_stats mms USING(match_minute_stats_id)
    JOIN event_type et USING(event_type_id)
    JOIN team t USING(team_id)
    JOIN player_match_event pme USING(match_event_id)
    JOIN player p USING(player_id)
    WHERE mms.match_id = %s
    ORDER BY mms.match_minute, mms.half, me.match_event_id
    """

    conn = get_db_connection(config)
    with conn.cursor() as cur:
        cur.execute(match_query, (match_id,))
        match_info = cur.fetchone()

        if not match_info:
            raise ValueError(f"Match with ID {match_id} not found")

        cur.execute(stats_query, (match_id,))
        match_stats = cur.fetchall()

        cur.execute(events_query, (match_id,))
        match_events = cur.fetchall()
    return {
        'match_info': dict(match_info),
        'match_stats': [dict(stat) for stat in match_stats],
        'match_events': [dict(event) for event in match_events]
    }
