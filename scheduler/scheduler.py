"""Scheduler that runs daily to create schedules for tomorrow's matches."""
from os import environ as ENV
from json import loads, dumps
import logging
from http.client import HTTPSConnection
from re import sub
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from boto3 import client


def configure_logger() -> logging.Logger:
    """Sets up the logger."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def connect_to_scheduler_client(config: dict) -> client:
    """Connects to the Eventbridge scheduler."""
    return client("scheduler", aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])


def get_all_daily_fixtures(conn: HTTPSConnection, config: dict) -> dict:
    """Get the fixtures happening tomorrow."""
    date = (datetime.now(timezone.utc) +
            timedelta(days=1)).strftime('%Y-%m-%d')
    conn.request(
        "GET", f"/v3/football/fixtures/date/{date}?api_token={config[
            "API_KEY"]}&include=participants")
    res = conn.getresponse()
    data = res.read()
    data_str = data.decode("utf-8")

    if res.status == 200:
        return loads(data_str)["data"]
    return {"error": True,
            "status": res.status,
            "reason": res.reason}


def extract_team_data(team: dict, prefix: str) -> dict:
    """Extracts team info with a given prefix."""
    return {
        f"{prefix}_team_id": team["id"],
        f"{prefix}_name": team["name"],
        f"{prefix}_code": team["short_code"],
        f"{prefix}_image": team["image_path"],
        f"{prefix}_location": team["meta"]["location"]
    }


def get_single_fixture(fixture: dict) -> dict:
    """Gets a single fixture and extracts relevant data."""
    team_1 = extract_team_data(fixture["participants"][0], "team_1")
    team_2 = extract_team_data(fixture["participants"][1], "team_2")

    return {
        "match_id": fixture["id"],
        "league_id": fixture["league_id"],
        "season_id": fixture["season_id"],
        "fixture_name": fixture["name"],
        "start_time": fixture["starting_at"],
        "team_data": [team_1, team_2]
    }


def get_data_from_fixtures(conn: HTTPSConnection, config: dict) -> list[dict]:
    """Get today's fixtures and extract relevant data."""
    fixtures = get_all_daily_fixtures(conn, config)
    return [get_single_fixture(fixture) for fixture in fixtures]


def manage_schedule_groups(scheduler_client: client, current_group: str, schedule_prefix: str) -> None:
    """Create current group and cleanup old ones."""
    logger = configure_logger()
    try:
        scheduler_client.create_schedule_group(Name=current_group)
        logger.info("Created schedule group: %s", current_group)
    except scheduler_client.exceptions.ConflictException:
        logger.info("Schedule group %s already exists", current_group)

    try:
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        tomorrow_date = (datetime.now(timezone.utc) + timedelta(days=1)
                         ).strftime('%Y-%m-%d')
        keep_groups = {f"{schedule_prefix}-{current_date}-fixtures",
                       f"{schedule_prefix}-{tomorrow_date}-fixtures"}

        paginator = scheduler_client.get_paginator("list_schedule_groups")
        for page in paginator.paginate():
            for group in page["ScheduleGroups"]:
                group_name = group["Name"]
                if (group_name.startswith(schedule_prefix) and
                    group_name.endswith("-fixtures") and
                        group_name not in keep_groups):

                    scheduler_client.delete_schedule_group(Name=group_name)
                    logger.info("Deleted old schedule group: %s}", group_name)
    except Exception as e:
        logger.error("Error during group cleanup: %s", e)


def create_match_schedule(scheduler_client: client, match: dict,
                          group_name: str, config: dict, schedule_prefix: str) -> None:
    """Create a single match schedule."""
    logger = configure_logger()
    start_time = datetime.strptime(
        match["start_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    end_time = start_time + timedelta(hours=3)

    schedule_name = f"{schedule_prefix}-{match["match_id"]}"
    try:
        scheduler_client.create_schedule(
            Name=schedule_name,
            GroupName=group_name,
            ScheduleExpression='cron(* * * * ? *)',
            StartDate=start_time.isoformat(),
            EndDate=end_time.isoformat(),
            FlexibleTimeWindow={'Mode': 'OFF'},
            Target={
                'Arn': config["TARGET_ARN"],
                'RoleArn': config["ROLE_ARN"],
                'Input': dumps(match)
            },
            State='ENABLED',
            Description=f"Schedule for fixture: {match['fixture_name']}"
        )
        logger.info("Created schedule: %s", schedule_name)

    except scheduler_client.exceptions.ConflictException:
        logger.info("Schedule %s already exists", schedule_name)


def process_daily_schedules(config: dict, schedule_prefix: str) -> dict:
    """Main processing function."""
    tomorrow_date = (datetime.now(timezone.utc) +
                     timedelta(days=1)).strftime('%Y-%m-%d')
    group_name = f"{schedule_prefix}-{tomorrow_date}-fixtures"

    scheduler_client = client("scheduler",
                              aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                              aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])

    api_conn = HTTPSConnection("api.sportmonks.com")
    fixtures = get_data_from_fixtures(api_conn, config)
    api_conn.close()

    if not fixtures:
        return {"statusCode": 200, "body": "No fixtures found today", "matches": []}

    manage_schedule_groups(scheduler_client, group_name, schedule_prefix)

    for match in fixtures:
        create_match_schedule(scheduler_client, match,
                              group_name, config, schedule_prefix)

    return {"statusCode": 200, "body": f"Created {len(fixtures)} schedules in group {group_name}",
            "matches": fixtures}


def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    Args:
        event: Lambda event data
        context: Lambda context object

    Returns:
        Dictionary with status code and response body
    """
    return process_daily_schedules(ENV, 'c17-football')


if __name__ == "__main__":
    load_dotenv()
    result = process_daily_schedules(ENV, 'c17-football')
    # print(result["matches"])
