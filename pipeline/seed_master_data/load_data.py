"""Script to run the load phase of this pipeline."""
from psycopg2.extensions import connection


def insert_team(conn: connection, team: dict) -> None:
    """Inserts a team record into the database if it doesn't 
    already exist."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO team (team_id, team_name, team_code, logo_url)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (team_id) DO NOTHING;
        """, (team["team_id"], team["name"], team["short_code"], team["logo_url"]
              ))
        cur.close()


def insert_competition(conn: connection, name: str) -> None:
    """Inserts a competition record into the database if 
    it doesn't already exist."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO competition (competition_name)
            VALUES (%s)
            ON CONFLICT (competition_name) DO NOTHING;
        """, (name,))
        cur.close()


def insert_season(conn: connection, name: str) -> None:
    """Inserts a season record into the database if it does not already exist."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO season (season_name)
            VALUES (%s)
            ON CONFLICT (season_name) DO NOTHING;
        """, (name,))
        cur.close()


def insert_match(conn: connection, match_id: int, home_team_id: int, away_team_id: int, match_date: str) -> None:
    """Inserts a match and returns its generated ID."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO match (match_id, home_team_id, away_team_id, match_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (match_id) DO NOTHING;
        """, (match_id, home_team_id, away_team_id, match_date))
        cur.close()


def insert_match_assignment(conn: connection, match_id: int, competition_name: str, season_name: str) -> None:
    """Inserts a match assignment record with the fetched 
    competition_id and season_id new match_id."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT competition_id FROM competition WHERE competition_name = %s;
        """, (competition_name,))
        competition_id = cur.fetchone()
        if not competition_id:
            raise ValueError(
                f"Competition '{competition_name}' not found in DB.")
        competition_id = competition_id[0]

        cur.execute("""
            SELECT season_id FROM season WHERE season_name = %s;
        """, (season_name,))
        season_id = cur.fetchone()
        if not season_id:
            raise ValueError(f"Season '{season_name}' not found in DB.")
        season_id = season_id[0]

        cur.execute("""
            INSERT INTO match_assignment (match_id, competition_id, season_id)
            VALUES (%s, %s, %s);
        """, (match_id, competition_id, season_id))
        cur.close()


def load_master_data(master_data: dict, conn: connection) -> None:
    """Loads validated match master data into the RDS PostgreSQL database.
    Inserts team, competition, season, match, and match_assignment data."""

    if master_data["insert_home_team"]:
        insert_team(conn, master_data["home_team"])
    if master_data["insert_away_team"]:
        insert_team(conn, master_data["away_team"])
    if master_data["insert_competition"]:
        insert_competition(conn, master_data["competition_name"])
    if master_data["insert_season"]:
        insert_season(conn, master_data["season_name"])

    insert_match(
        conn,
        master_data["match_id"],
        master_data["home_team"]["team_id"],
        master_data["away_team"]["team_id"],
        master_data["match_date"]
    )
    insert_match_assignment(
        conn, master_data["match_id"], master_data["competition_name"], master_data["season_name"]
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    pass
