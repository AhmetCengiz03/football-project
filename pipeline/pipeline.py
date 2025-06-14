"""Pipeline Script"""

from os import environ as ENV
from http.client import HTTPSConnection

from dotenv import load_dotenv


from extract import run_extract
from transform import get_dataframe_from_json, get_dataframe_from_response, transform_data
from load import get_connection, upload_all_data


def lambda_handler(event=None, context=None):
    """Runs the ETL Pipeline."""
    pass


if __name__ == "__main__":

    load_dotenv()

    api_token = ENV["TOKEN"]
    api_conn = HTTPSConnection(ENV["BASE_URL"])
    db_conn = get_connection()

    raw_data = run_extract(19422412, api_token, api_conn)

    # df = get_dataframe_from_response(raw_data)
    df = get_dataframe_from_json("match_19348525/scrape_1.json")

    if df["periods"].map(bool).any():
        minute_df, event_df, flags = transform_data(df)
        upload_all_data(minute_df, db_conn, event_df)

    else:
        print("Game has not started yet.")
