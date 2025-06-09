"""Scraping a live game with the Sportsmonks API."""

from os import environ as ENV
import http.client

from dotenv import load_dotenv


def scrape_live_by_id(fixture_id: int, token: str, conn: http.client.HTTPSConnection) -> dict:
    """Returns a dict of scraped information."""

    payload = ''
    headers = {}
    conn.request(
        "GET", f"/v3/football/fixtures/{fixture_id}?api_token={token}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")


if __name__ == "__main__":

    load_dotenv()
    api_token = ENV["TOKEN"]

    api_conn = http.client.HTTPSConnection("api.sportmonks.com")
    match_id = 19375375
    print(scrape_live_by_id(match_id, api_token, api_conn))

    api_conn.close()
