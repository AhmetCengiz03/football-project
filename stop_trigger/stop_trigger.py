"""Script to delete schedulers after a game has finished."""
from logging import getLogger, Logger
from os import environ as ENV
from json import dumps

from dotenv import load_dotenv
from boto3 import client


def connect_to_scheduler_client(config: dict) -> client:
    """Connects to the EventBridge scheduler."""
    return client("scheduler", aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"],
                  aws_session_token=config["AWS_SESSION_TOKEN"])


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
    logger = getLogger()
    for group_name in group_names:
        try:
            scheduler.delete_schedule(Name=schedule_name,
                                      GroupName=group_name)
            logger.info("Deleted schedule: %s", schedule_name)
        except scheduler.exceptions.ResourceNotFoundException:
            logger.info("Could not find and delete: %s", schedule_name)


def process_schedule_deletion(config: dict, match_id: int, schedule_prefix: str) -> None:
    """Main processing function."""
    scheduler = connect_to_scheduler_client(config)
    group_names = get_schedule_groups(scheduler, schedule_prefix)
    schedule_name = f"{schedule_prefix}-{match_id}"
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
        load_dotenv()
        logger = getLogger()
        logger.info("Received event: %s", dumps(event))
        match_id = event.get("match_id")

        if not match_id:
            raise ValueError("home_team, away_team and match end are required")

        process_schedule_deletion(ENV, match_id, "c17-football")
        return {
            "status_code": 200,
            "message": "Schedule deleted successfully"
        }

    except Exception as e:
        logger.error("Error in lambda_handler: %s", str(e))
        return {
            "status_code": 500,
            "body": {
                "error": str(e),
                "message": "Failed to delete schedule"
            }
        }


if __name__ == "__main__":
    load_dotenv()
    process_schedule_deletion(ENV, 123, "c17-football")
