import logging
from json import dumps

from dotenv import load_dotenv

from extract_transform import validate_and_transform_data
from load_data import load_master_data


def configure_logger() -> logging.Logger:
    """Sets up the logger."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def lambda_handler(event, context):
    """Lambda entry point for processing and storing match master data."""

    try:
        load_dotenv()
        logger = configure_logger()
        logger.info("Received match info")

        transformed_data = validate_and_transform_data(event)
        logger.info("Transformed data")

        load_master_data(transformed_data)
        logger.info("Data loaded successfully.")

        return {
            "statusCode": 200,
            "body": dumps({
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

    mock_event = {
        "match_id": 19367875,
        "league_id": 1034,
        "season_id": 25044,
        "fixture_name": "Gwangju vs Seoul",
        "start_time": "2025-06-13 10:30:00",
        "team_data": [
            {
                "team_1_team_id": 4370,
                "team_1_name": "Gwangju",
                "team_1_code": None,
                "team_1_image": "https://cdn.sportmonks.com/images/soccer/teams/18/4370.png",
                "team_1_location": "home"
            },
            {
                "team_2_team_id": 672,
                "team_2_name": "Seoul",
                "team_2_code": None,
                "team_2_image": "https://cdn.sportmonks.com/images/soccer/teams/0/672.png",
                "team_2_location": "away"
            }
        ]
    }
    transformed_data = validate_and_transform_data(mock_event)
    load_master_data(transformed_data)
    print("Match successfully seeded.")
    """
