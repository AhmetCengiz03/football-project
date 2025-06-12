"""Scheduler that runs daily to create schedules for today's matches."""
from os import environ as ENV
from json import loads, dumps
import logging
from datetime import datetime
from http.client import HTTPSConnection
from re import sub
from datetime import timedelta, timezone

from dotenv import load_dotenv
from boto3 import client


def configure_logger() -> logging.Logger:
    """Sets up the logger."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)


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

        team_1_data = fixture["participants"][0]
        team_2_data = fixture["participants"][1]

        team_1_team_id = team_1_data["id"]
        team_1_name = team_1_data["name"]
        team_1_code = team_1_data["short_code"]
        team_1_image = team_1_data["image_path"]
        team_1_location = team_1_data["meta"]["location"]

        team_2_team_id = team_2_data["id"]
        team_2_name = team_2_data["name"]
        team_2_code = team_2_data["short_code"]
        team_2_image = team_2_data["image_path"]
        team_2_location = team_2_data["meta"]["location"]

        matches_info.append({
            "match_id": match_id,
            "league_id": league_id,
            "season_id": season_id,
            "fixture_name": fixture_name,
            "start_time": fixture_start_time,
            "team_data": [{"team_1_team_id": team_1_team_id, "team_1_name": team_1_name, "team_1_code": team_1_code, "team_1_image": team_1_image, "team_1_location": team_1_location},
                          {"team_2_team_id": team_2_team_id, "team_2_name": team_2_name, "team_2_code": team_2_code, "team_2_image": team_2_image, "team_2_location": team_2_location}]
        })
    return matches_info


def connect_to_scheduler_client(config: dict) -> client:
    """Connects to the Eventbridge scheduler."""
    return client("scheduler", aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])


def format_schedule_name(name: str) -> str:
    """Format fixture name to create a valid AWS schedule name."""
    name = name.lower().replace(" ", "-")
    return sub(r'[^a-z0-9\-]', '', name)[:64]


def create_schedule(client: client, match_info: dict, config: dict) -> None:
    """Create schedule for a single match."""

    start_time = datetime.strptime(
        match_info["start_time"], "%Y-%m-%d %H:%M:%S")
    start_time_utc = start_time.replace(tzinfo=timezone.utc)
    end_time_utc = start_time_utc + timedelta(hours=3)

    schedule_name = format_schedule_name(match_info["fixture_name"])

    client.create_schedule(
        Name=schedule_name,
        ScheduleExpression='cron(* * * * ? *)',
        StartDate=start_time_utc.isoformat(),
        EndDate=end_time_utc.isoformat(),
        FlexibleTimeWindow={'Mode': 'OFF'},
        Target={
            'Arn': config["TARGET_ARN"],
            'RoleArn': config["ROLE_ARN"],
            'Input': dumps(match_info)
        },
        State='ENABLED',
        Description=f"Schedule for fixture: {match_info["fixture_name"]}."
    )


def create_schedule_for_all_matches(client: client, matches: list[dict], config: dict) -> None:
    """Create a 3 hour schedule triggering every minute for the match."""
    for match in matches:
        create_schedule(client, match, config)


def cleanup_old_schedules(client: client) -> None:
    """Clean up old schedules that are no longer needed."""
    paginator = client.get_paginator("list_schedules")
    pages = paginator.paginate()

    now_utc = datetime.now(timezone.utc)

    for page in pages:
        schedules = page["Schedules"]
        for schedule in schedules:
            if schedule["EndDate"] < now_utc:
                client.delete_schedule(Name=schedule["Name"])


def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    Args:
        event: Lambda event data
        context: Lambda context object

    Returns:
        Dictionary with status code and response body
    """

    scheduler_client = connect_to_scheduler_client(ENV)
    api_conn = HTTPSConnection("api.sportmonks.com")

    fixtures = get_data_from_fixtures(api_conn, ENV)
    api_conn.close()

    if not fixtures:
        return {"statusCode": 200, "body": "No fixtures found today"}

    # cleanup_old_schedules(scheduler_client)
    create_schedule_for_all_matches(scheduler_client, fixtures, ENV)

    return {"statusCode": 200, "body": f"Created {len(fixtures)} schedules"}


if __name__ == "__main__":
    configure_logger()
    load_dotenv()
    scheduler_client = connect_to_scheduler_client(ENV)
    api_conn = HTTPSConnection("api.sportmonks.com")

    fixtures = get_data_from_fixtures(api_conn, ENV)
    if not fixtures:
        print("No fixtures found today")
        exit(0)

    # cleanup_old_schedules(scheduler_client)
    create_schedule_for_all_matches(scheduler_client, fixtures, ENV)

    api_conn.close()
