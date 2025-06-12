"""Script to create the selector for choosing a game to be display on the dashboard."""
import streamlit as st
import pandas as pd

from data import get_all_matches


def season_selection_filtering(all_matches: pd.DataFrame) -> pd.DataFrame:
    """Create season selection dropdown with filtering."""
    seasons = sorted(all_matches["season_name"].unique(), reverse=True)
    selected_season = st.selectbox("Season", seasons, key="season")
    season_data = all_matches[all_matches["season_name"] == selected_season]
    return season_data


def competition_selection_filtering(season_data: pd.DataFrame) -> pd.DataFrame:
    """Create competition selection dropdown with filtering."""
    competitions = sorted(season_data["competition_name"].unique())
    selected_competition = st.selectbox(
        "Competition", competitions, key="competition")
    comp_data = season_data[season_data["competition_name"]
                            == selected_competition]
    return comp_data


def team_selection(comp_data: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Create team selection dropdowns."""
    home_teams = sorted(comp_data["home_team"].unique())
    away_teams = sorted(comp_data["away_team"].unique())

    col1, col2 = st.columns(2)

    with col1:
        home_team = st.selectbox("Home Team", home_teams, key="home_team")

    with col2:
        away_team = st.selectbox("Away Team", away_teams, key="away_team")

    return home_team, away_team


def find_and_select_match(comp_data, home_team, away_team):
    """Find the match and handle selection."""
    matches = comp_data[
        (comp_data["home_team"] == home_team) &
        (comp_data["away_team"] == away_team)
    ]

    if matches.empty:
        st.warning(f"No matches found: {home_team} vs {away_team}")
        if "selected_match_id" in st.session_state:
            del st.session_state["selected_match_id"]
        return

    if len(matches) == 1:
        selected_match = matches.iloc[0]
        st.session_state["selected_match_id"] = selected_match["match_id"]
        st.success("Match found")
    else:
        dates = matches["match_date"].astype(str).tolist()
        match_ids = matches["match_id"].tolist()

        selected_date = st.selectbox("Select date:", dates, key="match_date")
        if selected_date:
            selected_index = dates.index(selected_date)
            st.session_state["selected_match_id"] = match_ids[selected_index]
            st.success("Match found")


def create_match_selector():
    """Create the match selector dropdown."""
    with st.sidebar:
        st.header("Match Selection")

        all_matches = get_all_matches()

        season_data = season_selection_filtering(all_matches)

        comp_data = competition_selection_filtering(season_data)

        home_team, away_team = team_selection(comp_data)

        if home_team and away_team:
            find_and_select_match(comp_data, home_team, away_team)
