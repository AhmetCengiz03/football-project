"""Home page."""
import altair as alt
from vega_datasets import data
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import altair as alt
from vega_datasets import data

from data import get_match_info_for_selected_match, get_event_data_for_selected_match, get_team_from_match_id
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


def create_match_progression_radar_attack(timeline_df: pd.DataFrame, selected_minute: int) -> go.Figure:
    """Create radar plot for match statistics."""
    data_up_to_minute = timeline_df[timeline_df["match_minute"]
                                    == selected_minute]

    minute_data = data_up_to_minute.iloc[-1]
    # I may calculate averages here? For now it is just the stats for this minute

    radar_stats = [
        ("shots_home", "shots_away"),
        ("attacks_home", "attacks_away"),
        ("possession_home", "possession_away"),
        ("corners_home", "corners_away"),
        ("passes_home", "passes_away")
    ]
    categories = ["Shots", "Attacks",
                  "Possession", "Corners", "Passes"]
    home_values = []
    away_values = []

    for home_col, away_col in radar_stats:
        home_val = minute_data[home_col]
        away_val = minute_data[away_col]
        max_val = max(home_val, away_val, 1)
        home_scaled = (home_val/max_val) * 100
        away_scaled = (away_val/max_val) * 100
        home_values.append(home_scaled)
        away_values.append(away_scaled)

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
        title="Attacking stats",
        polar=dict(
            radialaxis=dict(
                visible=True
            ), bgcolor="rgba(0,0,0,0)"

        ),
        showlegend=True
    )

    return fig


def create_match_progression_radar_defence(timeline_df: pd.DataFrame, selected_minute: int) -> go.Figure:
    """Create radar plot for match statistics."""
    data_up_to_minute = timeline_df[timeline_df["match_minute"]
                                    == selected_minute]

    minute_data = data_up_to_minute.iloc[-1]
    # I may calculate averages here? For now it is just the stats for this minute

    radar_stats = [
        ("saves_home", "saves_away"),
        ("fouls_home", "fouls_away"),
        ("tackles_home", "tackles_away"),
        ("interceptions_home", "interceptions_away"),
        ("shots_blocked_home", "shots_blocked_away")
    ]
    categories = ["Saves", "Fouls", "Tackles",
                  "Interceptions", "Shots_blocked"]
    home_values = []
    away_values = []

    for home_col, away_col in radar_stats:
        home_val = minute_data[home_col]
        away_val = minute_data[away_col]
        max_val = max(home_val, away_val, 1)
        home_scaled = (home_val/max_val) * 100
        away_scaled = (away_val/max_val) * 100
        home_values.append(home_scaled)
        away_values.append(away_scaled)

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
        title='Defensive Stats',
        polar=dict(
            radialaxis=dict(
                visible=True
            ), bgcolor="rgba(0,0,0,0)"

        ),
        showlegend=True
    )

    return fig


def create_event_buttons(match_events: pd.DataFrame) -> None:
    """Create buttons for all events."""
    event_data = match_events.sort_values(
        "match_minute")[["type_name", "match_minute", "player_name"]].values
    cols = st.columns(3)
    for i, (event_type, minute, player_name) in enumerate(event_data):
        with cols[i % 3]:
            button_label = f"{minute} | {event_type} | {player_name}"
            if st.button(button_label, key=f"goal_{i}"):
                st.session_state["selected_minute"] = int(minute)
                st.rerun()


def create_comparison_line_chart(timeline_df: pd.DataFrame, selected_minute: int, stat_name: str) -> go.Figure:
    """Compare one stat between home and away."""
    home_col = f"{stat_name}_home"
    away_col = f"{stat_name}_away"

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


def create_minute_by_minute_comparison(timeline_df: pd.DataFrame, selected_minute: int) -> tuple[pd.DataFrame, list]:
    """Create a minute by minute comparison."""
    current_data = timeline_df[timeline_df["match_minute"] == selected_minute]
    minute_data = current_data.iloc[0]
    key_stats = [
        ("Possession", "possession_home", "possession_away", "%"),
        ("Shots", "shots_home", "shots_away", ""),
        ("Attacks", "attacks_home", "attacks_away", ""),
        ("Corners", "corners_home", "corners_away", "")
    ]

    return minute_data, key_stats

    with st.container():
        home, _, away = st.columns([4, 1, 4])

        with home:
            st.markdown(f"### {st.session_state["home_team"]}")
            for stat_name, home_col, away_col, unit in key_stats:
                home_val = minute_data[home_col]
                st.metric(stat_name, f"{home_val:.0f}{unit}")

        with away:
            st.markdown(f"### {st.session_state["away_team"]}")
            for stat_name, home_col, away_col, unit in key_stats:
                away_val = minute_data[away_col]
                st.metric(stat_name, f"{away_val:.0f}{unit}")


def create_home_page() -> None:
    """Main function to create the home page."""
    timeline_df = create_timeline_df()

    match_events = get_event_data_for_selected_match(
        st.session_state["selected_match_id"])

    selected_minute = create_top_bar(timeline_df)

    col1, col2, col3 = st.columns([1.5, 4, 1.5])

    # Game momentum/pressure chart

    momentum_chart = process_momentum_chart_creation(
        timeline_df, selected_minute)

    st.plotly_chart(momentum_chart)

    col1, col2, col3 = st.columns(3)

    minute_data, key_stats = create_minute_by_minute_comparison(
        timeline_df, selected_minute)
    fig_attack = create_match_progression_radar_attack(
        timeline_df, selected_minute)
    fig_defence = create_match_progression_radar_defence(
        timeline_df, selected_minute)

    with col1:
        st.markdown(f"### {st.session_state["home_team"]}")
        for stat_name, home_col, _, unit in key_stats:
            home_val = minute_data[home_col]
            st.metric(stat_name, f"{home_val:.0f}{unit}")

    # Radar chart
    with col2:
        st.markdown("<h3 style='text-align: center'>Match Events</h1>",
                    unsafe_allow_html=True)
        create_event_buttons(match_events)

    # Match events/commentary
    with col3:
        col3aa, col3ab = st.columns([1, 5])
        with col3ab:
            st.markdown(f"<h3 style='text-align: right'>{st.session_state["away_team"]}</h1>",
                        unsafe_allow_html=True)
        col3a, col3b = st.columns([3, 1])
        with col3b:
            for stat_name, home_col, away_col, unit in key_stats:
                away_val = minute_data[away_col]
                st.metric(stat_name, f"{away_val:.0f}{unit}")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_attack)
    with col2:
        st.plotly_chart(fig_defence)

    stat_name = st.selectbox("Choose a Stat to Compare",
                             ["shots", "attacks", "possession", "corners", "fouls"])

    fig = create_comparison_line_chart(timeline_df, selected_minute, stat_name)

    st.plotly_chart(fig)

    st.dataframe(timeline_df)


if __name__ == "__main__":
    create_home_page()
