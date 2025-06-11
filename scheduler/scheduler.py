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


def get_start_times_from_fixtures(conn: HTTPSConnection, config: dict) -> str:
    """Get the date from the fixtures"""
    data = get_all_daily_fixtures(conn, config)

    return [{"name": fixture["name"], "start": fixture["starting_at"]} for fixture in data]


def connect_to_scheduler_client(config: dict) -> client:
    """Connects to the Eventbridge scheduler."""
    return client("scheduler", aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])


def create_event_bridge_schedules(fixtures: list[dict], scheduler_client: clien):
    pass


if __name__ == "__main__":
    load_dotenv()
    scheduler_client = connect_to_scheduler_client(ENV)
    api_conn = HTTPSConnection("api.sportmonks.com")
    fixtures = get_start_times_from_fixtures(api_conn, ENV)
