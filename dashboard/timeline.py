"""All processing of data for the dashboard."""
import pandas as pd
import streamlit as st

from data import (
    get_event_data_for_selected_match,
    get_match_info_for_selected_match, get_all_stats_for_selected_match
)


def calculate_score_from_events(match_events: pd.DataFrame, match_info: pd.DataFrame) -> pd.DataFrame:
    """Calculate running score for this match."""

    goal_events = match_events[match_events["type_name"] == "goal"]

    if goal_events.empty:
        return pd.DataFrame()

    goal_events["is_home_goal"] = (
        goal_events["team_id"] == int(match_info["home_team_id"])).astype(int)
    goal_events["is_away_goal"] = (
        goal_events["team_id"] == int(match_info["away_team_id"])).astype(int)

    goals_by_minute = goal_events.groupby("match_minute").agg({
        "is_home_goal": "sum",
        "is_away_goal": "sum"
    }).reset_index()

    goals_by_minute["home_score"] = goals_by_minute["is_home_goal"].cumsum()
    goals_by_minute["away_score"] = goals_by_minute["is_away_goal"].cumsum()

    return goals_by_minute


def check_all_expected_events_exist(event_pivot: pd.DataFrame) -> None:
    """Ensure that all expected events are in table."""
    expected_events = ["var", "goal", "owngoal", "penalty",
                       "missed_penalty", "substitution", "yellowcard", "redcard"]
    for event_type in expected_events:
        if event_type not in event_pivot.columns:
            event_pivot[event_type] = 0


def create_full_match_timeline(match_events: pd.DataFrame, match_info: pd.DataFrame, match_stats: pd.DataFrame) -> pd.DataFrame:
    """Create a full timeline with all stats at every minute."""

    timeline = match_stats.copy()

    event_counts = match_events.value_counts(
        ["match_minute", "type_name"]).reset_index(name="count")

    event_pivot = event_counts.pivot_table(
        index="match_minute",
        columns="type_name",
        values="count",
        fill_value=0
    ).reset_index()

    check_all_expected_events_exist(event_pivot)

    timeline = timeline.merge(
        event_pivot, on="match_minute", how="left").fillna(0)

    score_data = calculate_score_from_events(match_events, match_info)

    if not score_data.empty:
        timeline = timeline.merge(score_data, on="match_minute", how="left")

        timeline["home_score"] = timeline["home_score"].ffill().fillna(0)
        timeline["away_score"] = timeline["away_score"].ffill().fillna(0)

    else:
        timeline["home_score"] = 0
        timeline["away_score"] = 0

    return timeline


def create_slider(timeline_df: pd.DataFrame) -> st.slider:
    """Create streamlit slider on dashboard."""
    max_minute = int(timeline_df["match_minute"].max())
    st.subheader("Match Timeline")
    selected_minute = st.slider(
        "Select Match Minute",
        min_value=1,
        max_value=max_minute,
        value=st.session_state.get("selected_minute", 1),
        step=1
    )
    return selected_minute


def create_timeline_df() -> pd.DataFrame:
    """Create game timeline dataframe."""
    print("Creating slider")
    match_events = get_event_data_for_selected_match(
        st.session_state["selected_match_id"])
    match_info = get_match_info_for_selected_match(
        st.session_state["selected_match_id"])
    match_stats = get_all_stats_for_selected_match(
        st.session_state["selected_match_id"])

    timeline_df = create_full_match_timeline(
        match_events, match_info, match_stats)

    timeline_df["possession_away"] = 100 - timeline_df["possession_home"]

    st.session_state["match_events"] = match_events
    st.session_state["match_info"] = match_info
    st.session_state["match_stats"] = match_stats

    return timeline_df.sort_values("match_minute")
