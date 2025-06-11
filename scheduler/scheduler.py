"""Scheduler that runs daily to create schedules for today's matches."""
from os import environ as ENV
from json import loads, load, dump
from datetime import datetime, timezone
from http.client import HTTPSConnection


from dotenv import load_dotenv


def get_all_daily_fixtures(date: str, conn: HTTPSConnection, config: dict) -> dict:
    """Get the fixtures happening today."""
    payload = ''
    headers = {}
    conn.request(
        "GET", f"/v3/football/fixtures/date/{date}?api_token={config["API_KEY"]}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data_str = data.decode("utf-8")

    if res.status == 200:
        return loads(data_str)["data"]
    return {"error": True,
            "status": res.status,
            "reason": res.reason}


def get_start_times_from_fixtures(data: list[dict]) -> str:
    """Get the date from the fixtures"""
    return [{"name": fixture["name"], "start": fixture["starting_at"]} for fixture in data]


if __name__ == "__main__":
    load_dotenv()
    api_conn = HTTPSConnection("api.sportmonks.com")
    all_fixtures = get_all_daily_fixtures('2025-06-11', api_conn, ENV)
    print(get_start_times_from_fixtures(all_fixtures))
