"""Scraping a live game with the Sportsmonks API."""

from os import environ as ENV, path
from datetime import datetime, timezone
import json
import time
import http.client

from dotenv import load_dotenv


def scrape_live_by_id(fixture_id: int, token: str, conn: http.client.HTTPSConnection) -> dict:
    """Returns a dict of scraped information for a given fixture_id."""

    payload = ''
    headers = {}
    conn.request(
        "GET", f"/v3/football/fixtures/{fixture_id}?api_token={token}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data_str = data.decode("utf-8")

    return json.loads(data_str)


def scrape_live_by_name(team_name: str, token: str, conn: http.client.HTTPSConnection) -> dict:
    """Returns a dict of scraped information for a given team name."""

    payload = ''
    headers = {}
    conn.request(
        "GET", f"/v3/football/livescores/inplay?api_token={token}\&include=statistics&filters=participantSearch:{team_name}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data_str = data.decode("utf-8")

    return json.loads(data_str)


def write_to_file(filename: str, data: dict) -> None:
    """Appends scraped data to a json file."""

    data = prepare_data(data)

    if not path.exists(filename) or path.getsize(filename) == 0:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([data], f, indent=4)
    else:

        with open(filename, "r+", encoding="utf-8") as f:
            file_data = json.load(f)
            file_data.append(data)
            f.seek(0)
            json.dump(file_data, f, indent=4)


def prepare_data(data: dict) -> dict:
    """
    Removes unwanted keys from our api call and adds info.
    NOTE: Whilst this is transformative, we need to capture a timestamp of when it was
    extracted at the time of extraction, and we don't want to write unnecessary keys to 
    our file each time. I've kept this minimal.
    """
    for dict_key in ["subscription", "timezone"]:
        data.pop(dict_key, None)

    if "rate_limit" in data:
        data["rate_limit"]["timestamp"] = datetime.now(
            timezone.utc).timestamp()
    else:
        raise KeyError("rate_limit not in data.")

    return data


def run_scraper(filename: str, specific_team: str | int,
                token: str, conn: http.client.HTTPSConnection):
    """Runs the scraper every 60 seconds until cancelled."""

    scrape_count = 1
    while True:
        print(f"Scraping... {scrape_count}")

        if isinstance(specific_team, str):
            data = scrape_live_by_name(specific_team, token, conn)
        elif isinstance(specific_team, int):
            data = scrape_live_by_id(specific_team, token, conn)
        else:
            raise TypeError(
                f"{specific_team} is not a valid string or integer.")

        scrape_count += 1
        write_to_file(filename, data)
        time.sleep(60)


if __name__ == "__main__":

    load_dotenv()
    api_token = ENV["TOKEN"]

    api_conn = http.client.HTTPSConnection("api.sportmonks.com")
    # Replace with a fixture id, or a team name from the game e.g. "Scotland"
    match_identifier = 19375375

    run_scraper("scrape_output.json", match_identifier, api_token, api_conn)

    api_conn.close()
