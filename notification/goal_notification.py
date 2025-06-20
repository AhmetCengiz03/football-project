"""Goal notification script for our lambda."""

from os import environ as ENV
import logging

import boto3
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)


def lambda_handler(event=None, context=None):
    """Lambda function for the creation of goal notifications."""

    client = boto3.client('sns')

    flags = event["flags"]
    goal_info = flags.get("goal_check", [])

    if not goal_info:

        logger.info("No new goals found.")
        return {
            "status": "No new goals found."
        }

    messages_sent = []
    for goal in goal_info:

        goal_message = create_goal_message(goal)
        logger.info("Created goal message: %s", goal_message)

        response = client.publish(
            TopicArn=ENV["TOPIC_ARN"],
            Message=goal_message,
            Subject="Goal scored!"

        )
        messages_sent.append(response["MessageId"])

    return {
        "status_code": 200,
        "message_ids": messages_sent,
        "status": f"{len(messages_sent)} goal notifications sent.",
    }


def create_goal_message(goal: dict) -> str:
    """Creates a goal message from given goal information."""

    return f"GOAL! {goal['minute']}' {goal["player_name"]} scores for {goal["team_id"]}."


if __name__ == "__main__":

    load_dotenv()
