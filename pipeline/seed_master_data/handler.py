from logging import getLogger
from json import dumps
from os import environ as ENV

from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extensions import connection

from extract_transform import validate_and_transform_data
from load_data import load_master_data


def get_db_connection(config: dict) -> connection:
    """Creates and returns a connection to the PostgreSQL
    database using environment variables."""
    return connect(
        dbname=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"],
        port=config["DB_PORT"]
    )


def lambda_handler(event, context):
    """Lambda entry point for processing and storing match master data."""

    try:
        load_dotenv()
        logger = getLogger()
        logger.info("Received match info")
        conn = get_db_connection(ENV)

        transformed_data = validate_and_transform_data(event, conn)
        logger.info("Transformed data")

        load_master_data(transformed_data, conn)
        logger.info("Data loaded successfully.")
        conn.close()
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
    event = {'match_id': 19367875, 'league_id': 1034, 'season_id': 25044, 'fixture_name': 'Gwangju vs Seoul', 'start_time': '2025-06-13 10:30:00', 'team_data': [{'team_1_team_id': 4370, 'team_1_name': 'Gwangju', 'team_1_code': None, 'team_1_image': 'https://cdn.sportmonks.com/images/soccer/teams/18/4370.png', 'team_1_location': 'home'}, {
        'team_2_team_id': 672, 'team_2_name': 'Seoul', 'team_2_code': None, 'team_2_image': 'https://cdn.sportmonks.com/images/soccer/teams/0/672.png', 'team_2_location': 'away'}]}
    load_dotenv()
    logger = getLogger()
    logger.info("Received match info")
    conn = get_db_connection(ENV)

    transformed_data = validate_and_transform_data(event, conn)
    logger.info("Transformed data")

    load_master_data(transformed_data, conn)
    logger.info("Data loaded successfully.")
