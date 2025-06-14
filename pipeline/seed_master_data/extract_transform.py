"""Validates and transforms match data, checking for existing
records in the database or fetching from the API if missing."""

from datetime import datetime
from http.client import HTTPSConnection
from json import loads
from os import environ as ENV

from psycopg2.extensions import connection


def validate_required_keys(event: dict) -> None:
    """Validates that all required top-level fields are present in the event."""
    required_keys = ["match_id", "league_id", "season_id",
                     "start_time", "team_data"]

    for key in required_keys:
        if key not in event:
            raise ValueError(f"Missing field: {key}.")


def validate_team_data(team_data: list[dict]) -> tuple[dict, dict]:
    """Checks that team_data contains two teams."""
    if not isinstance(team_data, list) or len(team_data) != 2:
        raise ValueError("Team data must contain exactly two teams.")

    return team_data[0], team_data[1]


def get_team_by_location(team1: dict, team2: dict, location: str) -> str:
    for team in [team1, team2]:
        if team["team_1_location"] == location or team["team_2_location"] == location:
            return team
    raise ValueError(f"No team found for location: {location}")


def extract_team_info(team: dict) -> dict:
    """Extracts team fields based on whether it's team_1 or team_2."""
    team_prefix = "team_1" if "team_1_team_id" in team else "team_2"

    return {
        "team_id": int(team[f"{team_prefix}_team_id"]),
        "name": team[f"{team_prefix}_name"],
        "logo_url": team[f"{team_prefix}_image"],
        "short_code": team[f"{team_prefix}_code"]
    }


def validate_timestamp(timestamp: str) -> None:
    """Validates that the timestamp is either implicit or explicit UTC format."""
    try:
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            if timestamp.endswith("Z"):
                timestamp = timestamp.replace("Z", "+00:00")
            datetime.fromisoformat(timestamp)
        except ValueError:
            raise ValueError(
                "Invalid 'start_time' format. Must be 'YYYY-MM-DD HH:MM:SS' or ISO 8601 UTC."
            )


def fetch_entity_name(entity: str, entity_id: int) -> str:
    """Fetches entity name (team/league/season) by ID using raw HTTPSConnection."""
    conn = HTTPSConnection("api.sportmonks.com")
    token = ENV["SPORTMONKS_API_TOKEN"]

    conn.request(
        "GET",
        f"/v3/football/{entity}/{entity_id}?api_token={token}",
        headers={}
    )
    res = conn.getresponse()
    body = res.read().decode("utf-8")
    conn.close()

    if res.status != 200:
        raise ValueError(
            f"Failed to fetch {entity} with ID {entity_id}: {res.status} {res.reason}")

    data = loads(body)
    if "data" not in data or "name" not in data["data"]:
        raise KeyError(
            f"Invalid response for {entity} with id: {entity_id}:{data}"
        )

    return data["data"]["name"]


def check_entity_in_db(conn: connection, table: str,  id_col: str, name_col: str, entity_id: int) -> str | None:
    """Checks if an entity exists in the DB and returns its name if found."""
    with conn.cursor() as cur:
        query = f"SELECT {name_col} FROM {table} WHERE {id_col} = %s"
        cur.execute(query, (entity_id,))
        result = cur.fetchone()
        cur.close()
    return result[0] if result else None


def check_competition_exists(conn: connection, competition_id: int) -> tuple[str, bool]:
    """Checks if the competition already exists in the database."""
    competition_name = check_entity_in_db(
        conn, "competition", "competition_id", "competition_name", competition_id)
    insert_competition = not competition_name
    if insert_competition:
        competition_name = fetch_entity_name("leagues", competition_id)

    return competition_name, insert_competition


def check_season_exists(conn: connection, season_id: int) -> tuple[str, bool]:
    """Checks if the season already exists in the database."""
    season_name = check_entity_in_db(
        conn, "season", "season_id", "season_name", season_id)

    insert_season = not season_name
    if insert_season:
        season_name = fetch_entity_name("seasons", season_id)

    return season_name, insert_season


def check_team_exists(conn: connection, team: dict) -> bool:
    """Checks if a team exists in the database and returns insert flag."""
    team_prefix = "team_1" if "team_1_team_id" in team else "team_2"
    team_id = int(team[f"{team_prefix}_team_id"])

    team_name = check_entity_in_db(
        conn, "team", "team_id", "team_name", team_id)
    insert_needed = not team_name

    if insert_needed:
        team_name = fetch_entity_name("teams", team_id)
        team[f"{team_prefix}_name"] = team_name

    return insert_needed


def validate_and_transform_data(event: dict, conn: connection) -> dict:
    """Validates and extracts structured match data from the event."""
    validate_required_keys(event)
    validate_timestamp(event["start_time"])

    team1, team2 = validate_team_data(event["team_data"])
    home_team = get_team_by_location(team1, team2, "home")
    away_team = get_team_by_location(team1, team2, "away")

    competition_id = int(event["league_id"])
    season_id = int(event["season_id"])

    competition_id = int(event["league_id"])
    competition_name, insert_competition = check_competition_exists(
        conn, competition_id)

    season_id = int(event["season_id"])
    season_name, insert_season = check_season_exists(conn, season_id)

    insert_home_team = check_team_exists(conn, home_team)
    insert_away_team = check_team_exists(conn, away_team)
    conn.close()

    return {
        "match_id": int(event["match_id"]),
        "match_date": event["start_time"],
        "competition_id": competition_id,
        "competition_name": competition_name,
        "season_id": season_id,
        "season_name": season_name,
        "home_team": extract_team_info(home_team),
        "away_team": extract_team_info(away_team),
        "insert_competition": insert_competition,
        "insert_season": insert_season,
        "insert_home_team": insert_home_team,
        "insert_away_team": insert_away_team
    }
