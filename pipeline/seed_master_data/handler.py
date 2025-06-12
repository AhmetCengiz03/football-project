import json
import logging
from extract_transform import validate_and_transform_data
from load_data import load_master_data

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
    mock_event = {
        "match_id": 1234,
        "league_id": 8,
        "season_id": 3,
        "start_time": "2025-09-10T15:00:00Z",
        "location": "home",
        "team_data": [
            {
                "team_1_team_id": 1,
                "team_1_name": "Team A",
                "team_1_code": "TMA",
                "team_1_image": "https://example.com/logoA.png",
                "team_1_location": "home"
            },
            {
                "team_2_team_id": 2,
                "team_2_name": "Team B",
                "team_2_code": "TMB",
                "team_2_image": "https://example.com/logoB.png",
                "team_2_location": "away"
            }
        ]
    }

    transformed_data = validate_and_transform_data(mock_event)
    load_master_data(transformed_data)
    print("Pipeline executed locally with mock event.")
