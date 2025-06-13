import json
import logging

from json import dumps

from dotenv import load_dotenv

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
            "body": dumps({
                "message": "Initial match data processed and inserted successfully.",
                "match_id": transformed_data["match_id"]
            })
        }

    except Exception as e:
        logger.error("Insert master data pipeline failed: %s", str(e))
        raise RuntimeError("Error at runtime.")


if __name__ == "__main__":

    pass
