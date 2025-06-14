"""Pipeline Script"""

from os import environ as ENV
from http.client import HTTPSConnection

from dotenv import load_dotenv


from extract import run_extract
from transform import get_dataframe_from_json, get_dataframe_from_response, transform_data
from load import get_connection, upload_all_data

if __name__ == "__main__":

    load_dotenv()

    api_token = ENV["TOKEN"]
    api_conn = HTTPSConnection("api.sportmonks.com")
    db_conn = get_connection()

    raw_data = run_extract(19422412, api_token, api_conn)

    df = get_dataframe_from_response(raw_data)
    df = get_dataframe_from_json("match_19348525/scrape_1.json")
    try:
        minute_df, event_df, flags = transform_data(df)
    except IndexError as e:
        print("Game has not started yet.")
        exit()

    upload_all_data(minute_df, db_conn, event_df)
