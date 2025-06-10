"""Scraping a live game with the Sportsmonks API."""

from os import environ as ENV, path
from datetime import datetime, timezone
import json
import time
import http.client

from dotenv import load_dotenv


def scrape_live_match(match_identifier: str | int,
                      token: str, conn: http.client.HTTPSConnection) -> dict:
    """Returns a dict of scraped information for a specified match."""

    payload = ''
    headers = {}

    if isinstance(match_identifier, str):
        url = f"livescores/inplay?api_token={token}&include=statistics&filters=participantSearch:{match_identifier}"
    elif isinstance(match_identifier, int):
        url = f"fixtures/{match_identifier}?api_token={token}"
    else:
        raise TypeError(
            f"{match_identifier} is not a valid string or integer.")

    conn.request(
        "GET", f"/v3/football/{url}", payload, headers)
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


def run_scraper(filename: str, match_identifier: str | int,
                token: str, conn: http.client.HTTPSConnection):
    """Runs the scraper every 60 seconds until cancelled."""

    scrape_count = 1

    while True:
        print(f"Scraping... {scrape_count}")

        data = scrape_live_match(match_identifier, token, conn)
        print(data)
        scrape_count += 1
        write_to_file(filename, data)
        time.sleep(60)


if __name__ == "__main__":

    load_dotenv()
    api_token = ENV["TOKEN"]
    api_conn = http.client.HTTPSConnection("api.sportmonks.com")

    # Replace with a fixture id, or a team name from the game e.g. 19375375 or "Scotland"
    identify_match = 19375375
    run_scraper("scrape_output.json", identify_match, api_token, api_conn)

    api_conn.close()
