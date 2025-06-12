"""Transform data for upload to our database."""

from os import environ as ENV
from http.client import HTTPSConnection
from json import load
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv

from extract import run_extract


def get_dataframe_from_response(data: dict) -> pd.DataFrame:
    """Returns a pandas DataFrame if data is valid."""

    if 'data' not in data:
        raise ValueError("API Response missing 'data' key.")

    if isinstance(data["data"], dict):
        return pd.DataFrame([data["data"]])

    if isinstance(data["data"], list):
        return pd.DataFrame(data["data"])

    raise TypeError(f"'data' key is of unexpected type: {type(data["data"])}.")


def get_dataframe_from_json(file_path: str) -> pd.DataFrame:
    """Returns a pandas DataFrame for a valid json file path."""

    with open(file_path, "r", encoding="utf-8") as f:
        data = load(f)
    return get_dataframe_from_response(data)


def drop_bulk_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drops unnecessary columns from the extracted data."""

    columns_to_remove = [
        "league_id",
        "season_id",
        "sport_id",
        "stage_id",
        "group_id",
        "aggregate_id",
        "round_id",
        "state_id",
        "venue_id",
        "name",
        "starting_at",
        "leg",
        "details",
        "length",
        "placeholder",
        "has_odds",
        "has_premium_odds",
        "starting_at_timestamp",
    ]

    return df.drop(columns=columns_to_remove, errors="ignore")


def get_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Gets the statistics rows and returns them as a DataFrame."""

    match_id = df.at[0, "id"]
    df_stats = pd.json_normalize(df["statistics"].iloc[0])
    df_stats["match_id"] = match_id

    return df_stats


def get_active_period(periods: list[dict]) -> dict:
    """Returns the current period that is in play."""

    for period in periods:
        if period.get("ticking", False):
            return period

    for period in reversed(periods):
        if 'started' in period:
            return period

    return periods[-1]


def get_period_information(df: pd.DataFrame) -> tuple[bool, int, int]:
    """Returns the minute and half"""

    periods = df.at[0, "periods"]
    active_period = get_active_period(periods)

    ticking = active_period.get("ticking", False)
    type_id = active_period.get("type_id", -1)
    minute = active_period.get("minutes", -1)

    return (ticking, type_id, minute)


def append_period_to_statistics(df: pd.DataFrame, df_stats: pd.DataFrame) -> pd.DataFrame:
    """Returns a statistics dataframe with period information."""

    ticking, type_id, minute = get_period_information(df)
    df_stats["half_live"] = ticking
    df_stats["half"] = type_id
    df_stats["match_minute"] = minute

    return df_stats.drop(columns=['id', 'fixture_id'], errors="ignore")


def get_match_event_df(df: pd.DataFrame) -> pd.DataFrame:
    """Returns the DataFrame for the match_event table."""

    comments = df.at[0, "comments"]
    # This needs reworking with live game event data.

    df_comments = pd.DataFrame(comments)
    return df_comments.drop(columns=['id', 'fixture_id'], errors="ignore")


def get_type_mapping(file_path: str) -> pd.DataFrame:
    """Returns a mapping of type_id to its statistic."""

    df_mapping = pd.read_excel(file_path)

    df_mapping = df_mapping.drop(
        columns=["parent_id", "code", "name", "model_type", "group", "stat_group"], errors="ignore")
    df_mapping.columns = ["type_id", "statistic_name"]

    return df_mapping


def create_match_minute_df(df_stats: pd.DataFrame, df_map: pd.DataFrame) -> pd.DataFrame:
    """Returns the match_minute DataFrame resembling our ERD."""

    df_stats = df_stats.merge(df_map, on="type_id", how="left")
    df_stats["statistic_name"] = df_stats["statistic_name"] + \
        df_stats["location"].map({"home": "_home", "away": "_away"})

    df_minute = df_stats.pivot_table(
        index=["match_id", "match_minute", "half"],
        columns="statistic_name",
        values="data.value"
    ).reset_index()

    df_minute.columns = df_minute.columns.str.lower()
    return df_minute


def drop_unwanted_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Drops stats not necessary to our design."""

    columns_to_remove = [
        "accurate_crosses_away",
        "accurate_crosses_home",
        "ball_possession_away",
        "big_chances_created_away",
        "big_chances_created_home",
        "big_chances_missed_away",
        "big_chances_missed_home",
        "dribbled_attempts_away",
        "dribbled_attempts_home",
        "duels_won_away",
        "duels_won_home",
        "free_kicks_away",
        "free_kicks_home",
        "goal_attempts_away",
        "goal_attempts_home",
        "goal_kicks_away",
        "goal_kicks_home",
        "interceptions_away",
        "interceptions_home",
        "long_passes_away",
        "long_passes_home",
        "shots_blocked_away",
        "shots_blocked_home",
        "shots_off_target_away",
        "shots_off_target_home",
        "successful_dribbles_percentage_away",
        "successful_dribbles_percentage_home",
        "successful_dribbles_away",
        "successful_dribbles_home",
        "successful_passes_percentage_home",
        "successful_passes_percentage_away",
        "throwins_away",
        "throwins_home",
        "total_crosses_away",
        "total_crosses_home"
    ]

    return df.drop(columns=columns_to_remove, errors="ignore")


def transform_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Runs the transformation process."""

    df = drop_bulk_columns(df)
    df_match_event = get_match_event_df(df)

    df_stats = append_period_to_statistics(df, get_statistics(df))

    df_minute = create_match_minute_df(
        df_stats, get_type_mapping("types_map_api.xlsx"))

    df_minute = drop_unwanted_stats(df_minute)
    df_minute = df_minute.rename(columns={
        "ball_possession_home": "possession_home",
        "shots_insidebox_home": "shots_inside_home",
        "shots_insidebox_away": "shots_inside_away",
        "shots_outsidebox_home": "shots_outside_home",
        "shots_outsidebox_away": "shots_outside_away",
        "shots_total_home": "shots_home",
        "shots_total_away": "shots_away"
    })

    game_status = get_flags(df, df_stats)
    return df_minute, df_match_event, game_status


def get_flags(df: pd.DataFrame, df_stats: pd.DataFrame) -> dict:
    """Returns a dict of the game state flags."""

    half_live = df_stats["half_live"].iloc[0]
    result_info = df["result_info"].iloc[0]

    return {
        "half_live": bool(half_live),
        "game_over": result_info is not None
    }


if __name__ == "__main__":

    load_dotenv()

    api_token = ENV["TOKEN"]
    api_conn = HTTPSConnection("api.sportmonks.com")
    identify_match = 19411877
    api_data = run_extract(identify_match, api_token, api_conn)
    base_df = get_dataframe_from_response(api_data)

    # base_df = get_dataframe_from_json("match_scrapes/scrape_100.json")
    # base_df['request_timestamp'] = datetime.now(
    #     timezone.utc).timestamp()  # temporary, to act as live data will

    print(transform_data(base_df))

    api_conn.close()
