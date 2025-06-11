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

    for fixture in data:
        match_id = fixture["id"]
        league_id = fixture["league_id"]
        season_id = fixture["season_id"]
        fixture_name = fixture["name"]
        fixture_start_time = fixture["starting_at"]
        home_participant_data = fixture["participants"][0]
        away_participant_data = fixture["participants"][1]

    return [{"name": fixture["name"], "start": fixture["starting_at"], ""} for fixture in data]


def connect_to_scheduler_client(config: dict) -> client:
    """Connects to the Eventbridge scheduler."""
    return client("scheduler", aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])


def create_event_bridge_schedules(fixtures: list[dict], scheduler_client: client, config: dict) -> list[dict]:
    """Creates Eventbridge schedules for each fixture."""
    results = []

    for fixture in fixtures:
        try:
            start_time = fixture["start"]


if __name__ == "__main__":
    load_dotenv()
    scheduler_client = connect_to_scheduler_client(ENV)
    api_conn = HTTPSConnection("api.sportmonks.com")
    fixtures = get_start_times_from_fixtures(api_conn, ENV)
    print(type(scheduler_client))
