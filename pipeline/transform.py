"""Transform data for upload to our database."""

from os import environ as ENV
from http.client import HTTPSConnection
import logging
from json import load
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv

from extract import run_extract

logger = logging.getLogger(__name__)
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

STATS_COLUMNS = [
    "accurate_crosses_away",
    "accurate_crosses_home",
    "ball_possession_away",
    "ball_safe_away",
    "ball_safe_home",
    "goal_attempts_away",
    "goal_attempts_home",
    "goal_kicks_away",
    "goal_kicks_home",
    "injuries_away",
    "injuries_home",
    "long_passes_away",
    "long_passes_home",
    "shots_off_target_away",
    "shots_off_target_home",
    "successful_dribbles_percentage_away",
    "successful_dribbles_percentage_home",
    "successful_passes_percentage_home",
    "successful_passes_percentage_away",
    "throwins_away",
    "throwins_home",
    "assists_away",
    "assists_home",
    "goals_away",
    "goals_home",
    "substitutions_away",
    "substitutions_home",
    "yellowcards_away",
    "yellowcards_home",
    "redcards_away",
    "redcards_home"
]

BULK_COLUMNS = [
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

EVENT_COLUMNS = [
    "period_id",
    "section",
    "result",
    "info",
    "addition",
    "extra_minute",
    "injured",
    "on_bench",
    "coach_id",
    "sub_type_id",
    "detailed_period_id",
    "sort_order"
]


def get_dataframe_from_response(data: dict) -> pd.DataFrame:
    """
    Returns a pandas DataFrame if data is valid.
    A json scrape expects data["data"] to be a list,
    whereas a live scrape expects a dict. This handles that.
    """

    if not data:
        raise ValueError("Data is empty.")

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

    logger.info("Read json data successfully.")
    return get_dataframe_from_response(data)


def drop_bulk_columns(df: pd.DataFrame, columns_to_remove: list[str]) -> pd.DataFrame:
    """Drops unnecessary columns from the extracted data."""

    logger.info("Dropping unnecessary columns from request.")
    return df.drop(columns=columns_to_remove, errors="ignore")


def get_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Gets the statistics rows and returns them as a DataFrame."""

    match_id = df.at[0, "id"]
    df_stats = pd.json_normalize(df["statistics"].iloc[0])
    df_stats["match_id"] = match_id

    logger.info("Created statistics dataframe.")
    return df_stats


def get_active_period(periods: list[dict]) -> dict:
    """Returns the current period that is in play."""

    for period in periods:
        if period.get("ticking", False):

            logger.info("Found active period.")
            return period

    for period in reversed(periods):
        if 'started' in period:

            logger.info("Found last active period.")
            return period

    return periods[-1]


def get_period_information(df: pd.DataFrame) -> tuple[bool, int, int]:
    """Returns the the state of the half, the current half and the minute."""

    periods = df.at[0, "periods"]
    active_period = get_active_period(periods)

    ticking = active_period.get("ticking", False)
    type_id = active_period.get("type_id", -1)
    minute = active_period.get("minutes", -1)

    logger.info("Is half live: %s. Current half: %s. Current minute: %s.",
                ticking, type_id, minute)
    return (ticking, type_id, minute)


def append_period_to_statistics(df: pd.DataFrame, df_stats: pd.DataFrame) -> pd.DataFrame:
    """Returns a statistics dataframe with period information."""

    ticking, type_id, minute = get_period_information(df)
    df_stats["half_live"] = ticking
    df_stats["half"] = type_id
    df_stats["match_minute"] = minute

    logger.info(
        "Successfully appended statistics with current game state information.")
    return df_stats.drop(columns=['id', 'fixture_id'], errors="ignore")


def get_match_event_df(df: pd.DataFrame) -> pd.DataFrame:
    """Returns the DataFrame for the match_event table."""

    events = df.at[0, "events"]
    logger.info("Found current match events.")
    return pd.DataFrame(events)


def drop_event_columns(df: pd.DataFrame, columns_to_remove: list[str]) -> pd.DataFrame:
    """Drops events not necessary to our design."""

    logger.info("Dropping unnecessary event information.")
    return df.drop(columns=columns_to_remove, errors="ignore")


def map_event_to_type(df_map: pd.DataFrame, df_event: pd.DataFrame) -> pd.DataFrame:
    """Return the mapping of event to event_type."""

    logger.info("Mapping events to their types.")
    return df_event.merge(df_map, on="type_id", how="inner")


def prepare_events(df: pd.DataFrame, columns_to_remove: list[str],
                   df_map: pd.DataFrame) -> pd.DataFrame:
    """Returns the prepared events DataFrame."""

    df = drop_event_columns(df, columns_to_remove)
    df_events = map_event_to_type(df_map, df)

    df_events = df_events.rename(columns={
        "id": "match_event_id",
        "fixture_id": "match_id",
        "participant_id": "team_id",
        "statistic_name": "type_name",
        "type_id": "event_type_id"
    })

    logger.info("match_event dataframe ready for upload.")
    return df_events


def get_type_mapping(file_path: str) -> pd.DataFrame:
    """Returns a mapping of type_id to its statistic."""

    df_mapping = pd.read_excel(file_path)

    df_mapping = df_mapping.drop(
        columns=["parent_id", "code", "name", "model_type", "group", "stat_group"], errors="ignore")
    df_mapping.columns = ["type_id", "statistic_name"]
    df_mapping["statistic_name"] = df_mapping["statistic_name"].str.lower()

    logger.info("Successfully created the type map dataframe.")
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

    logger.info("Successfully created the match_minute_stats dataframe.")
    return df_minute


def drop_unwanted_stats(df: pd.DataFrame, columns_to_remove: list[str]) -> pd.DataFrame:
    """Drops stats not necessary to our design."""

    logger.info("Dropping unwanted statistics.")
    return df.drop(columns=columns_to_remove, errors="ignore")


def transform_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Runs the transformation process."""

    df = drop_bulk_columns(df, BULK_COLUMNS)
    df_map = get_type_mapping("types_map_api.xlsx")
    df_match_event = get_match_event_df(df)

    if df_match_event.empty:
        df_events = df_match_event
    else:
        df_events = prepare_events(df_match_event, EVENT_COLUMNS, df_map)

    df_stats = append_period_to_statistics(df, get_statistics(df))

    df_minute = create_match_minute_df(df_stats, df_map)
    df_minute = drop_unwanted_stats(df_minute, STATS_COLUMNS)
    df_minute = df_minute.rename(columns={
        "ball_possession_home": "possession_home",
        "dangerous_attacks_away": "danger_attacks_away",
        "dangerous_attacks_home": "danger_attacks_home",
        "shots_insidebox_home": "shots_inside_home",
        "shots_insidebox_away": "shots_inside_away",
        "shots_outsidebox_home": "shots_outside_home",
        "shots_outsidebox_away": "shots_outside_away",
        "shots_total_home": "shots_home",
        "shots_total_away": "shots_away"
    })

    game_status = get_flags(df, df_stats)
    logger.info("Is game over: %s", game_status["game_over"])
    logger.info("Transform handing off to load ...")
    return df_minute, df_events, game_status


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

    api_conn.close()
