"""Scraping a live game with the Sportsmonks API."""

from os import environ as ENV, path, makedirs
from datetime import datetime, timezone
from json import loads, load, dump
from time import sleep
from http.client import HTTPSConnection

from dotenv import load_dotenv


def scrape_live_match(url: str, conn: HTTPSConnection) -> dict:
    """Returns a dict of scraped information for a specified match."""

    payload = ''
    headers = {}

    conn.request(
        "GET", f"/v3/football/{url}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data_str = data.decode("utf-8")

    if res.status == 200:
        return loads(data_str)
    return {"error": True,
            "status": res.status,
            "reason": res.reason}


def build_scrape_url(match_identifier: str | int, token: str) -> str:
    """Returns the url required based on the given identifier."""

    if isinstance(match_identifier, str):
        url = f"livescores/inplay?api_token={token}&include=statistics;periods;comments&filters=participantSearch:{match_identifier}"
    elif isinstance(match_identifier, int):
        url = f"fixtures/{match_identifier}?api_token={token}"
    else:
        raise TypeError(
            f"{match_identifier} is not a valid string or integer.")

    return url


def write_to_file_combined(filename: str, data: dict) -> None:
    """Appends scraped data to a json file."""

    if not path.exists(filename) or path.getsize(filename) == 0:
        with open(filename, 'w', encoding='utf-8') as f:
            dump([data], f, indent=4)
    else:

        with open(filename, "r+", encoding="utf-8") as f:
            file_data = load(f)
            file_data.append(data)
            f.seek(0)
            dump(file_data, f, indent=4)


def write_to_file(filename: str, data: dict) -> None:
    """Writes data to a json file."""

    with open(filename, "w", encoding="utf-8") as f:
        dump(data, f, indent=4)


def prepare_data(data: dict) -> dict:
    """
    Removes unwanted keys from our api call and adds info.
    NOTE: Whilst this is transformative, we need to capture a timestamp of when it was
    extracted at the time of extraction, and we don't want to write unnecessary keys to 
    our file each time. I've kept this minimal.
    """
    for dict_key in ("subscription", "timezone"):
        data.pop(dict_key, None)

    if "rate_limit" in data:
        data["rate_limit"]["timestamp"] = datetime.now(
            timezone.utc).timestamp()
    else:
        raise KeyError("rate_limit not in data.")

    return data


def run_scraper(match_identifier: str | int,
                token: str, conn: HTTPSConnection) -> None:
    """Runs the scraper every 60 seconds until cancelled."""

    scrape_count = 1
    url = build_scrape_url(match_identifier, token)
    makedirs(str(match_identifier))

    while True:
        print(f"Scraping... {scrape_count}")
        filename = f"{match_identifier}/scrape_{scrape_count}.json"

        data = scrape_live_match(url, conn)
        scrape_count += 1

        if "error" not in data:
            data = prepare_data(data)
        else:
            data["timestamp"] = datetime.now(
                timezone.utc).timestamp()

        write_to_file(filename, data)
        sleep(60)


if __name__ == "__main__":

    load_dotenv()
    api_token = ENV["TOKEN"]
    api_conn = HTTPSConnection("api.sportmonks.com")

    # Replace with a fixture id, or a team name from the game e.g. 19375375 or "Scotland"
    identify_match = 19411877
    run_scraper(identify_match, api_token, api_conn)

    api_conn.close()
