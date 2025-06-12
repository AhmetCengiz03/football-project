import os
import json
import logging
from extract_transform import validate_and_transform_data
from load_data import load_master_data

import requests
from dotenv import load_dotenv

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Lambda entry point for processing and storing match master data."""

    try:
        logger.info("Received match info: %s", json.dumps(event))

        transformed_data = validate_and_transform_data(event)
        logger.info("Transformed data: %s", transformed_data)

        load_master_data(transformed_data)
        logger.info("Data loaded successfully.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Initial match data processed and inserted successfully.",
                "match_id": transformed_data["match_id"]
            })
        }

    except Exception as e:
        logger.error("Insert master data pipeline failed: %s", str(e))
        raise RuntimeError("Error at runtime.")


if __name__ == "__main__":
    """
    load_dotenv()
    token = os.environ["SPORTMONKS_API_TOKEN"]
    resp = requests.get(
        f"https://api.sportmonks.com/v3/football/seasons?api_token={token}&page=2")
    print(resp.json())
    """
    mock_event = {
        "match_id": 6004321,
        "league_id": 567,
        "season_id": 23676,
        "fixture_name": "Mirandés vs Racing Santander",
        "start_time": "2025-06-12T19:00:00Z",
        "location": "home",
        "team_data": [
            {
                    "team_1_team_id": 149,
                    "team_1_name": "Mirandés",
                    "team_1_code": "CDM",
                    "team_1_image": "https://api.sportmonks.com/images/soccer/teams/149.png",
                    "team_1_location": "home"
            },
            {
                "team_2_team_id": 2835,
                "team_2_name": "Racing Santander",
                "team_2_code": "RAC",
                "team_2_image": "https://api.sportmonks.com/images/soccer/teams/2835.png",
                "team_2_location": "away"
            }
        ]
    }

    transformed_data = validate_and_transform_data(mock_event)
    load_master_data(transformed_data)
    print("Pipeline executed locally with mock event.")
