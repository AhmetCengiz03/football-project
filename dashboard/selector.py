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
    comp_data["matchup"] = comp_data.apply(
        lambda x: f"{x["home_team"]} - {x["away_team"]}", axis=1)
    matches = sorted(comp_data["matchup"].unique())
    selected_match = st.selectbox("Matches", matches, key="matchup")

    found_teams = comp_data[comp_data["matchup"] == selected_match]

    return found_teams["home_team"].iloc[0], found_teams["away_team"].iloc[0]


def find_and_select_match(comp_data: pd.DataFrame, home_team: list[str],
                          away_team: list[str]) -> None:
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
        st.session_state["selected_match_id"] = int(selected_match["match_id"])
        st.session_state["home_team"] = home_team
        st.session_state["away_team"] = away_team
        st.success("Match found")
    else:
        dates = matches["match_date"].astype(str).tolist()
        match_ids = matches["match_id"].tolist()

        selected_date = st.selectbox("Select date:", dates, key="match_date")
        if selected_date:
            selected_index = dates.index(selected_date)
            st.session_state["selected_match_id"] = int(
                match_ids[selected_index])
            st.session_state["home_team"] = home_team
            st.session_state["away_team"] = away_team
            st.success("Match found")


def create_match_selector() -> None:
    """Create the match selector dropdown."""
    with st.sidebar:
        st.header("Match Selection")

        comp_data = competition_selection_filtering(
            season_selection_filtering(get_all_matches())
        )

        home_team, away_team = team_selection(comp_data)
        print(home_team, away_team)
        if home_team and away_team:
            find_and_select_match(comp_data, home_team, away_team)

        st.image("dashboard/playbyplay.png")
        st.logo("dashboard/playbyplay.png", size="Large")
