# pylint: skip-file
"""Tests for the transform.py script."""

from pytest import raises
from unittest.mock import MagicMock
import pandas as pd

from transform import (
    get_dataframe_from_response, get_statistics, get_active_period,
    get_period_information, get_match_event_df, create_match_minute_df,
    get_flags
)


def test_get_dataframe_from_response_data_key_dict():

    response = {"data": {"match_id": 10, "sport_id": 1}}
    df = get_dataframe_from_response(response)
    assert isinstance(df, pd.DataFrame)


def test_get_dataframe_from_response_data_key_list():

    response = {
        "data": [
            {"match_id": 10, "sport_id": 1},
            {"rate_limit": 10, "reset_time": 100}
        ]}

    df = get_dataframe_from_response(response)
    assert isinstance(df, pd.DataFrame)


def test_get_dataframe_from_response_empty_data():

    response = {}
    with raises(ValueError):
        get_dataframe_from_response(response)


def test_get_dataframe_from_response_missing_data_key():

    response = {"oops": "fail_test"}
    with raises(ValueError):
        get_dataframe_from_response(response)


def test_get_dataframe_from_response_missing_data_key():

    response = "bad data response"
    with raises(TypeError):
        get_dataframe_from_response(response)


def test_get_statistics_expected_dataframe():

    df = pd.DataFrame([{
        "id": 10,
        "statistics": [
            {"statistic_name": "Possession", "value": 55},
            {"statistic_name": "Tackles", "value": 15}
        ]
    }])

    stats_df = get_statistics(df)

    assert "match_id" in stats_df.columns
    assert "statistic_name" in stats_df.columns
    assert "value" in stats_df.columns


def test_get_statistics_handles_no_stats_yet():

    df = pd.DataFrame([{
        "id": 10,
        "statistics": []
    }])

    stats_df = get_statistics(df)

    assert "match_id" in stats_df.columns


def test_get_active_period_gets_correct_period():

    periods = [
        {"period_id": 1, "started": 150, "ticking": True},
        {"period_id": 2, "started": -1, "ticking": False}
    ]

    period = get_active_period(periods)

    assert period["ticking"]
    assert period["period_id"] == 1


def test_get_active_period_gets_correct_period_one_period_available():

    periods = [
        {"period_id": 1, "started": 150, "ticking": True}
    ]

    period = get_active_period(periods)

    assert period["ticking"]
    assert period["period_id"] == 1


def test_get_active_period_gets_correct_period_second_half():

    periods = [
        {"period_id": 1, "started": 150, "ticking": False},
        {"period_id": 2, "started": 300, "ticking": True}
    ]

    period = get_active_period(periods)

    assert period["ticking"]
    assert period["period_id"] == 2


def test_get_active_period_gets_correct_period_third_half():

    periods = [
        {"period_id": 1, "started": 150, "ticking": False},
        {"period_id": 2, "started": 300, "ticking": False},
        {"period_id": 3, "started": 400, "ticking": True},
    ]

    period = get_active_period(periods)

    assert period["ticking"]
    assert period["period_id"] == 3


def test_get_active_period_gets_correct_period_game_over_last_ended():

    periods = [
        {"period_id": 1, "started": 150, "ticking": False},
        {"period_id": 2, "started": 300, "ticking": False}
    ]

    period = get_active_period(periods)

    assert not period["ticking"]
    assert period["period_id"] == 2


def test_get_active_period_gets_fallback_period_no_ticking_or_starting_value():

    periods = [
        {"period_id": 1},
        {"period_id": 2}
    ]

    period = get_active_period(periods)

    assert period["period_id"] == 2


def test_get_period_information_builds_as_expected():

    df = pd.DataFrame([{"periods":
                        [{"type_id": 1, "minutes": 48, "ticking": False},
                         {"type_id": 2, "minutes": 46, "ticking": True}]
                        }])

    ticking, type_id, minute = get_period_information(df)

    assert ticking
    assert type_id == 2
    assert minute == 46


def test_get_match_event_df_builds_correct_structure():

    df = pd.DataFrame([{"events": [
        {"event_id": 1, "type_id": 15},
        {"event_id": 2, "type_id": 5}
    ]}])

    event_df = get_match_event_df(df)

    assert "event_id" in event_df.columns
    assert "type_id" in event_df.columns


def test_create_match_minute_df_correct_structure_home_entry():

    df_stats = pd.DataFrame([
        {"match_id": 1, "match_minute": 20, "half": 1,
            "type_id": 15, "location": "home", "data.value": 25}
    ])

    df_map = pd.DataFrame([
        {"type_id": 15, "statistic_name": "tackles"},
        {"type_id": 16, "statistic_name": "passes"}
    ])

    df_match_minute = create_match_minute_df(df_stats, df_map)

    assert "tackles_home" in df_match_minute.columns


def test_create_match_minute_df_correct_structure_away_entry():

    df_stats = pd.DataFrame([
        {"match_id": 1, "match_minute": 25, "half": 1,
            "type_id": 16, "location": "away", "data.value": 10}
    ])

    df_map = pd.DataFrame([
        {"type_id": 15, "statistic_name": "tackles"},
        {"type_id": 16, "statistic_name": "passes"}
    ])

    df_match_minute = create_match_minute_df(df_stats, df_map)

    assert "passes_away" in df_match_minute.columns


def test_get_flags_first_half():

    df = pd.DataFrame([{"result_info": None}])
    df_stats = pd.DataFrame([{"half_live": True}])

    flags = get_flags(df, df_stats)

    assert flags["half_live"]
    assert not flags["game_over"]


def test_get_flags_half_time():

    df = pd.DataFrame([{"result_info": None}])
    df_stats = pd.DataFrame([{"half_live": False}])

    flags = get_flags(df, df_stats)

    assert not flags["half_live"]
    assert not flags["game_over"]


def test_get_flags_full_time():

    df = pd.DataFrame([{"result_info": "Boca won 1-1 after FT."}])
    df_stats = pd.DataFrame([{"half_live": False}])

    flags = get_flags(df, df_stats)

    assert not flags["half_live"]
    assert flags["game_over"]
