"""Scheduler that runs daily to create schedules for today's matches."""
from os import environ as ENV
from json import loads, load, dump
from datetime import datetime
from http.client import HTTPSConnection


from dotenv import load_dotenv
from boto3 import client


def get_all_daily_fixtures(conn: HTTPSConnection, config: dict) -> dict:
    """Get the fixtures happening today."""
    date = datetime.now().strftime('%Y-%m-%d')
    conn.request(
        "GET", f"/v3/football/fixtures/date/{date}?api_token={config["API_KEY"]}&include=participants")
    res = conn.getresponse()
    data = res.read()
    data_str = data.decode("utf-8")

    if res.status == 200:
        return loads(data_str)["data"]
    return {"error": True,
            "status": res.status,
            "reason": res.reason}


def get_data_from_fixtures(conn: HTTPSConnection, config: dict) -> list[dict]:
    """Get the date from the fixtures"""
    data = get_all_daily_fixtures(conn, config)
    matches_info = []
    for fixture in data:
        match_id = fixture["id"]
        league_id = fixture["league_id"]
        season_id = fixture["season_id"]
        fixture_name = fixture["name"]
        fixture_start_time = fixture["starting_at"]
        location = fixture["meta"]["location"]
        home_data = fixture["participants"][0]
        away_data = fixture["participants"][1]

        home_team_id = home_data["id"]
        home_name = home_data["name"]
        home_code = home_data["short_code"]
        home_image = home_data["image_path"]

        away_team_id = away_data["id"]
        away_name = away_data["name"]
        away_code = away_data["short_code"]
        away_image = away_data["image_path"]

        matches_info.append({
            "match_id": match_id,
            "league_id": league_id,
            "season_id": season_id,
            "fixture_name": fixture_name,
            "start_time": fixture_start_time,
            "location": location,
            "team_data": [{"home_team_id": home_team_id, "home_name": home_name, "home_code": home_code, "home_image": home_image},
                          {"away_team_id": away_team_id, "away_name": away_name, "away_code": away_code, "away_image": away_image}]
        })
    return matches_info


def connect_to_scheduler_client(config: dict) -> client:
    """Connects to the Eventbridge scheduler."""
    return client("scheduler", aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])


if __name__ == "__main__":
    load_dotenv()
    scheduler_client = connect_to_scheduler_client(ENV)
    api_conn = HTTPSConnection("api.sportmonks.com")
    print(get_all_daily_fixtures(api_conn, ENV)[3])
    fixtures = get_data_from_fixtures(api_conn, ENV)
