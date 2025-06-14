"""Pipeline Script"""

from os import environ as ENV
from http.client import HTTPSConnection

from dotenv import load_dotenv


from extract import run_extract
from transform import get_dataframe_from_response, transform_data
from load import get_connection, upload_all_data


def lambda_handler(event=None, context=None):
    """Runs the ETL Pipeline."""

    match_id = event["match_id"]

    api_token = ENV["TOKEN"]
    api_conn = HTTPSConnection(ENV["BASE_URL"])
    db_conn = get_connection()

    raw_data = run_extract(match_id, api_token, api_conn)
    api_conn.close()

    df = get_dataframe_from_response(raw_data)

    if df["periods"].map(bool).any():
        minute_df, event_df, flags = transform_data(df)
        upload_all_data(minute_df, db_conn, event_df)
        db_conn.close()

    else:
        print("Game has not started yet.")

        return {
            "status_code": 200,
            "body": "Game has not started yet.",
            "match_id": match_id
        }

    return {
        "status_code": 200,
        "body": flags,
        "match_id": match_id
    }


if __name__ == "__main__":

    load_dotenv()
