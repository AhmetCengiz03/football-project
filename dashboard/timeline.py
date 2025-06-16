"""All processing of data for the dashboard."""
import pandas as pd
import streamlit as st

from data import (
    get_event_data_for_selected_match,
    get_match_info_for_selected_match, get_all_stats_for_selected_match
)


def calculate_score_from_events(events_df, match_info):
    """Calculate running score for this match."""

    goal_events = events_df[events_df["type_name"] == "goal"]

    if goal_events.empty:
        print("No goals in this match")
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


def check_all_expected_events_exist(event_pivot):
    """Ensure that all expected events are in table."""
    expected_events = ["var", "goal", "owngoal", "penalty",
                       "missed_penalty", "substitution", "yellowcard", "redcard"]
    for event_type in expected_events:
        if event_type not in event_pivot.columns:
            event_pivot[event_type] = 0


def create_full_match_timeline(events_df, match_info, match_stats):
    """Create a full timeline with all stats at every minute."""

    timeline = match_stats.copy()

    event_counts = events_df.value_counts(
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

    score_data = calculate_score_from_events(events_df, match_info)

    if not score_data.empty:
        timeline = timeline.merge(score_data, on="match_minute", how="left")

        timeline["home_score"] = timeline["home_score"].ffill().fillna(0)
        timeline["away_score"] = timeline["away_score"].ffill().fillna(0)

    else:
        timeline["home_score"] = 0
        timeline["away_score"] = 0

    return timeline


def create_slider(timeline_df):
    """Create streamlit slider on dashboard."""
    max_minute = int(timeline_df["match_minute"].max())
    st.subheader("Match Timeline")
    selected_minute = st.slider(
        "Select Match Minute",
        min_value=1,
        max_value=max_minute,
        value=1,
        step=1
    )
    return selected_minute


def create_timeline_df():
    """Create game timeline dataframe."""
    print("Creating slider")
    events_df = get_event_data_for_selected_match(
        st.session_state["selected_match_id"])
    match_info = get_match_info_for_selected_match(
        st.session_state["selected_match_id"])
    match_stats = get_all_stats_for_selected_match(
        st.session_state["selected_match_id"])

    timeline_df = create_full_match_timeline(
        events_df, match_info, match_stats)

    return timeline_df
