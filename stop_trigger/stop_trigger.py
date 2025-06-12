import logging
from datetime import datetime
from boto3 import client


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def delete_scheduler(schedule_name, group_name):
    """Delete the scheduler"""
    scheduler = client("scheduler")
    try:
        scheduler.delete_schedule(Name=schedule_name,
                                  GroupName=group_name)
        logging.info("Deleted schedule: %s", schedule_name)
    except scheduler.exceptions.ResourceNotFoundException:
        logging.info("Could not find and delete: %s", schedule_name)


def main():
    schedule_name = "c17-football-test-delete"
    today = datetime.now().strftime("%Y-%m-%d")
    group_name = f"c17-football-{today}-fixtures"
    delete_scheduler(schedule_name, group_name)


main()
