"""Upcoming fixtures page."""
import streamlit as st
import pandas as pd

from data import get_all_matches, get_unique_match_ids_in_match_minute_stats


def get_upcoming_fixtures() -> pd.DataFrame:
    """Find games with no data as they have not started yet."""
    match_ids_started = get_unique_match_ids_in_match_minute_stats()
    all_matches = get_all_matches()

    upcoming_fixtures = all_matches[~all_matches["match_id"].isin(
        match_ids_started["match_id"])]

    return upcoming_fixtures.sort_values("match_date")


def display_fixtures() -> None:
    """Display the upcoming games on the page."""
    st.title("Upcoming Fixtures")
    st.markdown("Games that haven't started yet and need data collection")

    with st.spinner():
        try:
            upcoming_fixtures = get_upcoming_fixtures()
        except Exception as e:
            st.error(f"Error loading data {str(e)}")
            return

    if upcoming_fixtures.empty:
        st.success("No upcoming fixtures")

    else:
        st.subheader(f"Today's Games")
        grouped = upcoming_fixtures.groupby("competition_name")
        for competition, comp_games in grouped:
            with st.expander(f"{competition} ({len(comp_games)} games)", expanded=True):
                comp_games_sorted = comp_games.sort_values("match_date")
                for _, game in comp_games_sorted.iterrows():
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(
                            f"{game["home_team"]} vs {game["away_team"]}")
                    with col2:
                        st.markdown(f"{game["match_date"]} UTC")


if __name__ == "__main__":
    display_fixtures()
