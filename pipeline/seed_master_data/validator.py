from datetime import datetime, timezone
from typing import Dict, Tuple, List


def validate_required_values(event: Dict) -> None:
    """Validates that all required top-level fields are present in the event."""
    required_keys = ["match_id", "league_id", "season_id",
                     "start_time", "location", "team_data"]

    for key in required_keys:
        if key not in event:
            raise ValueError(f"Missing field: {key}.")


def validate_team_data(team_data: List[Dict]) -> Tuple[Dict, Dict]:
    """Checks that team_data contains two teams."""
    if not isinstance(team_data, list) or len(team_data) != 2:
        raise ValueError("Team data must contain exactly two teams.")

    return team_data[0], team_data[1]


def get_home_away_team(team: Dict, location: str) -> Dict | None:
    """Returns the team dict if its location matches 'home' or 'away'."""
    for key in team:
        if "location" in key and team[key] == location:
            return team
    return None


def extract_team_info(team: Dict) -> Dict:
    """Extracts team fields based on whether it's team_1 or team_2."""
    team_prefix = "team_1" if "team_1_team_id" in team else "team_2"

    return {
        "team_id": int(team[f"{team_prefix}_team_id"]),
        "name": team[f"{team_prefix}_name"],
        "logo_url": team[f"{team_prefix}_image"],
        "short_code": team[f"{team_prefix}_code"]
    }


def validate_timestamp(ts: str) -> None:
    """Validates that the timestamp is a valid ISO format string and in UTC."""
    try:
        if ts.endswith("Z"):
            ts = ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.utcoffset() != timezone.utc.utcoffset(dt):
            raise ValueError("Timestamp must be in UTC (offset +00:00).")
    except Exception:
        raise ValueError("Invalid 'start_time' timestamp format.")


def validate_match_master_data(event: Dict) -> Dict:
    """Validates and extracts structured match data from the event."""
    validate_required_values(event)
    validate_timestamp(event["start_time"])

    team1, team2 = validate_team_data(event["team_data"])

    home_team = get_home_away_team(
        team1, "home") or get_home_away_team(team2, "home")
    away_team = get_home_away_team(
        team1, "away") or get_home_away_team(team2, "away")

    if not home_team or not away_team:
        raise ValueError("Unable to identify both home and away teams.")

    return {
        "match_id": int(event["match_id"]),
        "match_date": event["start_time"],
        "competition_id": int(event["league_id"]),
        "competition_name": "TBD",
        "season_id": int(event["season_id"]),
        "season_name": "TBD",
        "home_team": extract_team_info(home_team),
        "away_team": extract_team_info(away_team)
    }
