"""Script to delete schedulers after a game has finished."""
import logging
from os import environ as ENV

from re import sub
from dotenv import load_dotenv
from boto3 import client
from json import dumps


def configure_logger() -> logging.Logger:
    """Sets up the logger."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def connect_to_scheduler_client(config: dict) -> client:
    """Connects to the EventBridge scheduler."""
    return client("scheduler", aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])


def format_team_names(team_1: str, team_2: str) -> str:
    """Format team names for schedule name."""

    team_1_clean = sub(r'[^a-zA-Z0-9]', '', team_1).lower()
    team_2_clean = sub(r'[^a-zA-Z0-9]', '', team_2).lower()

    return f"{team_1_clean}-{team_2_clean}"[:50]


def get_schedule_groups(scheduler_client: client, schedule_prefix: str) -> list[str]:
    """Get the group names of the schedulers."""
    schedule_groups = []
    paginator = scheduler_client.get_paginator("list_schedule_groups")
    for page in paginator.paginate():
        for group in page["ScheduleGroups"]:
            group_name = group["Name"]
            if (group_name.startswith(schedule_prefix) and
               group_name.endswith("-fixtures")):
                schedule_groups.append(group_name)
    return schedule_groups


def delete_scheduler(scheduler: client, schedule_name: str, group_names: list[str]) -> None:
    """Delete the specified scheduler."""
    for group_name in group_names:
        try:
            scheduler.delete_schedule(Name=schedule_name,
                                      GroupName=group_name)
            logging.info("Deleted schedule: %s", schedule_name)
        except scheduler.exceptions.ResourceNotFoundException:
            logging.info("Could not find and delete: %s", schedule_name)


def process_schedule_deletion(config: dict, home_team: str, away_team: str, schedule_prefix: str) -> None:
    """Main processing function."""
    configure_logger()
    scheduler = client("scheduler", aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                       aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])
    group_names = get_schedule_groups(scheduler, schedule_prefix)
    formatted_codes = format_team_names(home_team, away_team)
    schedule_name = f"{schedule_prefix}-{formatted_codes}"
    delete_scheduler(scheduler, schedule_name, group_names)


def lambda_handler(event, context):
    """
        Main Lambda handler function
        Parameters:
            event: Dict containing home_team, away team and match_end flag
        Returns:
            Dictionary with status code and response body
    """
    try:
        logger.info("Received event: %s", dumps(event))
        home_team = event.get("home_team")
        away_team = event.get("away_team")
        match_end = event.get("match_end")

        if not all([home_team, away_team, match_end]):
            raise ValueError("home_team, away_team and match end are required")

        if match_end == True:
            process_schedule_deletion(
                ENV, home_team, away_team, "c17-football")
            return {
                "status_Code": 200,
                "message": "Schedule deleted successfully"
            }
        return {
            "status_Code": 200,
            "message": "Game not ended yet"
        }

    except Exception as e:
        logger.error("Error in lambda_handler: %s", str(e))
        return {
            "statusCode": 500,
            "body": {
                "error": str(e),
                "message": "Failed to delete schedule"
            }
        }


if __name__ == "__main__":
    load_dotenv()
    HOME_TEAM = "home"
    AWAY_TEAM = "away"
    process_schedule_deletion(ENV, HOME_TEAM, AWAY_TEAM, "c17-football")
