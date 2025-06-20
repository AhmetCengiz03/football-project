# pylint: skip-file
"""Tests for load.py script."""
from unittest.mock import MagicMock, patch

import pandas as pd

from load import get_players_df, get_if_goal_scored_this_run, get_connection


def test_get_players_df_concatenates_player_cols():

    df = pd.DataFrame([
        {"player_id": 1, "player_name": "Origi", "related_player_id": 2,
            "related_player_name": "Alexander Arnold", "event_id": 5}
    ])

    player_df = get_players_df(df)

    assert player_df.shape == (2, 2)
    assert "related_player_id" not in player_df


def test_get_players_df_removes_duplicate_players():
    """Test that duplicate player IDs are removed."""
    df = pd.DataFrame([
        {"player_id": 1, "player_name": "Origi", "related_player_id": 2,
         "related_player_name": "Alexander Arnold", "event_id": 5},
        {"player_id": 1, "player_name": "Origi", "related_player_id": 3,
         "related_player_name": "Salah", "event_id": 6}
    ])

    player_df = get_players_df(df)

    assert player_df.shape == (3, 2)
    assert len(player_df["player_id"].unique()) == 3


def test_get_players_df_ignores_null_related_players():

    df = pd.DataFrame([
        {"player_id": 2, "player_name": "Milner", "related_player_id": None,
            "related_player_name": None, "event_id": 6}
    ])

    player_df = get_players_df(df)

    assert player_df.shape == (1, 2)
    assert "related_player_id" not in player_df


def test_get_players_df_handles_all_null_player_ids():
    df = pd.DataFrame([
        {"player_id": None, "player_name": None, "related_player_id": None,
         "related_player_name": None, "event_id": 1}
    ])

    player_df = get_players_df(df)

    assert player_df.empty


def test_no_goals_in_event_df():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    event_df = pd.DataFrame([
        {"match_event_id": 1, "type_name": "pass", "match_id": 100,
            "team_id": 1, "player_name": "Salah", "minute": 10}
    ])

    result = get_if_goal_scored_this_run(event_df, mock_conn)

    assert result == []


def test_goals_already_in_database():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    event_df = pd.DataFrame([
        {"match_event_id": 5, "type_name": "goal", "match_id": 100,
            "team_id": 1, "player_name": "Scorer", "minute": 45}
    ])
    mock_cursor.fetchall.return_value = [(5,)]

    result = get_if_goal_scored_this_run(event_df, mock_conn)

    assert result == []


def test_new_goals_found():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    event_df = pd.DataFrame([
        {"match_event_id": 10, "type_name": "goal", "match_id": 100,
            "team_id": 1, "player_name": "Salah", "minute": 30},
        {"match_event_id": 11, "type_name": "Goal", "match_id": 100,
            "team_id": 2, "player_name": "Hazard", "minute": 75},
        {"match_event_id": 12, "type_name": "pass", "match_id": 100,
            "team_id": 1, "player_name": "Milner", "minute": 20}
    ])
    mock_cursor.fetchall.return_value = []

    result = get_if_goal_scored_this_run(event_df, mock_conn)

    assert result[0]["match_event_id"] == 10
    assert result[0]["player_name"] == "Salah"
    assert result[1]["match_event_id"] == 11
    assert result[1]["player_name"] == "Hazard"
