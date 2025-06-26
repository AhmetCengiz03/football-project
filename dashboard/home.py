"""Home page."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from data import get_match_info_for_selected_match, get_event_data_for_selected_match
from timeline import create_timeline_df, create_slider
from momentum import process_momentum_chart_creation


def create_top_bar(timeline_df: pd.DataFrame) -> st.slider:
    """Create the top bar of the page."""
    selected_minute = create_slider(timeline_df)

    match_info = get_match_info_for_selected_match(
        st.session_state["selected_match_id"])

    _, col2, _ = st.columns([1.5, 8, 1.5])

    minute_data = timeline_df[timeline_df["match_minute"]
                              == selected_minute]

    home_score = int(minute_data["home_score"].iloc[0])
    away_score = int(minute_data["away_score"].iloc[0])
    home_logo = match_info["home_logo_url"].iloc[0]
    away_logo = match_info["away_logo_url"].iloc[0]

    with col2:
        col2a, col2b, col2c, col2d, col2e = st.columns([3, 1, 2, 1, 3])
        with col2a:
            st.markdown(f"<h1 style='text-align: center'>{st.session_state["home_team"]
                                                          }</h1>",
                        unsafe_allow_html=True)
        with col2b:
            st.image(home_logo, width=100)

        with col2c:
            st.markdown(f"<h1 style='text-align: center'>{home_score
                                                          } - {away_score}</h1>",
                        unsafe_allow_html=True)

        with col2d:
            st.image(away_logo, width=100)
        with col2e:
            st.markdown(f"<h1 style='text-align: center'> {st.session_state["away_team"]} </h1>",
                        unsafe_allow_html=True)

    return selected_minute


def get_rolling_sum_for_radar(timeline_df: pd.DataFrame, selected_minute: int, radar_stats: list[tuple]) -> pd.Series:
    """Gets the rolling sum within a specified window."""
    stat_columns = [col for home_col,
                    away_col in radar_stats for col in [home_col, away_col]]
    df = timeline_df.copy()
    window = 15
    for col in stat_columns:
        df[f"{col}_change"] = df[col].diff().fillna(0)

    for col in stat_columns:
        df[f"{col}_rolling"] = df[f"{col}_change"].rolling(window).sum()

    selected_data = df[df["match_minute"] == selected_minute]

    minute_data = selected_data.iloc[0]

    return minute_data


def create_match_progression_radar(timeline_df: pd.DataFrame, selected_minute: int,
                                   radar_stats: list[tuple], categories: list[str],
                                   radar_title: str) -> go.Figure:
    """Create radar plot for match statistics."""

    minute_data = get_rolling_sum_for_radar(
        timeline_df, selected_minute, radar_stats)
    home_values = []
    away_values = []

    for home_col, away_col in radar_stats:
        home_val = minute_data[f"{home_col}_rolling"]
        away_val = minute_data[f"{away_col}_rolling"]
        max_val = max(home_val, away_val, 1)
        home_scaled = (home_val/max_val) * 100
        away_scaled = (away_val/max_val) * 100
        home_values.append(home_scaled)
        away_values.append(away_scaled)

    # Necessary to replot first point, so radar chart line is complete
    home_values.append(home_values[0])
    away_values.append(away_values[0])
    categories.append(categories[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=home_values,
        theta=categories,
        line=dict(color="rgba(0,255,0,1)", width=2),
        name=st.session_state["home_team"]
    ))

    fig.add_trace(go.Scatterpolar(
        r=away_values,
        theta=categories,
        line=dict(color="rgba(255,0,0,1)", width=2),
        name=st.session_state["away_team"]
    ))
    fig.update_layout(
        title=radar_title,
        polar=dict(
            radialaxis=dict(
                visible=False
            ), bgcolor="rgba(0,0,0,0)"

        ),
        showlegend=True
    )

    return fig


def create_event_buttons(match_events: pd.DataFrame) -> None:
    """Create buttons for all events."""
    home_team_id = st.session_state["match_info"]["home_team_id"].iloc[0]
    away_team_id = st.session_state["match_info"]["away_team_id"].iloc[0]
    home_team_name = st.session_state["match_info"]["home_team_name"].iloc[0]
    away_team_name = st.session_state["match_info"]["away_team_name"].iloc[0]
    event_data = match_events.sort_values(
        "match_minute")[["type_name", "match_minute", "player_name", "team_id"]]
    event_data_no_subs = event_data[event_data["type_name"]
                                    != "substitution"].values
    cols = st.columns(3)
    for i, (event_type, minute, player_name, team_id) in enumerate(event_data_no_subs):
        with cols[i % 3]:
            if team_id == home_team_id:
                team_name = home_team_name
            elif team_id == away_team_id:
                team_name = away_team_name
            if event_type == "goal":
                select_icon = "⚽"
            elif event_type == "yellowcard":
                select_icon = "🟨"
            elif event_type == "redcard":
                select_icon = "🟥"
            elif event_type == "substitution":
                select_icon = "🔄"

            button_label = f"{minute} | {event_type} | {player_name} | {team_name}"
            if st.button(button_label, key=f"event{i}", icon=select_icon):
                st.session_state["selected_minute"] = int(minute)
                st.rerun()


def create_comparison_line_chart(timeline_df: pd.DataFrame,
                                 selected_minute: int, stat_name: str) -> go.Figure:
    """Compare one stat between home and away."""
    home_col = f"{stat_name.lower()}_home"
    away_col = f"{stat_name.lower()}_away"

    if home_col not in timeline_df.columns or away_col not in timeline_df.columns:
        st.error(f"Stat {stat_name} not available")
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=timeline_df["match_minute"],
        y=timeline_df[home_col],
        mode="lines+markers",
        name=st.session_state["home_team"],
        line=dict(color="rgba(0,255,0,1)", width=4),
    ))

    fig.add_trace(go.Scatter(
        x=timeline_df["match_minute"],
        y=timeline_df[away_col],
        mode="lines+markers",
        name=st.session_state["away_team"],
        line=dict(color="rgba(255,0,0,1)", width=4),
    ))
    fig.add_vline(x=selected_minute, line_dash="dash", line_color="white")

    return fig


def create_minute_by_minute_comparison(timeline_df: pd.DataFrame,
                                       selected_minute: int) -> tuple[pd.DataFrame, list, pd.DataFrame]:
    """Create a minute by minute comparison."""
    current_data = timeline_df[timeline_df["match_minute"] == selected_minute]
    previous_minute = timeline_df[timeline_df["match_minute"] == (
        selected_minute - 1)]
    minute_data = current_data.iloc[0]
    previous_minute_data = previous_minute.iloc[0]
    key_stats = [
        ("Possession", "possession_home", "possession_away", "%"),
        ("Shots", "shots_home", "shots_away", ""),
        ("Attacks", "attacks_home", "attacks_away", ""),
        ("Corners", "corners_home", "corners_away", ""),
        ("Fouls", "fouls_home", "fouls_away", "")
    ]

    return minute_data, key_stats, previous_minute_data


def create_home_page() -> None:
    """Main function to create the home page."""
    timeline_df = create_timeline_df()

    match_events = get_event_data_for_selected_match(
        st.session_state["selected_match_id"])

    selected_minute = create_top_bar(timeline_df)

    col1, col2, col3 = st.columns([1.5, 4, 1.5])

    # Game momentum/pressure chart
    with st.expander("Momentum Chart", expanded=True):
        momentum_chart = process_momentum_chart_creation(
            timeline_df, selected_minute)

        st.plotly_chart(momentum_chart)

    minute_data, key_stats, previous_minute_data = create_minute_by_minute_comparison(
        timeline_df, selected_minute)
    radar_stats = [
        ("shots_home", "shots_away"),
        ("attacks_home", "attacks_away"),
        ("possession_home", "possession_away"),
        ("corners_home", "corners_away"),
        ("passes_home", "passes_away")
    ]
    categories = ["Shots", "Attacks",
                  "Possession", "Corners", "Passes"]
    fig_attack = create_match_progression_radar(
        timeline_df, selected_minute, radar_stats, categories, "Attacking stats")

    radar_stats = [
        ("saves_home", "saves_away"),
        ("fouls_home", "fouls_away"),
        ("shots_blocked_home", "shots_blocked_away")
    ]
    categories = ["Saves", "Fouls",
                  "Shots Blocked"]

    fig_defence = create_match_progression_radar(
        timeline_df, selected_minute, radar_stats, categories, "Defensive Stats")

    with st.expander("Events"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"### {st.session_state["home_team"]}")
            for stat_name, home_col, _, unit in key_stats:
                home_val = minute_data[home_col]
                home_val_previous = previous_minute_data[home_col]
                delta = int(home_val - home_val_previous)
                st.metric(stat_name, f"{home_val:.0f}{unit}", delta=delta)

        with col2:
            st.markdown("<h3 style='text-align: center'>Match Events</h1>",
                        unsafe_allow_html=True)
            create_event_buttons(match_events)

        with col3:
            _, col3ab = st.columns([1, 5])
            with col3ab:
                st.markdown(f"<h3 style='text-align: right'>{st.session_state["away_team"]}</h1>",
                            unsafe_allow_html=True)
            _, col3b = st.columns([3, 1])
            with col3b:
                for stat_name, home_col, away_col, unit in key_stats:
                    away_val = minute_data[away_col]
                    away_val_previous = previous_minute_data[away_col]
                    delta = int(away_val - away_val_previous)
                    st.metric(stat_name, f"{away_val:.0f}{unit}", delta=delta)

    with st.expander("Radar Charts", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_attack)
        with col2:
            st.plotly_chart(fig_defence)

    with st.expander("Line Charts", expanded=True):
        stat_name = st.selectbox("Choose a Stat to Compare",
                                 ["Shots", "Attacks", "Possession", "Corners", "Fouls", "Saves"])

        fig = create_comparison_line_chart(
            timeline_df, selected_minute, stat_name)

        st.plotly_chart(fig)


if __name__ == "__main__":
    create_home_page()
