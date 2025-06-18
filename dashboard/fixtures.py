"""Page on individual team statistics."""
import streamlit as st
import pandas as pd

from data import get_all_matches


def get_all_games():
    """Get all games in database."""
    all_matches = get_all_matches()
    find_games_with_no_data(all_matches)


def find_games_with_no_data(all_matches: pd.Dataframe):
    """Find games with no data as they have not started yet."""


def get_all_match_ids_with_data():
    """Get all unique match ids in match_minute."""
