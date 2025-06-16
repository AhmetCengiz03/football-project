# pylint: skip-file
"""Tests for load.py script."""

import pandas as pd

from load import get_players_df


def test_get_players_df_concatenates_player_cols():

    df = pd.DataFrame([
        {"player_id": 1, "player_name": "Origi", "related_player_id": 2,
            "related_player_name": "Alexander Arnold", "event_id": 5}
    ])

    player_df = get_players_df(df)

    assert player_df.shape == (2, 2)
    assert "related_player_id" not in player_df


def test_get_players_df_ignores_null_related_players():

    df = pd.DataFrame([
        {"player_id": 2, "player_name": "Milner", "related_player_id": None,
            "related_player_name": None, "event_id": 6}
    ])

    player_df = get_players_df(df)

    assert player_df.shape == (1, 2)
    assert "related_player_id" not in player_df
