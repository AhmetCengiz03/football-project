"""Validates and transforms match data, checking for existing
records in the database or fetching from the API if missing."""
from datetime import datetime, timezone
from http.client import HTTPSConnection
from json import loads
from os import environ as ENV

from dotenv import load_dotenv

import psycopg2
from psycopg2.extensions import connection


def get_db_connection() -> connection:
    """Creates and returns a connection to the PostgreSQL
    database using environment variables."""
    return psycopg2.connect(
        dbname=ENV["DB_NAME"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"]
    )


def validate_required_values(event: dict) -> None:
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


def get_home_away_team(team: dict, location: str) -> dict | None:
    """Returns the team dict if its location matches 'home' or 'away'."""
    for key in team:
        if "location" in key and team[key] == location:
            return team

    return None


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


def fetch_entity_name_from_api(entity: str, entity_id: int) -> str:
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
    if res.status != 200:
        raise Exception(
            f"Failed to fetch {entity} with ID {entity_id}: {res.status} {res.reason}")

    data = loads(body)
    if "data" not in data or "name" not in data["data"]:
        raise Exception(
            f"Invalid response for {entity} with id: {entity_id}:{data}"
        )
    conn.close()

    return data["data"]["name"]


def get_entity_name_if_exists(cur, table: str, entity_id: int, id_col: str, name_col: str) -> str | None:
    """Checks if an entity exists in the DB and returns its name if found."""
    query = f"SELECT {name_col} FROM {table} WHERE {id_col} = %s"
    cur.execute(query, (entity_id,))
    result = cur.fetchone()

    return result[0] if result else None


def validate_and_transform_data(event: dict) -> dict:
    """Validates and extracts structured match data from the event."""
    load_dotenv()
    validate_required_values(event)
    validate_timestamp(event["start_time"])

    team1, team2 = validate_team_data(event["team_data"])
    home_team = get_home_away_team(
        team1, "home") or get_home_away_team(team2, "home")
    away_team = get_home_away_team(
        team1, "away") or get_home_away_team(team2, "away")

    competition_id = int(event["league_id"])
    season_id = int(event["season_id"])

    conn = get_db_connection()
    cur = conn.cursor()

    competition_name = get_entity_name_if_exists(
        cur, "competition", competition_id, "competition_id", "competition_name")
    insert_competition = False
    if not competition_name:
        competition_name = fetch_entity_name_from_api(
            "leagues", competition_id)
        insert_competition = True

    season_name = get_entity_name_if_exists(
        cur, "season", season_id, "season_id", "season_name")
    insert_season = False
    if not season_name:
        season_name = fetch_entity_name_from_api("seasons", season_id)
        insert_season = True

    insert_home_team = False
    insert_away_team = False
    for team in [home_team, away_team]:
        team_prefix = "team_1" if "team_1_team_id" in team else "team_2"
        team_id = int(team[f"{team_prefix}_team_id"])

        team_name = get_entity_name_if_exists(
            cur, "team", team_id, "team_id", "team_name")
        if not team_name:
            team_name = fetch_entity_name_from_api(
                "teams", team_id)
        team[f"{team_prefix}_name"] = team_name
        if team is home_team:
            insert_home_team = True
        else:
            insert_away_team = True
    cur.close()
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
