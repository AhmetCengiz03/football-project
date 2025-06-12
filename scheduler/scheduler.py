"""Scheduler that runs daily to create schedules for today's matches."""
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
    """Get the fixtures happening today."""
    date = datetime.now().strftime('%Y-%m-%d')
    conn.request(
        "GET", f"/v3/football/fixtures/date/{
            date}?api_token={config["API_KEY"]}&include=participants")
    res = conn.getresponse()
    data = res.read()
    data_str = data.decode("utf-8")

    if res.status == 200:
        return loads(data_str)["data"]
    return {"error": True,
            "status": res.status,
            "reason": res.reason}


def get_data_from_fixtures(conn: HTTPSConnection, config: dict) -> list[dict]:
    """Get today's fixtures and extract relevant data."""

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
            "team_data": [{"team_1_team_id": team_1_team_id, "team_1_name": team_1_name,
                           "team_1_code": team_1_code, "team_1_image": team_1_image,
                           "team_1_location": team_1_location},
                          {"team_2_team_id": team_2_team_id, "team_2_name": team_2_name,
                           "team_2_code": team_2_code, "team_2_image": team_2_image,
                           "team_2_location": team_2_location}]
        })
    return matches_info


def manage_schedule_groups(scheduler_client: client, current_group: str) -> None:
    """Create current group and cleanup old ones."""
    try:
        scheduler_client.create_schedule_group(Name=current_group)
        logging.info("Created schedule group: %s", current_group)
    except scheduler_client.exceptions.ConflictException:
        logging.info("Schedule group %s already exists", current_group)

    try:
        current_date = datetime.now().strftime('%Y-%m-%d')
        yesterday_date = (datetime.now() - timedelta(days=1)
                          ).strftime('%Y-%m-%d')
        keep_groups = {f"c17-football-{current_date}-fixtures",
                       f"c17-football-{yesterday_date}-fixtures"}

        paginator = scheduler_client.get_paginator("list_schedule_groups")
        for page in paginator.paginate():
            for group in page["ScheduleGroups"]:
                group_name = group["Name"]
                if (group_name.startswith("c17-football-") and
                    group_name.endswith("-fixtures") and
                        group_name not in keep_groups):

                    scheduler_client.delete_schedule_group(Name=group_name)
                    logging.info("Deleted old schedule group: %s}", group_name)
    except Exception as e:
        logging.error("Error during group cleanup: %s", e)


def format_team_codes(team_1: str, team_2: str) -> str:
    """Format team codes for schedule name."""
    team_1_raw = team_1["team_1_code"] or team_1.get(
        "team_1_name", "unknown")
    team_2_raw = team_2["team_2_code"] or team_2.get(
        "team_2_name", "unknown")

    team_1_clean = sub(r'[^a-zA-Z0-9]', '', team_1_raw).lower()
    team_2_clean = sub(r'[^a-zA-Z0-9]', '', team_2_raw).lower()
    return f"{team_1_clean}-{team_2_clean}"[:50]


def create_match_schedule(scheduler_client: client, match: dict,
                          group_name: str, config: dict) -> None:
    """Create a single match schedule."""
    start_time = datetime.strptime(
        match["start_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    end_time = start_time + timedelta(hours=3)

    formatted_codes = format_team_codes(
        match["team_data"][0], match["team_data"][1])

    schedule_name = f"c17-football-{formatted_codes}"
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
        logging.info("Created schedule: %s", schedule_name)

    except scheduler_client.exceptions.ConflictException:
        logging.info("Schedule %s already exists", schedule_name)


def process_daily_schedules(config: dict) -> dict:
    """Main processing function."""
    configure_logger()

    current_date = datetime.now().strftime('%Y-%m-%d')
    group_name = f"c17-football-{current_date}-fixtures"

    scheduler_client = client("scheduler",
                              aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                              aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])

    api_conn = HTTPSConnection("api.sportmonks.com")
    fixtures = get_data_from_fixtures(api_conn, config)
    api_conn.close()

    if not fixtures:
        return {"statusCode": 200, "body": "No fixtures found today", "matches": []}

    manage_schedule_groups(scheduler_client, group_name)

    for match in fixtures:
        create_match_schedule(scheduler_client, match, group_name, config)

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
    return process_daily_schedules(ENV)


if __name__ == "__main__":
    load_dotenv()
    result = process_daily_schedules(ENV)
    print(result["matches"])
